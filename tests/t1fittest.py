import os, warnings
import numpy
import nibabel
from scipy.optimize import curve_fit
from numpy import exp, cos, sin
from mmimproc.utils import progress
from datetime import datetime

def irformula(x, a, b, c):
    return numpy.abs(a * (1 - b * exp(-x/c)))

def spgrformula(x, a, b):
    TR = spgrformula.TR
    return a * ((1-exp(-TR/b))/(1-(cos(x)*exp(-TR/b)))) * sin(x)

scantype = 'SPGR'
X = numpy.array([2,10,15,20,30])
#Y = [1e+06, 1.6e+06, 1.3e+06, 975858] c 58, 160
#Y = [1e+06, 1e+06, 617572, 429000]
# T1: -11.6

img = nibabel.load('data/t1flip_all_generated.img')
Y = img.get_data()[0,0,0,:]
X = numpy.radians(X)

#B1 = 50
TR = 5.6




#Y = [(y/B1)*100 for y in Y]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    if scantype == 'IR':
        ai = Y[X.argmax()]  # S0
        bi = 2              # 'z'
        ci = 1000           # T1
        p0=[ai, bi, ci]
        formula = irformula
        poi = 2
    elif scantype == 'SPGR':
        ai = 15*Y.max()  # S0
        bi = 1000           # T1
        p0=[ai, bi]
        spgrformula.TR = TR
        formula = spgrformula
        poi = 1
    else:
        raise ValueError('Unknown scantype: '+scantype)
    popt, pcov = curve_fit(formula, X, Y, p0=p0)
print(popt[poi])


#a = popt[0]
#b = popt[1]
#x = 20
#y = a * ((1-exp(-TR/b))/(1-cos(x)*exp(-TR/b))) * sin(x)
