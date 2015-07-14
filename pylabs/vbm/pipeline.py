## Raw file conversion
# nibabel
## RMS / Concat
# MRIConcat
## Skullstripping
# fslvbm_2_proc_-n
## Segmentation
## Normalizing

## From here there is two paths; filter out covariate or include it in model.



import glob
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from niprov.options import NiprovOptions
from pylabs.utils.paths import getlocaldataroot
opts = NiprovOptions()
opts.dryrun = True

fs = getlocaldataroot()
vbmdir = fs+'js/self_control/hbm_group_data/vbm_17subj/workdir_v1/stats/'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
images = glob.glob(vbmdir+'*mod_merg*')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, groupcol=False, cols=[2], opts=opts)
images = multiregfilt(images, matfiles[0])

matfiles = csv2fslmat(csvfile, groupcol=False, cols=[4], opts=opts)
images = multiregfilt(images, matfiles[0])


## Randomize
designfile = 'scs_design2col.con'
matfiles = csv2fslmat(csvfile, groupcol=True, opts=opts)
multirandpar(images, matfiles, designfile, niterations=500)
