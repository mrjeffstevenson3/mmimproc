from __future__ import division
import collections, numpy, glob, datetime
from numpy import cos, sin, exp, tan
import matplotlib.pyplot as plt
from os.path import join
from scipy.optimize import curve_fit
from niprov import Context
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import spgrformula
from pylabs.qt1.model_pipeline import calculate_model
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.alignment.phantom import alignAndSave
provenance = Context()

def frac_sat(a, TR, T1):
    return round(((1-cos(a))*exp(-TR/T1))/(1-(cos(a)*exp(-TR/T1))), 5)

## model_pipeline
targetdate = datetime.date(2016, 3, 2)
expected = calculate_model('slu')[targetdate]

## data
fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subject = 'sub-phant2016-03-02'
anatdir = join(projectdir, subject, 'anat')
anglefiles = sorted(glob.glob(join(anatdir,'*14*1.nii')))
X = numpy.radians([7,10,15,20,30])

### coregistration
ref = join(projectdir, 'phantom_alignment_target.nii.gz')
aligned = [alignAndSave(f, ref, provenance=provenance) for f in anglefiles]

## atlassing
atlasfname = 'phantom_slu_mask_20160113.nii.gz'
atlasfpath = join(projectdir,atlasfname)
labels = atlaslabels(atlasfname)
indexOf15 = labels.index('15')

YRegionalData = []
for fpath in anglefiles:
    YRegionalData.append(samplevials(fpath))

Y = [stats['average'][indexOf15] for stats in YRegionalData]

Y = numpy.array(Y)


## minimize signal loss formula 
## fit once, get estimated S0
## from this we can adjust S0 and and fit.
## plot signal loss vs vial
## fit curve to signall loss vs T1

### fitting
#TR = 14.0
##ai = 15*Y.max()  # S0
#ai = Y.max()/sin(X[1])
#bi = 1000           # T1
#p0=[ai, bi]
#spgrformula.TR = TR
#formula = spgrformula

#popt, pcov = curve_fit(formula, X, Y, p0=p0)
#T1 = popt[1]

#y = Y/sin(X)
#m = exp(-TR/T1)
#x = Y/tan(X)
#b = S0*(1-m)
#y = mx+b



### sat
#for x, y in zip(X,Y):
#    fsat = frac_sat(x, TR, T1)
#    print((x, y, fsat))

### plot
#Xrange = numpy.radians(numpy.arange(200))
#fit = [formula(x, *popt) for x in Xrange]
#sat = numpy.array([frac_sat(x, TR, fit[i]) for i,x in enumerate(Xrange)])
#plt.plot(Xrange, fit) 
#plt.plot(X, Y, 'bo')
#plt.plot(Xrange, sat*10000) 
#plt.show()

##def func(x):
##    return (x - 2) * (x + 2)**2

##def func2(x):
##    return (x - 2) * x * (x + 2)**2

##min = 0
##max = 1

##res1 = optimize.fminbound(func, min, max)
##res2 = optimize.minimize_scalar(func, bounds=(min,max))
##res3 = optimize.fminbound(func2, min, max)
##res4 = optimize.minimize_scalar(func2, bounds=(min,max))

##print res1, res2.x
##print res3, res4.x

##import matplotlib.pyplot as plt
##import numpy as np

##xaxis = np.arange(-15,15)

##plt.plot(xaxis, func(xaxis))
##plt.plot(xaxis, func2(xaxis))
##plt.scatter(res2.x, res2.fun)
##plt.scatter(res4.x, res4.fun)
##plt.show()








