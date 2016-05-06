from __future__ import division
import nibabel, numpy, niprov
from pylabs.optimization import nonlinearfit
from pylabs.qt1.formulas import spgrformula
provenance = niprov.Context()
prov = lambda fpath: provenance.get(forFile=fpath).provenance


def fitT1WholeBrain(sfiles, b1file, outfpath):

    TR = prov(sfiles[0])['repetition-time']
    if hasattr(TR, '__iter__'):
        TR = TR[0]
    alphas = [prov(sfile)['flip-angle'] for sfile in sfiles]

    spgrformula.TR = TR
    initial = [10000000, 1500]
    names = ('S0', 'T1')
    A = numpy.radians(alphas)

    print('Loading data..')
    S_4d = numpy.array([nibabel.load(f).get_data() for f in sfiles]) # all data
    B1_3d = nibabel.load(b1file).get_data() # B1 data
    affine = nibabel.load(sfiles[0]).get_affine()
    assert B1_3d.shape == S_4d.shape[1:]  # make sure they have same dimensions

    print('Vectorizing and masking..')
    spatialdims = S_4d.shape[1:]
    nvoxels = numpy.prod(spatialdims)
    S = S_4d.reshape((nvoxels, len(alphas)))
    B1 = B1_3d.reshape((nvoxels,))
    mask1d = (S>0).all(axis=1)
    Smasked = S[mask1d,:]
    B1masked = B1[mask1d]
    nvalid = mask1d.sum()
    print('{0:.1f}% of voxels in mask.'.format(nvalid/nvoxels*100))

    X = (B1masked[:,numpy.newaxis]/100) * A[numpy.newaxis, :]
    Y = Smasked
    estimates = nonlinearfit(spgrformula, X, Y, initial, names)

    print('Saving file..')
    t1 = estimates['T1'].values.reshape(spatialdims)
    nibabel.save(nibabel.Nifti1Image(t1, affine), outfpath)
