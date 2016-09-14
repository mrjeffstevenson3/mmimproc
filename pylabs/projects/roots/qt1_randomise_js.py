import os, glob
from os.path import join
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report, atlaslabels
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
from pylabs.utils.timing import waitForFiles
from pylabs.utils.selection import select, withVoxelsOverThresholdOf
from pylabs.utils.files import deconstructRandparFiles
from pylabs.io.images import combineAsVolumes
import pylabs.masking
from pylabs.utils.provenance import ProvenanceWrapper
prov = niprov.Context()
prov.dryrun = True
prov.verbose = True

fs = getnetworkdataroot()
projectdir = join(fs, 'roots_of_empathy')
subjects = [28, 29, 30, 37, 53, 65]
statsdir = join(projectdir, 'correlations_qt1_randomise')
csvfile = 'data/behavior/roots_behavior_transposed.csv'
niprov.add(csvfile)
maskfile = join(statsdir, 'brain_mask.nii.gz')
designfile = join(statsdir, 'roots_design2col.con')
assert os.path.isfile(designfile)

fnametem = 'sub-2013-C0{0}_t1_flirt2sub-2013-C028_sigma1.5.nii.gz'
subjImages = [join(projectdir, 'sub-2013-C0{}'.format(s), 'ses-1', 'qt1',
                fnametem.format(s)) for s in subjects]
combined = join(statsdir, 't1_combined.nii.gz')
combineAsVolumes(subjImages, combined)
images = [combined]
[niprov.add(img) for img in images]

pylabs.masking.maskForStack(combined, maskfile)
assert os.path.isfile(maskfile)

exptag='js_whole_brain_nofilt_t2p7_n500'
matfiledir = join(statsdir,'matfiles','matfiles_'+exptag)
resultdir = join(statsdir,'randpar',exptag)
qsubdir = join(resultdir, 'qsubdir_defunctcommands')

## Covariate Filtering
# matfiles = csv2fslmat(csvfile, cols=[4], selectSubjects=subjects,
#      groupcol=False, demean=False, outdir=matfiledir)
# images = multiregfilt(images, matfiles[0])

## Randomize n500 test run
collist = [64, 92, 96]
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects,
    groupcol=True, outdir=matfiledir)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=500,
     tbss=True, workdir=qsubdir, outdir=resultdir, t_thresh=2.7)
