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
opts.dryrun = True

subjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
vbmdir = fs+'js/self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
images = glob.glob(vbmdir+'GM_mod_merg_s2.nii.gz')
[niprov.add(img) for img in images]

## Covariate Filtering
filterargs = {'selectSubjects':subjects, 'groupcol':False, 'demean':False, 
    'workdir':vbmdir, 'opts':opts} # preset csv2fslmat arguments
matfiles = csv2fslmat(csvfile, tag='filt_gender', cols=[2], **filterargs)
images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize
designfile = vbmdir+'scs_design2col.con'
assert os.path.isfile(designfile)
corrargs = {'selectSubjects':subjects, 'groupcol':True, 'workdir':vbmdir, 
    'opts':opts}
matfiles = csv2fslmat(csvfile, tag='vars', cols=[5, 21], **corrargs)
multirandpar(images, matfiles, designfile, niterations=100, opts=opts)

#TODO
# niprov: more verbose record; niprov prints full command
# regfilt: multiregfilt multiple filters at once
# regfilt: F flag quotation screws up niprov record f="1"
# randpar: output FILEname include niterations, image filename
# randpar:  cmd = '/usr/share/fsl/5.0/bin/randomise_parallel'' use FSLDIR global to call randomise
# randpar: think about working dir context manager because qsub/condor puts files in CWD

