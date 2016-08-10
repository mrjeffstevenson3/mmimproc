from __future__ import division
from numpy import cos, sin, exp, tan, radians, power

def spgrformula(a, S0, T1):
    TR = spgrformula.TR
    return S0 * sin(a) * sub(a, TR, T1) 

def approachSS(j, a, TR, T1, TE, T2s=50, M0=1.):
    return M0 * sin(a) * sub2(a, TR, T1, j) * exp(-TE/T2s)
    
def sub(a, TR, T1):
    return (1-exp(-TR/T1)) / (1-cos(a)*exp(-TR/T1))

def sub2(a, TR, T1, j):
    return sub(a, TR, T1) + jloss(j, a, T1, TR)

def jloss(j, a, T1, TR):
    return power(cos(a)*exp(-TR/T1), j-1) * (1-sub(a, TR, T1))

def spgrWithJ(a, S0, T1):
    TR = spgrWithJ.TR
    j = spgrWithJ.j
    TE = spgrWithJ.TE
    T2s = spgrWithJ.T2s
    return S0 * sin(a) * (sub(a, TR, T1) + jloss(j, a, T1, TR))

def sratio(a, TR, T1o, T1m):
    return ((1-exp(-TR/T1m)) * (1-cos(a) * exp(-TR/T1o))) / ((1-cos(a) * exp(-TR/T1m)) * (1-exp(-TR/T1o)))

#def spgrformula(a, S0, T1):
#    TR = spgrformula.TR
#    return S0 * ((1-exp(-TR/T1))/(1-cos(a)*exp(-TR/T1))) * sin(a)
#jdiff = jloss(j, a, T1, TR) - jloss(40, a, T1, TR)
