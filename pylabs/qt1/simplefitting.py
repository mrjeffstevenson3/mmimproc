from __future__ import division
import pandas
import scipy.optimize as optimize
from numpy import cos, sin, exp, tan, radians, power
from pylabs.qt1.formulas import spgrformula

def fitT1(S, A, B1, TR):
    """ Fit a series of values
    S nvalues*nflipangles
    A nflipangles in radians (possibly b1 corrected)
    B1 nvalues
    TR of the data
    """
    spgrformula.TR = TR
    T1i = 1000
    fit = pandas.Series(index=S.index.values, dtype=float)
    for v in S.index.values:
        Sv = S.loc[v].values
        S0i = 15*Sv.max()
        Ab1 = A*(B1[v]/100)
        try:
            popt, pcov = optimize.curve_fit(spgrformula, Ab1, Sv, p0=[S0i, T1i])
        except RuntimeError as e:
            continue
        fit[v] = popt[1]
    return fit
