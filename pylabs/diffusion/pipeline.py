## Raw file conversion:  nibabel
## RMS / Concat: MRIConcat
## Skullstripping: fslvbm_2_proc_-n
## Segmentation
## Normalizing
## From here there is two paths; filter out covariate or include it in model.
import os, glob
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = False
opts.verbose = True

subjects= [ 317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 376, 379, 381, 384, 385, 396 ]
skellist = [ 'all_F1_skeletonised.nii.gz', 'all_F2_skeletonised.nii.gz', 'all_FA_skeletonised.nii.gz', 'all_L1_skeletonised.nii.gz', 'all_MD_skeletonised.nii.gz', 'all_MO_skeletonised.nii.gz', 'all_RA_skeletonised.nii.gz', 'all_AD_skeletonised.nii.gz', 'all_L2_skeletonised.nii.gz', 'all_L3_skeletonised.nii.gz' ]
fs = getlocaldataroot()
tbssdir = fs+'js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
qsubdir = tbssdir+'qsubdir'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
images = [ tbssdir+i for i in skellist ]


[niprov.add(img) for img in images]

## Covariate Filtering
# filterargs = {'selectSubjects':subjects, 'groupcol':False, 'demean':False,
#     'workdir':tbssdir, 'opts':opts} # preset csv2fslmat arguments
# matfiles = csv2fslmat(csvfile, tag='filt_gender', cols=[2], **filterargs)
# images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize
designfile = tbssdir+'scs_design4col.con'
assert os.path.isfile(designfile)
corrargs = {'selectSubjects':subjects, 'groupcol':True, 'workdir':tbssdir,
    'opts':opts}
matfiles = csv2fslmat(csvfile, tag='gender_and_dti_delta_cov', cols=range(5, 39), covarcols=[2, 41], **corrargs)
multirandpar(images, matfiles, designfile, niterations=500, workdir=qsubdir,
    opts=opts)

