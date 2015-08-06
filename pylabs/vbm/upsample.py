import os, nibabel
from dipy.align.reslice import reslice


def upsample1mm(images):
    outimages = []
    for image in images:
        imagebasename = os.path.basename(image)
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
        outimages.append(outimage)
    return outimages

