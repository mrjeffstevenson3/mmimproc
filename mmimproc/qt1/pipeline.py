import os, glob
from os.path import join as pathjoin
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.correlation.behavior import csv2fslmat
from mmimproc.correlation.regfilt import multiregfilt
from mmimproc.correlation.randpar import multirandpar
from mmimproc.correlation.atlas import report, atlaslabels
from mmimproc.utils.paths import getlocaldataroot
from mmimproc.utils.timing import waitForFiles
from mmimproc.utils.selection import select, withVoxelsOverThresholdOf
from mmimproc.utils.files import deconstructRandparFiles
from mmimproc.vbm.upsample import upsample1mm
provenance = ProvenanceWrapper()
provenance.config.dryrun = False
provenance.config.verbose = True

subjects = [317, 328, 332, 334, 335, 347, 353, 364, 370, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
statsdir = fs+'self_control/hbm_group_data/qT1/ants_qT1_VBM_v6/stats/'
behavdir = fs+'self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_aug24_2015_Meq0_delta_qT1.csv'
provenance.add(csvfile)

images = glob.glob(statsdir+'all_qT1_MNI_1mm.nii.gz')
[provenance.add(img) for img in images]

exptag='filter_gender_and_qT1_delta_n500'
matfiledir = pathjoin(statsdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(statsdir,'randomise_runs',exptag)
qsubdir = pathjoin(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[2], covarcols=[46], selectSubjects=subjects,
    groupcol=False, demean=False, outdir=matfiledir, opts=opts)
images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize n500 test run
designfile = statsdir+'scs_design2col.con'
assert os.path.isfile(designfile)
collist = range(5, 8)+range(18, 32)+[44]
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects,
    groupcol=True, outdir=matfiledir, opts=opts)

combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, niterations=500,
    workdir=qsubdir, outdir=resultdir, opts=opts)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile), 
    relevantImageFilenameSegment=-5)

combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)

opts.dryrun = False
exptag='randpar_n5000_filtered_gender_and_qT1_delta_fm_sig_n500_2col_qT1'
resultdir = pathjoin(statsdir,'randomise_runs',exptag)

randparfiles = multirandpar(combs, designfile, niterations=5000,
    tbss=False, workdir=qsubdir, outdir=resultdir, opts=opts)
corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))


atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile), 
    relevantImageFilenameSegment=-5)
atlasfile = 'JHU-ICBM-tracts-maxprob-thr0-1mm_newATR1_newCC21_LR_cerebellum.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile), 
    relevantImageFilenameSegment=-5)



