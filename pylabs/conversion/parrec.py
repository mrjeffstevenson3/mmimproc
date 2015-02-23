# -*- coding: utf-8 -*-

from os import path as op
import nibabel  # noqa
from six import string_types


def par_to_nii(in_file, out_file, scaling='fp'):
    """Load a PAR/REC file, scale it, and save the data (usually as NIfTI)

    Parameters
    ----------
    in_file : str
        Input filename.
    out_file : str.
        Output filename. Should have a ``.nii`` or ``.nii.gz`` to save
        in NIfTI format.
    scaling : str
        Scaling to use. See nibabel's parrec2nii for options.
    """
    if not isinstance(in_file, string_types):
        raise TypeError('in_file must be a str')
    if op.splitext(in_file)[1].lower() != '.par':
        raise RuntimeError('Input must be a .par file')
    nibabel.save(nibabel.load(in_file, scaling=scaling), out_file)
