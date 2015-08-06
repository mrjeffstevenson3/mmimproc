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

exptag='filter_gender_and_dti_delta_n500'

subjects= [ 317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]
imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
fs = getlocaldataroot()
tbssdir = fs+'self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
matfiledir = pathjoin(tbssdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(tbssdir,'randpar',exptag)
qsubdir = resultdir+'qsubdir_defunctcommands'
behavdir = fs+'self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
maskfile = tbssdir+'mean_FA_skeletonised_mask.nii.gz'
images = [tbssdir+i for i in skellist]
masks = {img: maskfile for img in images} # Mask is the same for all images
niprov.add(csvfile)
[niprov.add(img) for img in images]

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[2], covarcols=[41], selectSubjects=subjects,
     groupcol=False, demean=False, outdir=matfiledir, opts=opts)
images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize n500 test run
designfile = tbssdir+'scs_design2col.con'
assert os.path.isfile(designfile)
collist = range(5, 8)+range(18, 32)
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects, 
    groupcol=True, outdir=matfiledir, opts=opts)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=500,
     tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))

#atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
#atlas = pathjoin('data','atlases',atlasfile)
#report(selectedCorrPfiles, atlas, atlaslabels(atlasfile))

combs = deconstructRandparFiles(selectedCorrPfiles)

opts.dryrun = False
exptag='filtered_gender_and_dti_delta_2col_n5000_select'
resultdir = pathjoin(tbssdir,'randomise_runs',exptag)
masks = {img: maskfile for img in combs.keys()} # Mask is the same for all images
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

