import collections
from os.path import join
import numpy
from pylabs.utils.paths import getlocaldataroot
import glob
from pylabs.qt1.fitting import spgrformula
from pylabs.qt1.coregister_phantoms import coregisterPhantoms
from scipy.optimize import curve_fit
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
import numpy as np
from numpy import cos, sin, exp

def frac_sat(a, TR, T1):
    return round(((1-cos(np.radians(a)))*exp(-TR/T1))/(1-(cos(np.radians(a))*exp(-TR/T1))), 5)

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subject = 'sub-phant2016-03-02'
anatdir = join(projectdir, subject, 'anat')

anglefiles = sorted(glob.glob(join(anatdir,'*14*1.nii')))
X = [7,10,15,20,30]

### coregistration
#coregAngleFiles = coregisterPhantoms(anglefiles, projectdir=projectdir)


## atlassing
atlasfname = 'phantom_slu_mask_20160113.nii.gz'
atlasfpath = join(projectdir,atlasfname)
labels = atlaslabels(atlasfname)
indexOf15 = labels.index('15')

YRegionalData = []
for fpath in anglefiles:
    YRegionalData.append(statsByRegion(fpath, atlasfpath))

Y = [stats['average'][indexOf15] for stats in YRegionalData]

X = numpy.radians(X)
Y = numpy.array(Y)


## fitting
TR = 14.0
ai = 15*Y.max()  # S0
bi = 1000           # T1
p0=[ai, bi]
spgrformula.TR = TR
formula = spgrformula

popt, pcov = curve_fit(formula, X, Y, p0=p0)

fsat = frac_sat(popt[0], TR, popt[1])







