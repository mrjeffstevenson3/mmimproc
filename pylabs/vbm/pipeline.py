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
opts.dryrun = True
opts.verbose = True

subjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
statsdir = fs+'self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/'
behavdir = fs+'self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)





images = glob.glob(statsdir+'?M_mod_merg_s4.nii.gz')
[niprov.add(img) for img in images]

exptag='randpar_n500_gender_and_vbm_delta_cov_4col_vbm'
matfiledir = pathjoin(statsdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(statsdir,'randomise_runs',exptag)
qsubdir = pathjoin(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
# matfiles = csv2fslmat(csvfile, cols=[2], covarcols=[43] selectSubjects=subjects,
#     groupcol=False, demean=False, outdir=matfiledir, opts=opts)
# images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize n500 test run
designfile = statsdir+'scs_design4col.con'
assert os.path.isfile(designfile)
collist = range(5, 8)+range(18, 32)
matfiles = csv2fslmat(csvfile, cols=collist, covarcols=[2, 43], selectSubjects=subjects,
    groupcol=True, outdir=matfiledir, opts=opts)

combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, niterations=500,
    workdir=qsubdir, outdir=resultdir, opts=opts)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))

selectedCorrPfiles1mm = upsample1mm(selectedCorrPfiles, opts=opts)
atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
report(selectedCorrPfiles1mm, atlas, atlaslabels(atlasfile), 
    relevantImageFilenameSegment=-5)

combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)

opts.dryrun = True
exptag='randpar_n5000_gender_and_vbm_delta_cov_fm_sig_n5000_4col_vbm'
resultdir = pathjoin(statsdir,'randomise_runs',exptag)

randparfiles = multirandpar(combs, designfile, niterations=5000,
    tbss=False, workdir=qsubdir, outdir=resultdir, opts=opts)




