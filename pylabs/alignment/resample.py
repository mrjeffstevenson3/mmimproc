from pathlib import *
from dipy.align.reslice import reslice
from pylabs.io.images import savenii
import numpy as np
import nibabel as nib


def reslice_roi(in_data, in_affine, in_zooms, out_zooms, ismask=False):   ## out_affine,
    """ Resample roi to matching volume
        Uses dipy.align.reslice
    """

    out_data, new_affine = reslice(in_data, in_affine, in_zooms, out_zooms)

    # assert np.allclose(out_affine, new_affine, 4), 'out affine and new affine do not match.'

    if ismask:
        out_data = np.ceil(out_data)

    return out_data, new_affine

def reslice_niivol(ref_vol, in_vol, out_vol, ismask=False):
    """

    :param ref_vol: The volume to match resampled voxels to.
    :param in_vol:  The volume to be resampled.
    :param ismask: If True then data type set to integer
    :return: saves nifti file to disk and returns resampled data and affine
    """
    ref_vol, in_vol = Path(ref_vol), Path(in_vol)
    if not ref_vol.is_file() or not in_vol.is_file():
        raise ValueError('one or both files not found. please check.')
    orig_img = nib.load(str(in_vol))
    orig_data = orig_img.get_data()
    orig_affine = orig_img.affine
    orig_zooms = orig_img.header.get_zooms()
    ref_img = nib.load(str(ref_vol))
    ref_zooms = ref_img.header.get_zooms()
    out_data, new_affine = reslice(orig_data, orig_affine, orig_zooms, ref_zooms)

    if ismask:
        out_data = np.int16(np.ceil(out_data))

    savenii(out_data, new_affine, out_vol)
    return out_data, new_affine
