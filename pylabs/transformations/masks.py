import nibabel, numpy
from pylabs.utils.paths import tempfile


def absolute(image):
    filename = tempfile(extension='.nii.gz')
    img = nibabel.load(image)
    maskData = numpy.abs(img.get_data())
    maskImg = nibabel.Nifti1Image(maskData, img.get_affine())
    nibabel.save(maskImg, filename)
    return filename
    
