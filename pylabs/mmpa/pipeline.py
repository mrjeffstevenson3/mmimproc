import os, glob
from os.path import join
import niprov
import nibabel, numpy
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
from pylabs.vbm.upsample import upsample1mm
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

fs = getlocaldataroot()
resultdir = join(fs,'self_control/hbm_group_data/mmpa/')
images = []
measures = []

## Behavior
behavdir = join(fs,'self_control/behavioral_data/behav_from_andy_march27_2015/')
csvfile = join(behavdir,'EF_and_Brain_july08_2015_Meq0_delta.csv')
niprov.add(csvfile)

## VBM
vbmsubjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]
vbmdir = join(fs,'self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/')
#vbmimgs2mm = glob.glob(join(vbmdir, '?M_mod_merg_s4.nii.gz'))
#images += upsample1mm(vbmimgs2mm, opts=opts) # is this correct for 4D files?
images += glob.glob(join(vbmdir, '?M_mod_merg_s4_1mm.nii.gz'))
measures += [os.path.basename(i)[:2] for i in images]

## TBSS
tbsssubjects = [317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
tbssdir = join(fs,'self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/')
imgtemplate = 'all_{0}_skeletonised.nii.gz'
tbssmeasures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
measures += tbssmeasures
skellist = [imgtemplate.format(m) for m in tbssmeasures]
images += [join(tbssdir,i) for i in skellist]

## FMRI
## assuming fmri pipeline has ran.
fmridir = join(fs,'self_control/hbm_group_data/fmri')
fmriimages = glob.glob(join(fmridir, 'analyze', '*_Congruent_gt_Incongruent.hdr'))
img = nibabel.load(fmriimages[0])
images += fmriimages
fmrisubjects = sorted([int(os.path.basename(i)[:3]) for i in fmriimages])
# remap. http://brainmap.wustl.edu/help/mapper.html

## MM
#[niprov.add(img) for img in images]
commonSubjects = set.intersection(*map(set, 
    [fmrisubjects, vbmsubjects, tbsssubjects]))

for i in images:
    print(i)

nsubjects = len(commonSubjects)
nmeasures = len(measures)
spatialdims = (182, 218, 182)
# subjects * measures * x * y * z
data = numpy.zeros((nsubjects, nmeasures)+spatialdims)
for s, subjectid in enumerate(commonSubjects):
    for m, measure in enumerate(measures):
        pass



