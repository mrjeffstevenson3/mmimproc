from __future__ import division
import numpy, pandas, seaborn
from numpy import radians, square, newaxis


def nonlinearfit(f, X, Y, initial):
    """ grid-search least-squares estimation of a non-linear curve.
    """

    X = X[:, :, numpy.newaxis]
    Y = Y[:, :, numpy.newaxis]

    assert X.shape[0] == Y.shape[0]
    nsamples = X.shape[0]

    nparams = initial.size
    estimates = numpy.tile(initial, (nsamples,1))
    nbins = 100
    width = 1.5
    niterations = 10
    zoomfactor = .5

    for j in range(niterations):
        
        res = (2*width)/nbins
        relprange = numpy.arange(1-width, 1+width, res) # nbins
        pgrids = numpy.meshgrid(*([relprange]*nparams)) # nparams x nbins x nbins 
        relativeP = numpy.array([pgrid.ravel() for pgrid in pgrids]) # nparams x ncombs
        P = estimates[:,:,newaxis]*relativeP[newaxis,:,:] # nsamples x nparams x ncombs

        Ye = f(X, P[:,0,:][:,newaxis,:], P[:,1,:][:,newaxis,:])

        ss = square(Y-Ye).sum(axis=1)
        minss = ss.min(axis=1)
        bestpraveled = ss.argmin(axis=1)
        oldestimates = estimates
        estimates = relativeP[:,bestpraveled].T*oldestimates
        width = width * zoomfactor

    return estimates


#for s in range(nsamples):
#    ssdf = pandas.DataFrame(ss[s,:].reshape((nbins,)*nparams), 
#            index = relprange*oldestimates[s,0], 
#            columns = relprange*oldestimates[s,1])
#    plt.figure()
#    seaborn.heatmap(ssdf)
#    plt.savefig('sample_{}.png'.format(s))
