from __future__ import division
import numpy, nibabel, scipy.stats, math, datetime
from numpy import square, sqrt
from pylabs.utils import progress


def correlateWholeBrain(files, variables):
    assert len(files) == variables.shape[0] # ensure equally many subjects
    n = nsubjects = variables.shape[0]
    nvars = variables.shape[1]
    data = []
    shapes = []
    for f, fpath in enumerate(files):
        print('Loading image {} of {}..'.format(f+1, len(files)))
        img = nibabel.load(fpath)
        sdata = img.get_data()
        shapes.append(sdata.shape)
        data.append(sdata)
    print('Concatenating data..')
    data = numpy.array(data)
    affine = img.get_affine()
    for shape in shapes:
        assert shape==shapes[0] # ensure images have same dimensions
    print('Vectorizing and masking..')
    spatialdims = data.shape[1:]
    nvoxels = numpy.prod(spatialdims)
    data2d = data.reshape((nsubjects, nvoxels))
    mask1d = (data2d>0).all(axis=0)
    mdata2d = data2d[:, mask1d]
    nvalid = mask1d.sum()
    print('{0:.1f}% of voxels in mask.'.format(nvalid/nvoxels*100))

    X = mdata2d[:, numpy.newaxis, :]
    Y = variables.values[:, :, numpy.newaxis]
    r, t = corr(X, Y)
    p = scipy.stats.t.sf(t, n-2) * 2                #997ms

    nvoxelsScalar = 4
    scalarResults = numpy.zeros((nvars, nvoxelsScalar))
    for v, varname in enumerate(variables.columns.values):
        for k in range(nvoxelsScalar):
            x = mdata2d[:, k]
            y = variables[varname]
            scalarResults[v, k] = scipy.stats.pearsonr(x,y)[0]
    assert numpy.allclose(r[:,:4], scalarResults)

    print('Starting FDR permutations..')
    niterations = 1000
    npermutations = math.factorial(n)
    assert niterations < npermutations
    nbins = 1000
    tmax = 20.
    tres = tmax/nbins
    binedges = numpy.arange(0, tmax-tres, tres)
    tdist = numpy.zeros(binedges.size-1, dtype=int)
    start = datetime.datetime.now()
    for j in range(niterations):
        progress.progressbar(j, niterations, start)
        I = numpy.random.permutation(numpy.arange(nsubjects))
        Y = variables.values[:, :, numpy.newaxis]
        _, tp = corr(X, Y)
        tdist += numpy.histogram(numpy.abs(tp), binedges)[0]
    alpha = .05
    q = .05
    cumtdist = numpy.cumsum(tdist[::-1])/tdist.sum()
    closestbin = numpy.abs(cumtdist-(q*alpha)).argmin()
    tcorr = binedges[::-1][closestbin]
    pcorr = scipy.stats.t.sf(tcorr, n-2)
    assert pcorr < alpha
    print('\nCorrected p-value: {}'.format(pcorr))

    output2d = numpy.zeros((nvars, nvoxels))
    output2d[:, mask1d] = p
   
    print('Unvectorizing and saving to file..')
    output4d = output2d.reshape((nvars,) + spatialdims)
    for v, varname in enumerate(variables.columns.values):
        img = nibabel.Nifti1Image(output4d[v,:,:,:], affine)
        nibabel.save(img, 'corr_{}.nii.gz'.format(varname))

def corr(X, Y):
    n = Y.shape[0]
    mx = X.mean(axis=0, keepdims=True)
    my = Y.mean(axis=0, keepdims=True)
    xm, ym = X-mx, Y-my                             #48ms
    r_num = (xm * ym).mean(axis=0)                  #167ms
    r_den = X.std(axis=0) * Y.std(axis=0)           #108ms
    r = r_num / r_den
    t = r * sqrt( (n - 2) / (1 - square(r)) )       #19ms
    return r, t





