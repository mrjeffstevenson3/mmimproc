import os, nibabel
from os.path import join
import niprov
from dipy.align.reslice import reslice
from pylabs.utils import PylabsOptions


def upsample1mm(images, outdir=None, opts=PylabsOptions()):
    """ Resample images to 1mm isotropic

    Uses dipy.align.reslice
    """
    outimages = []
    for image in images:
        imagebasename = os.path.basename(image)
        if outdir:
            outimage = join(outdir, imagebasename.replace('.nii.gz',
                '_1mm.nii.gz'))
        else:
            outimage = image.replace('.nii.gz','_1mm.nii.gz')
        print('Upsampling '+imagebasename)
        img = nibabel.load(image)
        data = img.get_data()
        affine = img.get_affine()
        zooms = img.get_header().get_zooms()[:3]
        new_zooms = (1., 1., 1.)
        data2, affine2 = reslice(data, affine, zooms, new_zooms)
        img2 = nibabel.Nifti1Image(data2, affine2)
        nibabel.save(img2, outimage)
        niprov.log(outimage, 'upsampled to 1mm', image, script=__file__, 
            opts=opts)
        outimages.append(outimage)
    return outimages

