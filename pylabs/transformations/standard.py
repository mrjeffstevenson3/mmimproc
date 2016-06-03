import os
from os.path import join
import niprov
from nipype.interfaces import fsl
from pylabs.utils import PylabsOptions
import pylabs.transformations.masks as masks
from pylabs.utils.paths import tempfile


def standardizeBasedOnAbsoluteMask(image, outdir=None, opts=PylabsOptions()):
    """ Use nipype / FLIRT to put the image in MNI space without transforming.
    """
    imagebasename = os.path.basename(image)
    print('Standardizing '+imagebasename)
    outfile = join(outdir, imagebasename.split('.')[0]+'.nii.gz')
    matfile = join(outdir, imagebasename.split('.')[0]+'_2mni.mat')
    template = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')
    # align mask
    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.in_file = masks.absolute(image)
    flt.inputs.reference = template
    flt.inputs.out_file = tempfile(extension='.nii.gz')
    flt.inputs.out_matrix_file = matfile
    flt.inputs.interp = 'nearestneighbour'
    result = flt.run() 
    # align using transformation matrix from mask alignment
    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.in_file = image
    flt.inputs.reference = template
    flt.inputs.out_file = outfile
    flt.inputs.in_matrix_file = matfile
    flt.inputs.out_matrix_file = tempfile(extension='.mat')
    flt.inputs.apply_xfm = True
    result = flt.run() 
    #niprov.log(outfile, 'standardized with FLIRT', image, code=flt.cmdline,
    #    script=__file__, logtext=result.outputs.out_log, opts=opts)
    return outfile


