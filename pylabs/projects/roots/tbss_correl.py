import os, glob
from os.path import join
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report, atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.timing import waitForFiles
from pylabs.utils.selection import select, withVoxelsOverThresholdOf
from pylabs.utils.files import deconstructRandparFiles
import niprov
prov = niprov.Context()
prov.dryrun = True
prov.verbose = True

#fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = ['sub-2013-C028', 'sub-2013-C029', 'sub-2013-C030', 'sub-2013-C037', 'sub-2013-C053', 'sub-2013-C065']
fs = getlocaldataroot()
statsdir = join(fs, project, 'mytbss_mf_v1', 'stats')
behavdir = 'data/behavior/'
csvfile = behavdir+'roots_behavior_transposed.csv'
niprov.add(csvfile)
maskfile = join(statsdir, 'mean_FA_skeletonised_mask.nii.gz')

imgtemplate = 'all_{0}_skeletonised.nii.gz'
#measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
measures = ['FA']
skellist = [imgtemplate.format(m) for m in measures]
images = [statsdir+i for i in skellist]
[niprov.add(img) for img in images]

exptag='testrun_filter_gender_n500'
matfiledir = join(statsdir,'matfiles','matfiles_'+exptag)
resultdir = join(statsdir,'randpar',exptag)
qsubdir = join(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[7], selectSubjects=subjects,
     groupcol=False, demean=False, outdir=matfiledir)
images = multiregfilt(images, matfiles[0])

## Randomize n500 test run
designfile = join(statsdir, 'roots_design2col.con')
assert os.path.isfile(designfile)
collist = range(56, 137)
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects,
    groupcol=True, outdir=matfiledir)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=500,
     tbss=True, workdir=qsubdir, outdir=resultdir)

corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.

selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))

atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
atlas = join('data','atlases',atlasfile)
report(selectedCorrPfiles, atlas, atlaslabels(atlasfile),
    relevantImageFilenameSegment=-4)

combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)

opts.dryrun = True
exptag='testrun_filtered_gender_2col_n5000_select'
resultdir = join(statsdir,'randomise_runs',exptag)
masks = {img: maskfile for img in combs.keys()} # Mask is the same for all images
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=5000,
    tbss=True, workdir=qsubdir, outdir=resultdir, opts=opts)

