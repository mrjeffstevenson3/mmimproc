from pathlib import *
import nibabel as nib
from os.path import join
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


def reorient_mpf(in_hdr_fname, out_nii_fname=None, outdir=None, provenance=ProvenanceWrapper()):
    """
    Convert analyse output from vasily's MPF program to RAS+ nifti

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
    if outdir:
        outdir = Path(outdir)
        if not outdir.is_dir():
             outdir.mkdir(parents=True)
        out_fname = outdir / out_nii_fname
    else:
        out_fname = out_nii_fname
    provenance.log(str(out_fname), 'reoriented mpf header to RAS+ nifti', str(in_hdr_fname), script=__file__)
    return