## Raw file conversion:  nibabel
## RMS / Concat: MRIConcat
## Skullstripping: fslvbm_2_proc_-n
## Segmentation
## Normalizing
## From here there is two paths; filter out covariate or include it in model.
import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

exptag='gender_filter'

subjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
vbmdir = fs+'js/self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/'
matfiledir = pathjoin(vbmdir,'matfiles',exptag)
resultdir = pathjoin(vbmdir,'randpar',exptag)
qsubdir = pathjoin(vbmdir,'qsubs_defunctcommands')
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
images = glob.glob(vbmdir+'GM_mod_merg_s2.nii.gz')
[niprov.add(img) for img in images]

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[2], selectSubjects=subjects, 
    groupcol=False, demean=False, outdir=matfiledir, opts=opts)
images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize
designfile = vbmdir+'scs_design2col.con'
assert os.path.isfile(designfile)
matfiles = csv2fslmat(csvfile, cols=[5, 21], selectSubjects=subjects, 
    groupcol=True, outdir=matfiledir, opts=opts)
multirandpar(images, matfiles, designfile, niterations=100, workdir=qsubdir, 
    outdir=resultdir, opts=opts)

