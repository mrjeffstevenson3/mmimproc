import os, glob
from os.path import join
import niprov
import nibabel, numpy
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
from dipy.align.reslice import reslice
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

fs = getlocaldataroot()


contrasts = ['Congruent','Incongruent',
    'Congruent_gt_Incongruent','Incongruent_gt_Congruent']
fmridir = join(fs,'self_control/hbm_group_data/fmri')

#fmrisubjects = sorted([int(os.path.basename(i)[:3]) for i in fmriimages])
# remap. http://brainmap.wustl.edu/help/mapper.html

# http://nipy.org/nibabel/coordinate_systems.html


def getContrast(filename):
    return '_'.join(os.path.basename(filename).split('.')[0].split('_')[1:])

origdims = (79, 95, 68)
dims1mm = [d*2 for d in origdims]
hdrfilter = join(fmridir, 'analyze', '*.hdr')
hdrimages = sorted(glob.glob(hdrfilter))
for contrast in contrasts:
    print('Working on contrast '+contrast)
    contrastimages = [i for i in hdrimages if getContrast(i)==contrast]
    nsubjects = len(contrastimages)
    data = numpy.full(dims1mm+[nsubjects], numpy.nan)
    for s, image in enumerate(contrastimages):
        imagebasename = os.path.basename(image)
        print('Rescaling image '+image)
        img = nibabel.load(image)
        data1 = img.get_data()
        affine1 = img.get_affine()
        zooms = img.get_header().get_zooms()[:3]
        new_zooms = (1., 1., 1.)
        data2, affine2 = reslice(data1, affine1, zooms, new_zooms)
        data[:,:,:,s] = data2
    groupimg = nibabel.Nifti1Image(data, affine2)
    groupimage = join(fmridir, '{0}_1mm.nii.gz'.format(contrast))
    print('Saving '+groupimage)
    nibabel.save(groupimg, groupimage)
    niprov.log(groupimage, 'grouped and upsampled to 1mm', contrastimages, 
        script=__file__, opts=opts)

#from nipype.interfaces import fsl
#from nipype.testing import example_data
#flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
#flt.inputs.in_file = 'myInput.img'
#flt.inputs.reference = 'myReference.img'
#flt.inputs.out_file = 'moved_subject.nii'
#flt.inputs.out_matrix_file = 'subject_to_template.mat'
#res = flt.run() 

