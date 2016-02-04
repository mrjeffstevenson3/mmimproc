from os.path import join
import collections, itertools
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.files import sortedParGlob
from pylabs.conversion.phantom_conv import (phantom_midslice_par2mni, 
                                        phantom_B1_midslice_par2mni)
from pylabs.qt1.fitting_phantoms import fitPhantoms
from pylabs.qt1.coregister_phantoms import coregisterPhantoms
from pylabs.qt1.atlassing_phantoms import atlasPhantoms
from pylabs.qt1.model_pipeline import calculate_model
from pylabs.qt1.correspondence_phantoms import createSpgrTseirCorrespondenceImages
## Evaluate which flip angles are required to do an adequate SPGR QT1
## based on tadpole phantom 999

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subj = 'sub-phant2016-01-13'
subjectdir = join(projectdir, subj)

## convert parrecs to nifti
niftiDict = collections.defaultdict(list)
parfiles = sortedParGlob(join(subjectdir, 'source_parrec/*.PAR'))
for parfile in parfiles:
    args = {}
    if 'SPGR' in parfile or 'IRTSE' in parfile:
        if 'SPGR' in parfile:
            method = 'orig_spgr'
        else:
            method = 'tseir'
        args['scaling'] = 'fp'
        args['method'] = method
        args['outdir'] = join(subjectdir, 'anat')
        par2mni = phantom_midslice_par2mni
    elif 'B1' in parfile and 'fixed' in parfile:
        method = 'b1map'
        args['scaling'] = 'dv'
        args['outdir'] = join(subjectdir, 'fmap')
        par2mni = phantom_B1_midslice_par2mni
    else: 
        continue
    args['parfile'] = parfile
    args['datadict'] = niftiDict
    args['flipexception'] = ['']
    args['protoexception'] = ['20160113']
    args['outfilename'] = subj+'_'+method
    key, val = par2mni(**args)
    for k, v in zip(key, val):
        niftiDict[k].append(v)

xdict = {}
for key in niftiDict:
    if key[1]=='orig_spgr_mag':
        ## Figure out which combinations of flip angles we can test
        spgrKey = [k for k in niftiDict.keys() if k[1]=='orig_spgr_mag'][0]
        spgrFilesAndFlipAngles = niftiDict[spgrKey]
        allAngles = sorted([i[1] for i in spgrFilesAndFlipAngles])
        combinations = list(itertools.combinations(allAngles, 3))
        xdict[key] = combinations

t1images = fitPhantoms(niftiDict, projectdir=projectdir, xdict=xdict, 
    skipExisting=True)

## correspondence_phantoms: create special spgr/tseir ratio images
createSpgrTseirCorrespondenceImages(t1images, projectdir=projectdir)

## coregister_phantoms
t1images = coregisterPhantoms(t1images, projectdir=projectdir)

## model_pipeline
expected = calculate_model('slu')

## atlassing_phantoms
atlasPhantoms(t1images, expected, projectdir)




