from __future__ import division
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
from numpy import cos, sin, exp, tan
import matplotlib.pyplot as plt

def frac_sat(a, TR, T1):
    return round(((1-cos(a))*exp(-TR/T1))/(1-(cos(a)*exp(-TR/T1))), 5)




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
#ai = 15*Y.max()  # S0
ai = Y.max()/sin(X[1])
bi = 1000           # T1
p0=[ai, bi]
spgrformula.TR = TR
formula = spgrformula

popt, pcov = curve_fit(formula, X, Y, p0=p0)
T1 = popt[1]

y = Y/sin(X)
m = exp(-TR/T1)
x = Y/tan(X)
b = S0*(1-m)
y = mx+b



## sat
for x, y in zip(X,Y):
    fsat = frac_sat(x, TR, T1)
    print((x, y, fsat))

## plot
Xrange = numpy.radians(numpy.arange(200))
fit = [formula(x, *popt) for x in Xrange]
sat = numpy.array([frac_sat(x, TR, fit[i]) for i,x in enumerate(Xrange)])
plt.plot(Xrange, fit) 
plt.plot(X, Y, 'bo')
plt.plot(Xrange, sat*10000) 
plt.show()

#def func(x):
#    return (x - 2) * (x + 2)**2

#def func2(x):
#    return (x - 2) * x * (x + 2)**2

#min = 0
#max = 1

#res1 = optimize.fminbound(func, min, max)
#res2 = optimize.minimize_scalar(func, bounds=(min,max))
#res3 = optimize.fminbound(func2, min, max)
#res4 = optimize.minimize_scalar(func2, bounds=(min,max))

#print res1, res2.x
#print res3, res4.x

#import matplotlib.pyplot as plt
#import numpy as np

#xaxis = np.arange(-15,15)

#plt.plot(xaxis, func(xaxis))
#plt.plot(xaxis, func2(xaxis))
#plt.scatter(res2.x, res2.fun)
#plt.scatter(res4.x, res4.fun)
#plt.show()








