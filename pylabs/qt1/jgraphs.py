from __future__ import division
import numpy, pandas
from numpy import cos, sin, exp, tan, radians, power
import matplotlib.pyplot as plt
from pylabs.qt1.formulas import jloss



a = 7.0
T1s = numpy.arange(0, 2000, 200)
J = numpy.arange(20)+1
jlosses = numpy.zeros((J.size, T1s.size))
for i, j in enumerate(J):
    jlosses[i,:] = jloss(j, a, T1s, TR)

