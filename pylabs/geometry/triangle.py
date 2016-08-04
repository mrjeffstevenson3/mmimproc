from __future__ import division # division always floating point
import numpy
from numpy import mean, sqrt, square


def triangleHeight(b, a, c):
    # base is b
    allSides = [a,b,c]
    if 0 in allSides:
        return 0.0
    longestSide = max(allSides)
    if longestSide > (sum(allSides)-longestSide):
        # Not a valid triangle, assume rounding error
        return 0.0
    s = (a+b+c)/2 # semiperimeter 
    area = sqrt(s*(s-a)*(s-b)*(s-c)) # Heron's
    h = area/(b/2)
    return h
