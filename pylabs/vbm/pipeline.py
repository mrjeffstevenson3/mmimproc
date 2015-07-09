## Raw file conversion
# nibabel
## RMS / Concat
# MRIConcat
## Skullstripping
# fslvbm_2_proc_-n
## Segmentation
## Normalizing

## From here there is two paths; filter out covariate or include it in model.

## Covariate Filtering
# create gender covariate mat file from csv
# reg_filt script

## Randomize
import glob
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.randpar import multirandpar
base = 'self_control/hbm_group_data/'
csvfile = base+'tbss_19subj/workdir_thr1p5_v3/stats/EF_and_Brain_mar26_2015.csv'
designfile = 'scs_design2col.con'
matfiles = csv2fslmat(csvfile, groupcol=True)
images = glob.glob('*mod_merge*')
multirandpar(images, matfiles, designfile, niterations=500)
