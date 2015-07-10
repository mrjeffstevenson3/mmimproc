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

base = 'self_control/hbm_group_data/'
csvfile = base+'tbss_19subj/workdir_thr1p5_v3/stats/EF_and_Brain_mar26_2015.csv'
images = glob.glob('*mod_merge*')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, groupcol=False, cols=[x], opts=opts)
images = multiregfilt(images, matfiles[0])

matfiles = csv2fslmat(csvfile, groupcol=False, cols=[y], opts=opts)
images = multiregfilt(images, matfiles[0])


## Randomize
designfile = 'scs_design2col.con'
matfiles = csv2fslmat(csvfile, groupcol=True, opts=opts)
multirandpar(images, matfiles, designfile, niterations=500)
