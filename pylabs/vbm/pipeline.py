## Raw file conversion:  nibabel
## RMS / Concat: MRIConcat
## Skullstripping: fslvbm_2_proc_-n
## Segmentation
## Normalizing
## From here there is two paths; filter out covariate or include it in model.
import os, glob
from os.path import join as pathjoin
import niprov
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report, atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.timing import waitForFiles
from pylabs.utils.selection import select_significant
from niprov.options import NiprovOptions
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

exptag='gender_and_vbm_delta_cov_4col_vbm'

subjects = [
317, 328, 332, 334, 335, 347, 353, 364, 371, 376, 379, 381, 384, 385, 396]

fs = getlocaldataroot()
vbmdir = fs+'js/self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/'
matfiledir = pathjoin(vbmdir,'matfiles','matfiles_'+exptag)
resultdir = pathjoin(vbmdir,'randomise_runs','randpar_n500_'+exptag)
qsubdir = pathjoin(vbmdir,'qsubs_defunctcommands')
behavdir = fs+'js/self_control/behavioral_data/behav_from_andy_march27_2015/'
csvfile = behavdir+'EF_and_Brain_july08_2015_Meq0_delta.csv'
niprov.add(csvfile)
imgtemplate = '{0}_mod_merge_{1}.nii.gz'
images = glob.glob(vbmdir+'?M_mod_merg_s4.nii.gz')
[niprov.add(img) for img in images]

## Covariate Filtering
#
# matfiles = csv2fslmat(csvfile, cols=[2], covarcols=[43] selectSubjects=subjects,
#     groupcol=False, demean=False, outdir=matfiledir, opts=opts)
# images = multiregfilt(images, matfiles[0], opts=opts)

## Randomize n500 test run
designfile = vbmdir+'scs_design4col.con'
assert os.path.isfile(designfile)
subcols = range(5,8)+range(18,32)
matfiles = csv2fslmat(csvfile, cols=subcols, covarcols=[2, 43], selectSubjects=subjects,
     groupcol=True, outdir=matfiledir, opts=opts)
randparfiles = multirandpar(images, matfiles, designfile, niterations=500, 
    workdir=qsubdir, outdir=resultdir, opts=opts)

randparfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
waitForFiles(randparfiles, interval=5) # every 5 seconds check if files done.

# find significant results from n500 run to pass along to n5000
#images, matfiles = select_significant(resultdir, vbmdir, matfiledir, 'vbm')

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = pathjoin('data','atlases',atlasfile)
#corepfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
report(randparfiles, atlas, atlaslabels(atlasfile))

exptag='randpar_n5000_gender_and_vbm_delta_cov_fm_sig_n500_4col_vbm'
resultdir = pathjoin(vbmdir,'randomise_runs',exptag)
randparfiles = multirandpar(images, matfiles, designfile, niterations=5000,
    tbss=False, workdir=qsubdir, outdir=resultdir, opts=opts)


