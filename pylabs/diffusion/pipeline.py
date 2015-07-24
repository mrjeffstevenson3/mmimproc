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

subjects= [ 317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
fs = getlocaldataroot()
tbssdir = fs+'js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
qsubdir = tbssdir+'qsubdir'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
images = [tbssdir+i for i in skellist]
[niprov.add(img) for img in images]

## Randomize
designfile = tbssdir+'scs_design4col.con'
assert os.path.isfile(designfile)
matfiles = csv2fslmat(csvfile, tag='gender_and_dti_delta_cov', cols=range(5, 39), 
    covarcols=[2, 41], selectSubjects=subjects, groupcol=True, workdir=tbssdir, opts=opts)
multirandpar(images, matfiles, designfile, niterations=500, workdir=qsubdir,
    opts=opts)

