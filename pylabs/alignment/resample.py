from dipy.align.reslice import reslice
import numpy as np


def reslice_roi(in_data, in_affine, in_zooms, out_affine, out_zooms):
    """ Resample roi to matching volume
        Uses dipy.align.reslice
    """

    out_data, new_affine = reslice(in_data, in_affine, in_zooms, out_zooms)

    assert np.allclose(out_affine, new_affine, 4), 'out affine and new affine do not match.'

    return out_data, new_affine
