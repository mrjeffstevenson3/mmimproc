from __future__ import division
import collections, numpy, glob, datetime, pandas, itertools
import scipy.optimize as optimize
from numpy import cos, sin, exp, tan, radians, power
import matplotlib.pyplot as plt
from os.path import join, isfile
from niprov import Context
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.fitting import spgrformula
from pylabs.qt1.model_pipeline import modelForDate
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.qt1.formulas import sratio
from pylabs.regional import averageByRegion
from pylabs.alignment.phantom import align, applyXformAndSave
from pylabs.stats import ScaledPolyfit
provenance = Context()

## settings
fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subjectsByTR = {14.0:datetime.date(2016, 3, 2),
                28.0:datetime.date(2016, 3, 2), 
                56.0:datetime.date(2016, 3, 11)}
alignmentTarget = join(projectdir, 'phantom_flipangle_alignment_target.nii')
vialAtlas = join(projectdir,'phantom_alignment_target_round_mask.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]

TRs = subjectsByTR.keys()
adata = {}
J = {}
Jfit = {}
Jdiff = {}
overview = {}
xform = {}
xform = {14.0: {'rxy': 0, 'tx': 0, 'ty': 0}, 28.0: {'rxy': -3, 'tx': 1, 'ty': 0}}
expected = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
fit = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
diff = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
fit2 = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
srat = {}
curves = {}
for TR in TRs:
    if TR ==56:
        continue
    date = subjectsByTR[TR]
    subject = 'sub-phant'+str(date)
    subjectdir = join(projectdir, subject)

    ## model_pipeline
    expected[TR] = modelForDate(date, 'slu')[vialOrder]

    ## Gather files & align
    alphafilter = '*{}*1.nii'.format(int(TR))
    alphafiles = sorted(glob.glob(join(subjectdir,'anat',alphafilter)))
    assert TR == provenance.get(forFile=alphafiles[0]).provenance['repetition-time']
    if not xform:
        xform[TR] = align(alphafiles[0], alignmentTarget, delta=10)

    ## b1 map
    b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))
    alignedB1file = b1file.replace('.nii', '_coreg.nii')
    applyXformAndSave(xform[TR], b1file, alignmentTarget, 
        newfile=alignedB1file, provenance=provenance)
    B1 = averageByRegion(alignedB1file, vialAtlas).loc[vialOrder]

    ## transform and sample flip-angle files
    adata[TR] = pandas.DataFrame()
    for alphafile in alphafiles:
        alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
        applyXformAndSave(xform[TR], alphafile, alignmentTarget, 
            newfile=alignedAlphafile, provenance=provenance)
        vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
        alpha = provenance.get(forFile=alignedAlphafile).provenance['flip-angle']
        adata[TR][alpha] = vialAverages
    adata[TR] = adata[TR].loc[vialOrder]
    alphas = adata[TR].columns.values.tolist()

    ### fitting
    def spgrformula(a, S0, T1):
        TR = spgrformula.TR
        return S0 * ((1-exp(-TR/T1))/(1-cos(a)*exp(-TR/T1))) * sin(a)
    spgrformula.TR = TR
    A = radians(alphas)
    T1i = 1000
    for v in vialOrder:
        Sa = adata[TR].loc[v].values
        S0i = 15*Sa.max()
        Ab1 = A*(B1[v]/100)
        popt, pcov = optimize.curve_fit(spgrformula, Ab1, Sa, p0=[S0i, T1i])
        fit[TR][v] = popt[1]

    ## Observed T1 difference
    diff[TR] = (fit[TR]-expected[TR])/expected[TR]

    ### fitting 2
    def spgrformula(a, S0, T1):
        TR = spgrformula.TR
        return S0 * ((1-exp(-TR/T1))/(1-cos(a)*exp(-TR/T1))) * sin(a)
    spgrformula.TR = TR
    A = radians(alphas)
    T1i = 1000
    srat[TR] = pandas.DataFrame(index=alphas, columns=vialOrder, dtype=float)
    for v in vialOrder:
        Ab1 = A*(B1[v]/100)
        srat[TR][v] = sratio(Ab1, TR, fit[TR][v], expected[TR][v])
        SaUncor = adata[TR].loc[v].values
        Sa = SaUncor * srat[TR][v]
        S0i = 15*Sa.max()
        popt, pcov = optimize.curve_fit(spgrformula, Ab1, Sa, p0=[S0i, T1i])
        fit2[TR][v] = popt[1]

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm


X = expected[TR].values
Y = srat[TR].T.columns.values
X, Y = numpy.meshgrid(X, Y)
Z = srat[TR].values

fig2 = plt.figure()
az = fig2.gca(projection='3d')
az.plot_surface(X, Y, Z, rstride=8, cstride=8, alpha=0.3, cmap=cm.coolwarm)
#cset = az.contour(X, Y, Z, zdir='z', offset=numpy.min(Z)-1, cmap=cm.coolwarm)
cset = az.contour(X, Y, Z, zdir='x', offset=numpy.min(X)-1, cmap=cm.coolwarm)
cset = az.contour(X, Y, Z, zdir='y', offset=numpy.max(Y)+0.05, cmap=cm.coolwarm)
az.set_xlabel('GM <-- T1 --> WM')
az.set_xlim(numpy.min(X)-1, numpy.max(X)+1)
az.set_ylabel('Flip Angle')
az.set_ylim(numpy.min(Y)-1, numpy.max(Y)+1)
az.set_zlabel('Signal Ratio')
az.set_zlim(numpy.min(Z)-0.1, numpy.max(Z)+0.1)
az.set_title('Signal Ratio as Function of T1 and Flip Angle',fontsize=15)
plt.show()




