from __future__ import division
import collections, numpy, glob, datetime, pandas, seaborn
from numpy import cos, sin, exp, tan, radians, power, square, newaxis
import matplotlib.pyplot as plt
from pylabs.optimization import nonlinearfit


## Get brain sample:
from pylabs.qt1.brainsampling import sample
from pylabs.qt1.formulas import spgrformula as f
f.TR = 11.

initial = [10000000, 1000] # So, T1
names = ('S0', 'T1')
alphas = sample.columns.values[-3:].astype(float)
A = radians(alphas)
X = (sample['B1'][:,numpy.newaxis]/100) * A[numpy.newaxis, :]
Y = sample[alphas].values

estimates = nonlinearfit(f, X, Y, initial, names)
print(estimates)


# Xl = X.repeat(1000*100, axis=0)
# 50s for 100,000 samples. Estimate that valid voxels is ~1million

