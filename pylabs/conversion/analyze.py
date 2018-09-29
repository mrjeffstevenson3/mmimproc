from pathlib import *
import nibabel as nib
from nibabel.orientations import (io_orientation, inv_ornt_aff, apply_orientation)
import numpy as np
from pylabs.io.images import savenii
from pylabs.utils import *


def analyze2nifti(images, outdir=None, provenance=ProvenanceWrapper()):
    """ Convert files to .nii format using nibabel.

    """
    outimages = []
    for image in images:
        image = Path(image)
        outdir = Path(outdir)
        if not outdir.is_dir():
            outdir.mkdir(parents=True)
        imagebasename = image.name
        if outdir:
            outimage = outdir / replacesuffix(imagebasename, '.nii.gz')
        else:
            outimage = replacesuffix(imagebasename, '.nii.gz')
        print('Converting to nifti '+str(imagebasename))
        img = nib.load(str(image))
        nib.save(img, str(outimage))
        provenance.log(str(outimage), 'converted to nii', str(image), script=__file__)
        outimages.append(str(outimage))
    return outimages


def reorient_mpf(in_hdr_fname, out_nii_fname=None, image_type='MPF', provenance=ProvenanceWrapper()):
    """
    Convert analyse output from vasily's MPF program to RAS+ nifti.
    Must be executed in qt1 directory or some other same level directory to work

    """
    in_hdr_fname = Path(in_hdr_fname)
    if not in_hdr_fname.suffix == '.hdr':
        raise ValueError('input file not analyse header file .hdr. suffix found was '+in_hdr_fname.suffix)
    if out_nii_fname:
        out_nii_fname = Path(out_nii_fname)
        ext = ''.join(out_nii_fname.suffixes)
        if ext not in ['.nii.gz', '.nii']:
            raise ValueError('outfile does not have nifti file extension. ext='+ext)
    else:
        out_nii_fname = replacesuffix(in_hdr_fname, '.nii.gz')
    if not out_nii_fname.parent.is_dir():
        out_nii_fname.parent.mkdir(parents=True)
    # header is bad, cannot use affine from hdr file get from parrec
    if image_type not in ['R1', 'R1_', 'r1', 'r1_', 'MPF', 'mpf', 'MPF_', 'mpf_']:
        raise ValueError('image_type must = MPF or R1_')
    img = nib.load(str(in_hdr_fname))
    if str.upper(image_type) in ['MPF', 'MPF_']:
        parfile = Path('../source_parrec/', replacesuffix(remove_prepend(in_hdr_fname, 'MPF'), '.PAR'))
        affine = nib.load(str(parfile)).affine
    if str.upper(image_type) in ['R1', 'R1_']:
        parfile = Path('../source_parrec/', replacesuffix(remove_prepend(in_hdr_fname, 'R1_'), '.PAR'))
        affine = nib.load(str(parfile)).affine
    # Reorient data block to LAS+ if necessary
    ornt = nib.io_orientation(np.diag([-1, 1, 1, 1]).dot(affine))
    if np.all(ornt == [[0, 1],
                       [1, 1],
                       [2, 1]]):  # already in LAS+
        t_aff = np.eye(4)
        in_data = img.get_data().astype(np.float32)
    else:  # Not in LAS+
        t_aff = inv_ornt_aff(ornt, img.shape)
        affine = np.dot(affine, t_aff)
        in_data = apply_orientation(img.get_data().astype(np.float32), ornt)
    savenii(in_data, affine, out_nii_fname)
    provenance.log(str(out_nii_fname), 'reoriented mpf header to RAS+ nifti', str(in_hdr_fname), script=__file__)
    return
