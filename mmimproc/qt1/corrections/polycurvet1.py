from mmimproc.qt1.simplefitting import fitT1
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
    ncoeff = 3
    P = numpy.polyfit(fit, diff, ncoeff)
    fP = numpy.poly1d(P)

    ## plot
    xspace = numpy.linspace(fit.min()-100, fit.max()+100, 200)
    plt.figure()
    name = 'polycurvet1_p{}_TR{}'.format(ncoeff, TR)
    plt.plot(fit, diff, 'bo', xspace, fP(xspace))
    plt.title(name)
    plt.savefig(name+'.png')
    
    return (name,)+(TR,)+tuple(P)

def apply(correction, S, A, B1):
    """Dummy application of a correction method to data
    correction  ?                       data returned by create() function
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    """
    TR = correction[1]
    P = correction[2:]
    fit = fitT1(S, A, B1, TR)
    fP = numpy.poly1d(P)
    diff = fP(fit)
    corr = fit+diff
    return corr
    
