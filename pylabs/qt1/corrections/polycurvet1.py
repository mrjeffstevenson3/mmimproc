from pylabs.qt1.simplefitting import fitT1
import numpy
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
    diff = expected-fit
    P = numpy.polyfit(fit, diff, 3)
    fP = numpy.poly1d(P)

    xspace = numpy.linspace(fit.min()-100, fit.max()+100, 200)

    plt.figure()
    pltname = 'polycurvet1_TR{}'.format(TR)
    plt.plot(fit, diff, 'bo', xspace, fP(xspace))
    plt.title(pltname)
    plt.savefig(pltname+'.png')
    
    return tuple(P)+(TR,)

def apply(correction, S, A, B1):
    """Dummy application of a correction method to data
    correction  ?                       data returned by create() function
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    """
    TR = correction[-1]
    P = correction[:-1]
    fit = fitT1(S, A, B1, TR)
    fP = numpy.poly1d(P)
    diff = fP(fit)
    corr = fit+diff
    return corr
    
