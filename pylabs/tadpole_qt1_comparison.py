from os.path import join
import collections 
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.files import sortedParGlob
from pylabs.conversion.phantom_conv import phantom_midslice_par2mni as par2mni
from pylabs.qt1.fitting_phantoms import fitPhantoms
from pylabs.qt1.coregister_phantoms import coregisterPhantoms
from pylabs.qt1.atlassing_phantoms import atlasPhantoms
from pylabs.qt1.model_pipeline import calculate_model
## Evaluate which flip angles are required to do an adequate SPGR QT1
## based on tadpole phantom 999

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subj = 'sub-phant2016-01-13'
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
        # interrogate files here for available flip angles. like:
        #            run = [f for f in run if f[1]!='mask']
        #            files, X = zip(*sorted(run, key=lambda s: s[1]))
        ## Vary flip angles used
        # list(itertools.combinations([1,2,3,4,5], 3))
        # pass them to fitPhantoms as a separate dictionary
        niftiDict[k].append(v)


## fitting_phantoms
t1images = fitPhantoms(niftiDict, projectdir=projectdir)

## coregister_phantoms
t1images = coregisterPhantoms(t1images, projectdir=projectdir)

## model_pipeline
expected = calculate_model('slu')

## atlassing_phantoms
atlasPhantoms(t1images, expected, projectdir)




