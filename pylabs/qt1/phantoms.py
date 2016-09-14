from __future__ import division
import collections, numpy, glob, datetime, pandas, itertools
from os.path import join, isfile, basename
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.io.mixed import listOfDictsToJson
from pylabs.utils.paths import getnetworkdataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.regional import averageByRegion
from pylabs.alignment.phantom import align, applyXformAndSave
provenance = Context()
provget = lambda  f: provenance.get(forFile=f).provenance
singletr = lambda tr: tr[0] if isinstance(tr, list) else tr

"""
This script loops through all phantom session directories and samples
the phantom scans and the corresponding B1 field maps using 
pylabs.regional.averageByRegion. The sampled data is then saved in a json file
in the phantom project directory. This is a separate script since it can take
a long time to convert and sample all these files, whereas the next steps
in the pipeline (fitting e.g.) change frequently but are faster.
"""

## settings
fs = getnetworkdataroot()
scanner = 'disc'
projectdir = join(fs, 'phantom_qT1_{}'.format(scanner))
alignmentTarget = join(projectdir, 'phantom_flipangle_alignment_target.nii')
vialAtlas = join(projectdir,'phantom_alignment_target_round_mask.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]
datafpath = join(projectdir, 'phantomdata.json')

xform = {}
phantoms = []

subjectdirs = glob.glob(join(projectdir, 'phantom_qT1_*'))
for s, subjectdir in enumerate(subjectdirs):
    print('Sampling phantom {} of {}'.format(s+1, len(subjectdirs)))
    phantom = {}
    subject = basename(subjectdir)
    datestr = subject.split('_')[2]
    phantom['date'] = datetime.datetime.strptime(datestr, '%Y%m%d').date()

    ## par2nii
    #niftiDict = convertSubjectParfiles(subject, subjectdir)

    ## Gather files & align
    phantom['method'] = 'spgr'
    alphafilter = '*tr_{}*1.nii'.format(int(11))
    alphafiles = sorted(glob.glob(join(subjectdir,'anat',alphafilter)))
    if not alphafiles:
        continue
    phantom['TR'] = singletr(provget(alphafiles[0])['repetition-time'])

    #if date not in xform:
    phantom['xform'] = align(alphafiles[0], alignmentTarget, delta=10)

    data = pandas.DataFrame(index=vialOrder)

    ## b1 map
    b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))
    alignedB1file = b1file.replace('.nii', '_coreg.nii')
    applyXformAndSave(phantom['xform'], b1file, alignmentTarget, 
        newfile=alignedB1file, provenance=provenance)
    print('Sampling B1')
    data['b1'] = averageByRegion(alignedB1file, vialAtlas)

    ## transform and sample flip-angle files
    
    for alphafile in alphafiles:
        alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
        applyXformAndSave(phantom['xform'], alphafile, alignmentTarget, 
            newfile=alignedAlphafile, provenance=provenance)
        print('Sampling signal for one flip angle..')
        vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
        alpha = provenance.get(forFile=alignedAlphafile).provenance['flip-angle']
        data[alpha] = vialAverages.loc[vialOrder]
    phantom['data'] = data
    phantoms.append(phantom)

listOfDictsToJson(phantoms, datafpath)


