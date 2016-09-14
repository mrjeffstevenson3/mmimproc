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
from pylabs.utils.provenance import ProvenanceWrapper
prov = niprov.Context()
prov.dryrun = True
prov.verbose = True

fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = [28, 29, 30, 37, 53, 65]
#fs = getlocaldataroot()
statsdir = join(fs, project, 'myvbm', 'stats')
behavdir = 'data/behavior/'
csvfile = behavdir+'roots_behavior_transposed.csv'
niprov.add(csvfile)
maskfile = join(statsdir, 'WM_mask.nii.gz')
imgtemplate = '{0}_mod_merg_s3.nii.gz'
measures = ['WM']

skellist = [imgtemplate.format(m) for m in measures]
images = [statsdir+'/'+i for i in skellist]
[niprov.add(img) for img in images]

exptag='t_thresh_2p7_filter_gender_n500'
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
collist = range(24, 105)
#collist = [81, 96]
matfiles = csv2fslmat(csvfile, cols=collist, selectSubjects=subjects,
    groupcol=True, outdir=matfiledir)
masks = {img: maskfile for img in images} # Mask is the same for all images
combs = {img:matfiles for img in images}
randparfiles = multirandpar(combs, designfile, masks=masks, niterations=500,
     tbss=False, workdir=qsubdir, outdir=resultdir, t_thresh=2.7)