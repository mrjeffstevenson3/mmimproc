import os, glob
from os.path import join as pathjoin
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.correlation.behavior import csv2fslmat
from mmimproc.correlation.regfilt import multiregfilt
from mmimproc.correlation.randpar import multirandpar
from mmimproc.correlation.atlas import report, atlaslabels
from mmimproc.utils.paths import getnetworkdataroot
from mmimproc.utils.timing import waitForFiles
from mmimproc.utils.selection import select, withVoxelsOverThresholdOf
from mmimproc.utils.files import deconstructRandparFiles
provenance = ProvenanceWrapper()
provenance.config.dryrun = True
provenance.config.verbose = True

subjects = [317, 322, 324, 328, 332, 334, 335, 341, 347, 353, 364, 370, 371, 
    376, 379, 381, 384, 385, 396 ]

fs = getnetworkdataroot()
statsdir = fs+'self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/'
behavdir = fs+'self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
provenance.add(csvfile)
maskfile = statsdir+'mean_FA_skeletonised_mask.nii.gz'

imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
images = [statsdir+i for i in skellist]
[provenance.add(img) for img in images]

exptag='filter_gender_and_dti_delta_n500'
matfiledir = pathjoin(statsdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(statsdir,'randpar',exptag)
qsubdir = pathjoin(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[2], covarcols=[41], selectSubjects=subjects,
     groupcol=False, demean=False, outdir=matfiledir, opts=opts)
images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize n500 test run
designfile = statsdir+'scs_design2col.con'
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

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile),
    relevantImageFilenameSegment=-4)

combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)

opts.dryrun = True
exptag='filtered_gender_and_dti_delta_2col_n5000_select'
resultdir = pathjoin(statsdir,'randomise_runs',exptag)
masks = {img: maskfile for img in combs.keys()} # Mask is the same for all images
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

