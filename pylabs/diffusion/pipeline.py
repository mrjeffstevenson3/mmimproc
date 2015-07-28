import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.timing import waitForFiles
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = False
opts.verbose = True

exptag='gender_and_dti_delta_cov'

subjects= [ 317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
fs = getlocaldataroot()
tbssdir = fs+'js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
matfiledir = pathjoin(tbssdir,'matfiles',exptag)
resultdir = pathjoin(tbssdir,'randpar',exptag)
qsubdir = resultdir+'qsubdir_defunctcommands'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
maskfile = tbssdir+'mean_FA_skeletonised_mask.nii.gz'
images = [tbssdir+i for i in skellist]
masks = {img: maskfile for img in images} # Mask is the same for all images
niprov.add(csvfile)
[niprov.add(img) for img in images]


## Randomize
designfile = tbssdir+'scs_design4col.con'
assert os.path.isfile(designfile)
matfiles = csv2fslmat(csvfile, cols=range(5, 39), covarcols=[2, 41],
    selectSubjects=subjects, groupcol=True, outdir=matfiledir, opts=opts)
randparfiles = multirandpar(images, matfiles, designfile, masks=masks, 
    niterations=500, tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

waitForFiles(randparfiles, interval=5) # every 5 seconds check if files done.
report()

