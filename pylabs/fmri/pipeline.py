import os, glob
from os.path import join
import niprov
import nibabel, numpy
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
from pylabs.transformations.standard import standardize2mni
opts = NiprovOptions()
opts.dryrun = False
opts.verbose = True

fs = getlocaldataroot()


contrasts = ['Congruent','Incongruent',
    'Congruent_gt_Incongruent','Incongruent_gt_Congruent']
fmridir = join(fs,'self_control/hbm_group_data/fmri')
mnidir = join(fmridir,'nifti')
mnidims = [182, 218, 182]



def getContrast(filename):
    return '_'.join(os.path.basename(filename).split('.')[0].split('_')[1:])

hdrfilter = join(fmridir, 'analyze', '*.hdr')
hdrimages = sorted(glob.glob(hdrfilter))
[niprov.add(i) for i in hdrimages]
images = standardize2mni(hdrimages, mnidir, opts=opts)


for contrast in contrasts:
    print('Grouping contrast '+contrast)

    contrastimages = [i for i in images if getContrast(i)==contrast]
    nsubjects = len(contrastimages)
    data = numpy.full(mnidims+[nsubjects], numpy.nan)
    for s, image in enumerate(contrastimages):
        imagebasename = os.path.basename(image)
        img = nibabel.load(image)
        data[:,:,:,s] = img.get_data()
        affine = img.get_affine()
    groupimg = nibabel.Nifti1Image(data, affine)
    groupfilename = join(fmridir, '{0}.nii.gz'.format(contrast))
    print('Saving '+groupfilename)
    nibabel.save(groupimg, groupfilename)
    niprov.log(groupfilename, 'grouped', contrastimages, 
        script=__file__, opts=opts)


# remap. http://brainmap.wustl.edu/help/mapper.html
# http://nipy.org/nibabel/coordinate_systems.html


