import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report, atlaslabels
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils.timing import waitForFiles
from pylabs.utils.selection import select, withVoxelsOverThresholdOf
from pylabs.utils.files import deconstructRandparFiles
from niprov.config import Configuration
opts = Configuration()
opts.dryrun = False
opts.verbose = True

subjects = [201, 202, 203, 204, 205, 206, 209, 210, 211, 212, 216, 219, 220, 221, 222, 223,
            903, 909, 910, 912, 913, 915, 916, 917, 919, 920, 921, 922, 923, 924, 925 ]

fs = getnetworkdataroot()
statsdir = fs+'bilingual_dti/mytbss_31subj_fsl_dtifit_mf_fixed_vecs_v5/stats/'
behavdir = fs+'bilingual_dti/behavioral_data/'
csvfile = behavdir+'SPA_group_gender_bilingual_spoken_and_auditory_exposure_and_confidence_SES_Edu_grp_cols_nov16_2015_v13.csv'
niprov.add(csvfile)
maskfile = statsdir+'mean_FA_skeleton_mask.nii.gz'

imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = [ 'FA', 'l1', 'md', 'mo', 'rd', 'WM', 'l2', 'l3']
skellist = [imgtemplate.format(m) for m in measures]
images = [statsdir+i for i in skellist]
[niprov.add(img) for img in images]

exptag='filtered_gend_no_demean_31subj_group_csv13_n5000'
matfiledir = pathjoin(statsdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(statsdir,'randomise_runs',exptag)
qsubdir = pathjoin(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[3], covarcols=None, selectSubjects=subjects,
     groupcol=False, demean=False, outdir=matfiledir, opts=opts)
images = multiregfilt(images, matfiles[0], opts=opts)
opts.dryrun = False
## Randomise Group run
designfile = statsdir+'design_2col_group_only.con'
assert os.path.isfile(designfile)
matfiles = csv2fslmat(csvfile, covarcols=[30, 31], selectSubjects=subjects,
    groupcol=False, demean=False, outdir=matfiledir, opts=opts)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=5000,
     tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)
opts.dryrun = True
## Randomize n500 test run
exptag='filtered_gend_no_demean_31subj_behav_corr_v12_n500'
resultdir = pathjoin(statsdir,'randomise_runs',exptag)
designfile = statsdir+'bilingual_dti_design2col.con'
assert os.path.isfile(designfile)
collist = range(15,29)
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects,
    groupcol=True, demean=True, outdir=matfiledir, opts=opts)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=500,
     tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.97))

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile),
    relevantImageFilenameSegment=-4)

combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)

#opts.dryrun = False
exptag='filtered_gend_31subj_behav_corr_v12_n5000_sel_thr97'
resultdir = pathjoin(statsdir,'randomise_runs',exptag)
masks = {img: maskfile for img in combs.keys()} # Mask is the same for all images
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

#plotting
