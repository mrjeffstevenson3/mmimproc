import os, nibabel
from os.path import join
from pylabs.utils.provenance import ProvenanceWrapper


def analyze2nifti(images, outdir=None, provenance=ProvenanceWrapper()):
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
        provenance.log(outimage, 'converted to nii', image, script=__file__)
        outimages.append(outimage)
    return outimages
