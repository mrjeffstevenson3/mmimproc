from __future__ import division
import collections, numpy, glob, datetime, pandas, itertools
from os.path import join, isfile, basename
from niprov import Context
from pylabs.io.mixed import mixedDataToJson
from pylabs.utils.paths import getnetworkdataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.regional import averageByRegion
from pylabs.alignment.phantom import align, applyXformAndSave
provenance = Context()
provget = lambda  f: provenance.get(forFile=f).provenance
singletr = lambda tr: tr[0] if isinstance(tr, list) else tr

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
for subjectdir in subjectdirs:
    phantom = {}
    subject = basename(subjectdir)
    datestr = subject.split('_')[2]
    phantom['date'] = datetime.datetime.strptime(datestr, '%Y%m%d').date()

    ## par2nii
    niftiDict = convertSubjectParfiles(subject, subjectdir)

    ## Gather files & align
    alphafilter = '*tr_{}*1.nii'.format(int(TR))
    alphafiles = sorted(glob.glob(join(subjectdir,'anat',alphafilter)))
    if not alphafiles:
        print('\n\n\nNO SPGRS TR11 FOUND FOR {}\n\n\n'.format(subject))
        continue
    phantom['TR'] = singletr(provget(alphafiles[0])['repetition-time'])

    if date not in xform:
        phantom['xform'] = align(alphafiles[0], alignmentTarget, delta=10)

    data = pandas.DataFrame()

    ## b1 map
    b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))
    alignedB1file = b1file.replace('.nii', '_coreg.nii')
    applyXformAndSave(xform[date], b1file, alignmentTarget, 
        newfile=alignedB1file, provenance=provenance)
    print('Sampling B1')
    data['b1'] = averageByRegion(alignedB1file, vialAtlas).loc[vialOrder]

    ## transform and sample flip-angle files
    
    for alphafile in alphafiles:
        alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
        applyXformAndSave(xform[date], alphafile, alignmentTarget, 
            newfile=alignedAlphafile, provenance=provenance)
        print('Sampling signal for one flip angle..')
        vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
        alpha = provenance.get(forFile=alignedAlphafile).provenance['flip-angle']
        data[alpha] = vialAverages.loc[vialOrder]
    phantom['data'] = data
    phantoms.append(phantom)

listOfDictsToJson(phantoms, datafpath)


