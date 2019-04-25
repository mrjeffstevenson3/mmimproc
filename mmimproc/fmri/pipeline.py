import os, glob
from os.path import join
from mmimproc.utils.provenance import ProvenanceWrapper
import nibabel, numpy
from mmimproc.utils.paths import getlocaldataroot
from mmimproc.utils import Filesystem
from mmimproc.transformations.standard import standardizeBasedOnAbsoluteMask
provenance = ProvenanceWrapper()
filesys = Filesystem()

fs = getlocaldataroot()


contrasts = ['Congruent','Incongruent',
    'Congruent_gt_Incongruent','Incongruent_gt_Congruent']
fmridir = join(fs,'self_control/hbm_group_data/fmri')
mnidir = join(fmridir,'nifti_mni')
filesys.makedirs(mnidir)
mnidims = [182, 218, 182]


hdrfilter = join(fmridir, 'analyze', '*.hdr')
images = sorted(glob.glob(hdrfilter))
[provenance.add(i) for i in images]
images = [standardizeBasedOnAbsoluteMask(i, mnidir) for i in images]

def getContrast(filename):
    return '_'.join(os.path.basename(filename).split('.')[0].split('_')[1:])

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
    provenance.log(groupfilename, 'grouped', contrastimages, 
        script=__file__)


# remap. http://brainmap.wustl.edu/help/mapper.html
# http://nipy.org/nibabel/coordinate_systems.html


