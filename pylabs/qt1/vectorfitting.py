from pylabs.optimization import nonlinearfit
from pylabs.qt1.formulas import spgrformula as f


def fitT1WholeBrain(alphafiles, b1file):

    f.TR = 11.
    initial = [10000000, 1500] # So, T1
    names = ('S0', 'T1')
    A = radians(alphas)


    print('Loading data..')
    S = numpy.array([nibabel.load(f).get_data() for f in alphafiles]) # all data
    B1 = nibabel.load(b1file).get_data() # B1 data
    assert B1.shape == S.shape[1:]  # make sure they have same dimensions

    print('Vectorizing and masking..')
    spatialdims = data.shape[1:]
    nvoxels = numpy.prod(spatialdims)
    data2d = data.reshape((nvoxels, nangles))
    mask1d = (data2d>0).all(axis=0)
    mdata2d = data2d[:, mask1d]
    nvalid = mask1d.sum()
    print('{0:.1f}% of voxels in mask.'.format(nvalid/nvoxels*100))


    X = (sample['B1'][:,numpy.newaxis]/100) * A[numpy.newaxis, :]
    Y = sample[alphas].values
    estimates = nonlinearfit(f, X, Y, initial, names)
