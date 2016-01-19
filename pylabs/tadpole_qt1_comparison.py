from os.path import join
import collections 
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.phantom_conv import phantom_midslice_par2mni as par2mni

import glob
def sortedParGlob (filefilter):
    return sorted(glob.glob(filefilter), key=lambda f: int(f.split('_')[-2]))

## Evaluate which flip angles are required to do an adequate SPGR QT1
## based on tadpole phantom 999

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subj = 'sub-phant20160113'
subjectdir = join(projectdir, subj)

## convert parrecs to nifti
anatdir = join(subjectdir, 'anat')
niftiDict = collections.defaultdict(list)
spgrFilter = 'source_parrec/*SPGR*.PAR'
phantSPGRparfiles = sortedParGlob(join(subjectdir, spgrFilter))
scaling = 'fp'
method = 'orig_spgr'
fname = subj+'_'+'orig_spgr'
for parfile in phantSPGRparfiles:
    key, val = par2mni(parfile=parfile, datadict=niftiDict, method=method, 
        outdir=anatdir, exceptions=[], outfilename=fname, scaling=scaling)
    for k, v in zip(key, val):
        niftiDict[k].append(v)

## fitting_phantoms
## coregister_phantoms
## model_pipeline
## atlassing (phantoms)





