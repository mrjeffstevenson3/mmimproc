from __future__ import division
import nibabel, numpy, sys
from numpy import cos, sin, exp, tan, radians, power
from mmimproc.optimization import nonlinearfit
provenance = ProvenanceWrapper()
prov = lambda fpath: provenance.get(forFile=fpath).provenance

## Same equation as formulas.spgrformula but without sub function (performance)
def spgrformula(a, S0, T1):
    TR = spgrformula.TR
    expminTRT1 = exp(-TR/T1)
    return S0 * sin(a) * ((1-expminTRT1) / (1-cos(a) * expminTRT1))


def fitT1WholeBrain(sfiles, b1file, outfpath, maxval=sys.maxint):

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
    S = S_4d.reshape((len(alphas),nvoxels )).T
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
    t1vector = numpy.zeros((nvoxels,))
    t1vector[mask1d] = estimates['T1'].values
    t1vector = t1vector.clip(0, maxval)
    t1 = t1vector.reshape(spatialdims)
    nibabel.save(nibabel.Nifti1Image(t1, affine), outfpath)
