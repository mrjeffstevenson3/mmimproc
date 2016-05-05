from __future__ import division
import numpy, pandas, seaborn
from numpy import radians, square, newaxis


def nonlinearfit(f, X, Y, initial, names):
    """ grid-search least-squares estimation of a non-linear curve.
    """
    assert len(initial) == len(names)
    assert X.shape[0] == Y.shape[0]
    
    print('[nonlinearfit] Initializing..')

    X = X[:, :, numpy.newaxis]
    Y = Y[:, :, numpy.newaxis]
    nsamples = X.shape[0]
    nparams = len(initial)
    estimates = numpy.tile(initial, (nsamples,1))
    nbins = 10
    width = 1.5
    niterations = 3
    zoomfactor = .11

    for j in range(niterations):

        res = (2*width)/nbins
        msg = '[nonlinearfit] Zoom {} of {}, resolution {}'
        print(msg.format(j+1, niterations, res))
        relprange = numpy.arange(1-width, 1+width, res) # nbins
        pgrids = numpy.meshgrid(*([relprange]*nparams)) # nparams x nbins x nbins 
        relativeP = numpy.array([pgrid.ravel() for pgrid in pgrids]) # nparams x ncombs
        P = estimates[:,:,newaxis]*relativeP[newaxis,:,:] # nsamples x nparams x ncombs
        Plist = [P[:,p,:][:,newaxis,:] for p in range(nparams)]
 
        Ye = f(X, *Plist)

        ss = square(Y-Ye).sum(axis=1)
        minss = ss.min(axis=1)
        bestpraveled = ss.argmin(axis=1)
        oldestimates = estimates
        estimates = relativeP[:,bestpraveled].T*oldestimates
        width = width * zoomfactor

    return pandas.DataFrame(estimates, columns=names)


#for s in range(nsamples):
#    ssdf = pandas.DataFrame(ss[s,:].reshape((nbins,)*nparams), 
#            index = relprange*oldestimates[s,0], 
#            columns = relprange*oldestimates[s,1])
#    plt.figure()
#    seaborn.heatmap(ssdf)
#    plt.savefig('sample_{}.png'.format(s))
