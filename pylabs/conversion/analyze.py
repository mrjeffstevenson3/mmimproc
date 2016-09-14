import os, nibabel
from os.path import join
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.utils import PylabsOptions


def analyze2nifti(images, outdir=None, opts=PylabsOptions()):
    """ Convert files to .nii format using nibabel.

    """
    outimages = []
    for image in images:
        imagebasename = os.path.basename(image)
        if outdir:
            outimage = join(outdir, imagebasename.replace('.hdr','.nii.gz'))
        else:
            outimage = image.replace('.hdr','.nii.gz')
        print('Converting to nifti '+imagebasename)
        img = nibabel.load(image)
        data = img.get_data()
        affine = img.get_affine()
        img2 = nibabel.Nifti1Image(data, affine)
        nibabel.save(img2, outimage)
        niprov.log(outimage, 'converted to nii', image, script=__file__, 
            opts=opts)
        outimages.append(outimage)
    return outimages
