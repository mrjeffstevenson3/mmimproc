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
from pylabs.qt1.formulas import approachSS
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
sloss = {}
corr = {}
xform = {}
xform = {14.0: {'rxy': 0, 'tx': 0, 'ty': 0}, 28.0: {'rxy': -3, 'tx': 1, 'ty': 0}}
expected = pandas.DataFrame(columns=TRs, index=vialOrder)
fit = pandas.DataFrame(columns=TRs, index=vialOrder)
diff = pandas.DataFrame(columns=TRs, index=vialOrder)
corrfit = pandas.DataFrame(columns=TRs, index=vialOrder)
curves = {}
for TR in TRs:
    if TR ==56:
        continue
    date = subjectsByTR[TR]
    subject = 'sub-phant'+str(date)
    subjectdir = join(projectdir, subject)

    ## par2nii
    #niftiDict = convertSubjectParfiles(subject, subjectdir)

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

    ## Signal loss
    sloss[TR] = pandas.DataFrame(index=vialOrder, columns=adata[TR].columns, dtype=float)
    corr[TR] = pandas.DataFrame(index=vialOrder, columns=['cfit','d'], dtype=object)
    def fracsat(a, TR, T1):
        return ((1-cos(a))*exp(-TR/T1))/(1-(cos(a)*exp(-TR/T1)))
    for v in vialOrder:
        t1 = expected[TR][v]
        sloss[TR].loc[v] = fracsat(A, TR, t1)
        SaUncor = adata[TR].loc[v].values
        Sa = SaUncor / (1-sloss[TR].loc[v]*cos(A))
        S0i = 15*Sa.max()
        Ab1 = A*(B1[v]/100)
        try:
            popt, pcov = optimize.curve_fit(spgrformula, Ab1, Sa, p0=[S0i, T1i])
        except RuntimeError as exc:
            pass
        corr[TR]['cfit'][v] = popt[1]
        corr[TR]['d'][v] = (popt[1]-t1)/t1

    ## Fit correction curve
    curves[TR] = ScaledPolyfit(expected[TR], diff[TR], 2)

    ## plotting
    plt.figure()
    pandas.DataFrame({'expected': expected[TR], 'observed':fit[TR]}).plot.bar()
    plt.savefig('exp_vs_obs_TR{}.png'.format(TR))
    plt.figure()
    diff[TR].plot.line()
    plt.savefig('T1_difference_TR{}.png'.format(TR))
    plt.figure()
    curves[TR].plot()
    plt.savefig('corr_curve_TR{}.png'.format(TR))

D = pandas.Panel(adata)

