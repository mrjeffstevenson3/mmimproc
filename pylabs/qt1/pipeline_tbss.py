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
from pylabs.vbm.upsample import upsample1mm
opts = NiprovOptions()
opts.dryrun = False
opts.verbose = True

subjects = [317, 328, 332, 334, 335, 347, 353, 364, 370, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
statsdir = fs+'self_control/hbm_group_data/qT1/tbss_qT1_reg_v7/stats/'
behavdir = fs+'self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'SCS_Behavior_dataset_9_14_15_Meq0_delta_qT1_SS_resptime_D.csv'
niprov.add(csvfile)

images = glob.glob(statsdir+'all_qT1_skeletonised.nii.gz')
[niprov.add(img) for img in images]

exptag='filter_skel_gender_and_qT1_delta_n500'
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
# collist = range(5, 8)+range(18, 32)+[44]
matfiles = csv2fslmat(csvfile, cols=range(49, 69), selectSubjects=subjects,
    groupcol=True, outdir=matfiledir, opts=opts)

combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, niterations=500,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile), 
    relevantImageFilenameSegment=-5)

combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)

exptag='randpar_n5000_filtered_skel_gender_and_qT1_delta_fm_sig_n500_2col_qT1'
resultdir = pathjoin(statsdir,'randomise_runs',exptag)

randparfiles = multirandpar(combs, designfile, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)
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


