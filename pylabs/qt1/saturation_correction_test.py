from __future__ import division
import collections, numpy, glob, datetime, pandas
import scipy.optimize as optimize
from numpy import cos, sin, exp, tan, radians
import matplotlib.pyplot as plt
from os.path import join, isfile
from niprov import Context
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.fitting import spgrformula
from pylabs.qt1.model_pipeline import modelForDate
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.regional import averageByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.alignment.phantom import alignAndSave
provenance = Context()

## settings
fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subject = 'sub-phant2016-03-02'
subjectdir = join(projectdir, subject)
anatdir = join(projectdir, subject, 'anat')
alignmentTarget = join(projectdir, 'phantom_flipangle_alignment_target.nii')
vialAtlas = join(projectdir,'phantom_slu_mask_20160113.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]

## model_pipeline
targetdate = datetime.date(2016, 3, 2)
expected = modelForDate(targetdate, 'slu')[vialOrder]

## par2nii
#niftiDict = convertSubjectParfiles(subject, subjectdir)

## align and sample flip-angle files
data = pandas.DataFrame()
alphafiles = sorted(glob.glob(join(anatdir,'*14*1.nii')))
for alphafile in alphafiles:
    alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
    if not isfile(alignedAlphafile):
        alignAndSave(alphafile, alignmentTarget, newfile=alignedAlphafile, 
            provenance=provenance)
    vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
    alpha = provenance.get(forFile=alignedAlphafile).provenance['flip-angle']
    data[alpha] = vialAverages
data = data.loc[vialOrder]

### fitting
def spgrformula(a, S0, T1):
    TR = spgrformula.TR
    return S0 * ((1-exp(-TR/T1))/(1-cos(a)*exp(-TR/T1))) * sin(a)
TR = provenance.get(forFile=alphafile).provenance['repetition-time']
spgrformula.TR = TR
A = radians(data.columns.values)
T1i = 1000
fit = pandas.Series()
for v in vialOrder:
    Sa = data.loc[v].values
    S0i = 15*Sa.max()
    popt, pcov = optimize.curve_fit(spgrformula, A, Sa, p0=[S0i, T1i])
    fit[v] = popt[1]

## Calculate theoretical signal loss
def fracsat(a, TR, T1):
    return ((1-cos(a))*exp(-TR/T1))/(1-(cos(a)*exp(-TR/T1)))
sloss = pandas.DataFrame(index=vialOrder, columns=data.columns)
for v in vialOrder:
    sloss.loc[v] = fracsat(A, TR, expected.loc[v])

## plotting
plt.figure()
pandas.DataFrame({'expected': expected, 'observed':fit}).plot.bar()
plt.savefig('exp_vs_obs_TR{}.png'.format(TR))
plt.figure()
((fit-expected)/expected).plot.line()
plt.savefig('T1_difference_TR{}.png'.format(TR))
plt.figure()
sloss.transpose().plot.line() ## (loglog=True) This is Tofts fig 4.9
plt.savefig('fracsat_tofts_TR{}.png'.format(TR))

### plot
#Xrange = numpy.radians(numpy.arange(200))
#fit = [formula(x, *popt) for x in Xrange]
#sat = numpy.array([frac_sat(x, TR, fit[i]) for i,x in enumerate(Xrange)])
#plt.plot(Xrange, fit) 
#plt.plot(X, Y, 'bo')
#plt.plot(Xrange, sat*10000) 
#plt.show()


### Calculate new signal based on model T1
#corrdata = pandas.DataFrame(index=vialOrder, columns=data.columns)
#S0fit = popt[0]
#for v in vialOrder:
#    corrdata.loc[v] = spgrformula(A, S0, expected.loc[v])










