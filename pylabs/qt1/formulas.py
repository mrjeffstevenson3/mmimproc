from __future__ import division
from numpy import cos, sin, exp, tan, radians, power

def approachSS(j, a, TR, T1, TE, T2s=50, M0=1.):
    return M0 * sin(a) * sub2(a, TR, T1, j) * exp(-TE/T2s)
    
def sub(a, TR, T1):
    return (1-exp(-TR/T1)) / (1-cos(a)*exp(-TR/T1))

def sub2(a, TR, T1, j):
    return (sub(a, TR, T1) + power(cos(a)*exp(-TR/T1), j-1) * (1-sub(a, TR, T1)))
