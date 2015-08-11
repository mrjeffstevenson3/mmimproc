import os
from os.path import join
import niprov
from nipype.interfaces import fsl
from pylabs.utils import PylabsOptions


def standardize2mni(images, outdir, opts=PylabsOptions()):
    """ Use nipype / FLIRT to coregister an image to the standard MNI template.
    """
    standardizedImages = []
    for image in images:
        imagebasename = os.path.basename(image)
        print('Standardizing '+imagebasename)
        outfile = join(outdir, imagebasename.split('.')[0]+'.nii.gz')

        template = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')
        flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
        flt.inputs.in_file = image
        flt.inputs.reference = template
        flt.inputs.out_file = outfile
        result = flt.run() 
        niprov.log(outfile, 'standardized with FLIRT', image, code=flt.cmdline,
            script=__file__, logtext=result.outputs.out_log, opts=opts)
        standardizedImages.append(outfile)
    return standardizedImages

def space2mni(images, outdir, opts=PylabsOptions()):
    """ Use nipype / FLIRT to put the image in MNI space without transforming.
    """
    standardizedImages = []
    for image in images:
        imagebasename = os.path.basename(image)
        print('Standardizing '+imagebasename)
        outfile = join(outdir, imagebasename.split('.')[0]+'.nii.gz')
        template = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')
        flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
        flt.inputs.in_file = image
        flt.inputs.reference = template
        flt.inputs.out_file = outfile
        flt.inputs.in_matrix_file = 'data/identity.mat'
        flt.inputs.apply_xfm = True
        flt.inputs.interp = 'nearestneighbour'
        result = flt.run() 
        niprov.log(outfile, 'standardized with FLIRT', image, code=flt.cmdline,
            script=__file__, logtext=result.outputs.out_log, opts=opts)
        standardizedImages.append(outfile)
    return standardizedImages


