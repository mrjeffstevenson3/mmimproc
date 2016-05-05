from __future__ import division
import collections, numpy, glob, datetime, pandas, seaborn
from numpy import cos, sin, exp, tan, radians, power, square, newaxis
import matplotlib.pyplot as plt
from pylabs.optimization import nonlinearfit


## Get brain sample:
from pylabs.qt1.brainsampling import sample
def spgrformula(a, S0, T1):
    TR = spgrformula.TR
    return S0 * sin(a) * (1-exp(-TR/T1)) / (1-cos(a)*exp(-TR/T1))
spgrformula.TR = 11.


initial = numpy.array([10000000, 1000]) # So, T1
alphas = sample.columns.values[-3:].astype(float)
A = radians(alphas)
Ab1 = (sample['B1'][:,numpy.newaxis]/100) * A[numpy.newaxis, :]
S = sample[alphas].values

estimates = nonlinearfit(spgrformula, Ab1, S, initial)
print(estimates[:,0])
print(estimates[:,1])









