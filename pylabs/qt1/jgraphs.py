from __future__ import division
import numpy, pandas, seaborn
from numpy import cos, sin, exp, tan, radians, power
import matplotlib.pyplot as plt
from pylabs.qt1.formulas import jloss


TR = 14.
a = radians(30.0)
T1s = pandas.Series(numpy.arange(50, 2000, 100))
J = pandas.Series(numpy.arange(1,40,2))
jlosses = pandas.DataFrame(index=J, columns=T1s)
for t1 in T1s:
    jlosses[t1] = jloss(J.values, a, t1, TR)

seaborn.heatmap(jlosses)


print(jlosses[jlosses < .02].idxmax())





