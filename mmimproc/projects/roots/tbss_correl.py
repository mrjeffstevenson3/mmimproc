import os, glob
from os.path import join
from mmimproc.correlation.behavior import csv2fslmat
from mmimproc.correlation.regfilt import multiregfilt
from mmimproc.correlation.randpar import multirandpar
from mmimproc.correlation.atlas import report, atlaslabels
from mmimproc.utils.paths import getlocaldataroot, getnetworkdataroot
from mmimproc.utils.timing import waitForFiles
from mmimproc.utils.selection import select, withVoxelsOverThresholdOf
from mmimproc.utils.files import deconstructRandparFiles
from mmimproc.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
prov.dryrun = True
prov.verbose = True

fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = [28, 29, 30, 37, 53, 65]
#fs = getlocaldataroot()
statsdir = join(fs, project, 'mytbss_mf_v1', 'stats')
behavdir = 'data/behavior/'
csvfile = behavdir+'roots_behavior_transposed.csv'
prov.add(csvfile)
#maskfile = join(statsdir, 'all_FA_qformfix_reg2templ_mask_edited.nii.gz')
maskfile = join(statsdir, 'mean_FA_skeleton_mask.nii.gz')

imgtemplate = 'all_{0}_skeletonised.nii.gz'
#imgtemplate = 'all_{0}_qformfix_reg2templ.nii.gz'
#measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
measures = ['FA', 'RA', 'MD']
#measures = ['FA', 'F2', 'MD', 'RA']
skellist = [imgtemplate.format(m) for m in measures]
images = [statsdir+'/'+i for i in skellist]
[prov.add(img) for img in images]

exptag='skeletonised_t_thresh_2p7_nofilt_n500'
matfiledir = join(statsdir,'matfiles','matfiles_'+exptag)
resultdir = join(statsdir,'randpar',exptag)
qsubdir = join(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
matfiles = csv2fslmat(csvfile, cols=[4], selectSubjects=subjects,
     groupcol=False, demean=False, outdir=matfiledir)
images = multiregfilt(images, matfiles[0])

## Randomize n500 test run
designfile = join(statsdir, 'roots_design2col.con')
assert os.path.isfile(designfile)
#collist = range(24, 105)
collist = [81, 96]
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects,
    groupcol=True, outdir=matfiledir)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=500,
     tbss=False, workdir=qsubdir, outdir=resultdir, t_thresh=2.7)
#
# corrPfiles = [f+'_tfce_corrp_tstat1.nii.gz' for f in randparfiles]
# corrPfiles += [f+'_tfce_corrp_tstat2.nii.gz' for f in randparfiles]
# waitForFiles(corrPfiles, interval=5) # every 5 seconds check if files done.
#
# selectedCorrPfiles = select(corrPfiles, withVoxelsOverThresholdOf(.95))
#
# atlasfile = 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz'
# atlas = join('data','atlases',atlasfile)
# report(selectedCorrPfiles, atlas, atlaslabels(atlasfile),
#     relevantImageFilenameSegment=-4)
#
# combs = deconstructRandparFiles(selectedCorrPfiles, matdir=matfiledir, imgdir=statsdir)
#
# prov.dryrun = True
# exptag='testrun_filtered_gender_2col_n5000_select'
# resultdir = join(statsdir,'randomise_runs',exptag)
# masks = {img: maskfile for img in combs.keys()} # Mask is the same for all images
# randparfiles = multirandpar(combs, designfile, masks=masks, niterations=5000,
#     tbss=True, workdir=qsubdir, outdir=resultdir)
#
