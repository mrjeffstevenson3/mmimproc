from pylabs.qt1.simplefitting import fitT1
from pylabs.qt1.formulas import spgrWithJ
import numpy, pandas
import scipy.optimize
from numpy import power, cos, exp
import matplotlib.pyplot as plt


def create(S, A, B1, expected, fit, TR):
    """Dummy construction/estimating of a correction method
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    expected    nvials                  model T1 per vial
    fit         nvials                  original T1 fit value
    TR          one value               e.g. 14.

    Should return data needed for apply() e.g. coefficients
    """
    vialOrder = S.index.values

    def jloss(j, a, T1, TR):
        return power(cos(a)*exp(-TR/T1), j-1)

    jmax = 1000 # 32
    J = numpy.arange(jmax)+2

    Jfit = pandas.DataFrame(index=J, columns=vialOrder, dtype=float)
    Jdiff = pandas.DataFrame(index=J, columns=vialOrder, dtype=float)
    spgrWithJ.TR = TR
    spgrWithJ.TE = 4.6
    spgrWithJ.T2s = 50
    T1i = 1000
    for j in J:
        spgrWithJ.j = j
        for v in vialOrder:
            Sv = S.loc[v].values
            S0i = 15*Sv.max()
            Ab1 = A*(B1[v]/100)
            try:
                popt, pcov = scipy.optimize.curve_fit(
                                    spgrWithJ, Ab1, Sv, p0=[S0i, T1i])
            except RuntimeError as e:
                continue
            Jfit[v].loc[j] = popt[1]
        Jdiff.loc[j] = numpy.abs(expected-Jfit.loc[j])/expected
    bestj = Jdiff.mean(axis=1).idxmin()
    name = 'jopt_j'+str(bestj)
    
    return (name,)+(TR,)+(bestj,)

def apply(correction, S, A, B1):
    """Dummy application of a correction method to data
    correction  ?                       data returned by create() function
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    """
    TR = correction[1]
    j = correction[2]

    spgrWithJ.TR = TR
    spgrWithJ.j = j
    spgrWithJ.TE = 4.6
    spgrWithJ.T2s = 50
    T1i = 1000
    corr = pandas.Series(index=S.index.values, dtype=float)
    for v in S.index.values:
        Sv = S.loc[v].values
        S0i = 15*Sv.max()
        Ab1 = A*(B1[v]/100)
        try:
            popt, pcov = scipy.optimize.curve_fit(
                                spgrWithJ, Ab1, Sv, p0=[S0i, T1i])
        except RuntimeError as e:
            continue
        corr[v] = popt[1]
    return corr
    
