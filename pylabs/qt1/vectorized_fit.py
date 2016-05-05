from __future__ import division
import collections, numpy, glob, datetime, pandas
from numpy import cos, sin, exp, tan, radians, power, square, newaxis
import matplotlib.pyplot as plt


## Get brain sample:
from pylabs.qt1.brainsampling import sample
def spgrformula(a, S0, T1):
    TR = spgrformula.TR
    return S0 * sin(a) * (1-exp(-TR/T1)) / (1-cos(a)*exp(-TR/T1))
spgrformula.TR = 11.


initial = numpy.array([10000000, 1000]) # So, T1
A = sample.columns.values[-3:].astype(float)
Ab1 = (sample['B1'][:,numpy.newaxis]/100) * A[numpy.newaxis, :]
S = sample[A].values


X = Ab1[:, :, numpy.newaxis]
Y = S[:, :, numpy.newaxis]

assert X.shape[0] == Y.shape[0]
nsamples = X.shape[0]

nparams = initial.size
estimates = numpy.tile(initial, (nsamples,1))
nbins = 10
width = .7
niterations = 1

for j in range(niterations):
    
    res = (2*width)/nbins

    relprange = numpy.arange(1-width, 1+width, res) # nbins
    pgrids = numpy.meshgrid(*([relprange]*nparams)) # nparams x nbins x nbins 
    #pgrids[0].clip(min=.8, max=1.8)
    relativeP = numpy.array([pgrid.ravel() for pgrid in pgrids]) # nparams x ncombs
    P = estimates[:,:,newaxis]*relativeP[newaxis,:,:] # nsamples x nparams x ncombs

    P = P.clip(min=0)

    Ye = spgrformula(X, P[:,0,:][:,newaxis,:], P[:,1,:][:,newaxis,:])
    ss = square(Y-Ye).sum(axis=1)

    minss = ss.min(axis=1)
    bestpraveled = ss.argmin(axis=1)
    oldestimates = estimates
    estimates = relativeP[:,bestpraveled][::-1].T*oldestimates ## ???
    estimates = estimates.clip(min=0)
    width = width*.9


print(estimates[:,0])
print(estimates[:,1])


ssdf = pandas.DataFrame(ss[5,:].reshape((nbins,)*nparams), 
        index = relprange*oldestimates[5,0], 
        columns = relprange*oldestimates[5,1])







