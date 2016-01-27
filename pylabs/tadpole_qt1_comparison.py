from os.path import join
import collections, itertools
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
        niftiDict[k].append(v)

## Figure out which combinations of flip angles we can test
allAngles = sorted([i[1] for i in niftiDict.values()[0] if i[1]!='mask'])
combinations = list(itertools.combinations(allAngles, 3))
ncombs = len(combinations)

## Fit each combination of flip angles:
t1images = []
for s, xsample in enumerate(combinations):
    print('Fitting flip angle combination {0} of {1}'.format(s, ncombs))
    t1images += fitPhantoms(niftiDict, projectdir=projectdir, X=xsample, 
        skipExisting=True)

## coregister_phantoms
t1images = coregisterPhantoms(t1images, projectdir=projectdir)

## model_pipeline
expected = calculate_model('slu')

## atlassing_phantoms
atlasPhantoms(t1images, expected, projectdir)




