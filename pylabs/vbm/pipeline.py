## Raw file conversion
# nibabel
## RMS / Concat
# MRIConcat
## Skullstripping
# fslvbm_2_proc_-n
## Segmentation
## Normalizing

## From here there is two paths; filter out covariate or include it in model.

subjects = [
317,
328,
332,
334,
335,
347,
353,
364,
371,
376,
379,
381,
384,
385,
396,
]


import os
import glob
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from niprov.options import NiprovOptions
from pylabs.utils.paths import getlocaldataroot
opts = NiprovOptions()
opts.dryrun = False

fs = getlocaldataroot()
vbmdir = fs+'js/self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
images = glob.glob(vbmdir+'GM_mod_merg_s2.nii.gz')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, selectSubjects=subjects, groupcol=False, cols=[2], demean=False, opts=opts)
matfiles = [os.path.join(os.getcwd(),m) for m in matfiles]
images = multiregfilt(images, matfiles[0], opts=opts)

#matfiles = csv2fslmat(csvfile, selectSubjects=subjects, groupcol=False, cols=[4], opts=opts)
#images = multiregfilt(images, matfiles[0], opts=opts)


## Randomize
designfile = '/media/DiskArray/shared_data/js/self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/matfiles/scs_design2col.con'
matfiles = csv2fslmat(csvfile, selectSubjects=subjects, groupcol=True, cols=[5, 21], opts=opts)
multirandpar(images, matfiles, designfile, niterations=100, opts=opts)


#TODO
# more verbose record; niprov prints full command
# niprov .discover on stats dir
# randpar output FILEname include niterations, image filename
# multiregfilt multiple
# fsl_regfilt
# full path for matfiles when passing to fsl
# check if fsl can deal with being called not from data directory
# csv2matfiles demean flag doesnt affect filename
# F flag quotation screws up niprov record f="1"
# mask filename convention = WM_mask.nii.gz for VBM
# custom matfiles dir name
# move designfile to stats dir
#cmd = '            cmd = '/usr/share/fsl/5.0/bin/randomise_parallel'' use FSLDIR global to call randomise
# generally fsl command directly to FSLDIR
# think about working dir context manager because qsub/condor puts files in CWD
# #V=variant smoothing, T= TFCE threshold free clustering.
# fsl_regfilt instead of regfilt
