# -*- coding: utf-8 -*-

import subprocess


def dump_header(img_fname, out_fname):
    """Use fslhd to dump an image header to a text file

    Parameters
    ----------
    img_fname : str
        Filename of the image to use.
    out_fname : str
        Filename to save the header to.
    """
    with open(out_fname, 'w') as fid:
        subprocess.check_call(['fslhd', '-x', img_fname], stdout=fid)
