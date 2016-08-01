import collections
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.fitting_phantoms import fitPhantoms
from pylabs.qt1.coregister_phantoms import coregisterPhantoms
from pylabs.qt1.atlassing_phantoms import atlasPhantoms
from pylabs.qt1.model_pipeline import calculate_model
import niprov
prov = niprov.ProvenanceContext()
fs = getlocaldataroot()
#fs = '/Users/mrjeffs/Documents/Research/data'
projectdir = join(fs, 'phantom_qT1_slu')
#subjects = ['sub-phant2016-03-02', 'sub-phant2016-03-11']
subjects = ['sub-phant2016-07-27']
niftiDict = collections.defaultdict(list)

## convert parrecs to nifti
for subj in subjects:
    subjectdir = join(projectdir, subj)
    niftiDict = convertSubjectParfiles(subj, subjectdir, niftiDict)

## Fitting
t1images = fitPhantoms(niftiDict, projectdir=projectdir, skipExisting=True)

## coregister_phantoms
t1images = coregisterPhantoms(t1images, projectdir=projectdir)

## model_pipeline
expected = calculate_model('slu')

## atlassing_phantoms
atlasPhantoms(t1images, expected, projectdir)




