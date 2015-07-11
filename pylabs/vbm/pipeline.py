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
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = True

fs = '/diskArray/mirror/'
local = '/diskArray/data/scs/'
vbmdir = 'self_control/hbm_group_data/vbm_17subj/workdir_v1/stats/'
csvfile = local+'EF_and_Brain_july08_2015_Meq0_delta.csv'
images = glob.glob(vbmdir+'*mod_merge*')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, groupcol=False, cols=[2], opts=opts)
images = multiregfilt(images, matfiles[0])

matfiles = csv2fslmat(csvfile, groupcol=False, cols=[4], opts=opts)
images = multiregfilt(images, matfiles[0])


## Randomize
designfile = 'scs_design2col.con'
matfiles = csv2fslmat(csvfile, groupcol=True, opts=opts)
multirandpar(images, matfiles, designfile, niterations=500)
