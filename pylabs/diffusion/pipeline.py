import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report, atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.timing import waitForFiles
from pylabs.utils.selection import select, withVoxelsOverThresholdOf
from pylabs.utils.files import deconstructRandparFiles
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

exptag='gender_and_dti_delta_cov'

subjects= [ 317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
fs = getlocaldataroot()
tbssdir = fs+'js/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
matfiledir = pathjoin(tbssdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(tbssdir,'randpar',exptag)
qsubdir = resultdir+'qsubdir_defunctcommands'
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
maskfile = tbssdir+'mean_FA_skeletonised_mask.nii.gz'
images = [tbssdir+i for i in skellist]
masks = {img: maskfile for img in images} # Mask is the same for all images
niprov.add(csvfile)
[niprov.add(img) for img in images]


## Randomize n500 test run
designfile = tbssdir+'scs_design4col.con'
assert os.path.isfile(designfile)
matfiles = csv2fslmat(csvfile, cols=range(5, 39), covarcols=[2, 41],
 selectSubjects=subjects, groupcol=True, outdir=matfiledir, opts=opts)
randparfiles = multirandpar(images, matfiles, designfile, masks=masks, niterations=500,
     tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

# find significant results from n500 run to pass along to n5000
selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))
imagenames, matfilenames = deconstructRandparFiles(selectedCorrPfiles)
images = [pathjoin(vbmdir, i) for i in imagenames]
matfiles = [pathjoin(matfiledir, m) for m in matfilenames]

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile))

exptag='gender_and_dti_delta_cov_4col_n5000_select'
resultdir = pathjoin(tbssdir,'randomise_runs',exptag)
randparfiles = multirandpar(images, matfiles, designfile, masks=masks, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

