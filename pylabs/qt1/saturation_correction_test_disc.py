from __future__ import division
import collections, numpy, glob, datetime, pandas
from numpy import radians
import matplotlib.pyplot as plt
from os.path import join, isfile
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.model_pipeline import modelForDate
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.regional import averageByRegion
from pylabs.alignment.phantom import align, applyXformAndSave
from pylabs.qt1.simplefitting import fitT1
provenance = Context()
def prov(fpath):
    return provenance.get(forFile=fpath).provenance

## settings
fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_disc')
subject = 'phantom_qT1_20140618'
date = datetime.date(2014, 6, 18)
subjectdir = join(projectdir,subject)
alignmentTarget = join(projectdir, 
    'phantom_flipangle_alignment_target_20140618_fa10.nii')
vialAtlas = join('data','atlases',
    'new_vial_mask_20140618_fa10-mask.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]

import pylabs.qt1.corrections.jopt as correct
correctionname = correct.__name__.split('.')[-1]

## Get brain sample:
from pylabs.qt1.brainsampling import sample

xform = {}
adata = {}
correction = {}
phantom = {}
brain = {}
TR = 11.
alphas = [2,10,20]

phantom[TR] = pandas.DataFrame(index=vialOrder, 
                columns=['model','fit','corr'], dtype=float)

## par2nii
niftiDict = convertSubjectParfiles(subject, subjectdir)

## model_pipeline
phantom[TR]['model'] = modelForDate(date, 'disc')[vialOrder]

## Gather files & align
niftidictkey = [k for k in niftiDict.keys() if 'spgr' in k[1]][0]
spgrdict = dict(niftiDict[niftidictkey])
alphafiles = [k for k, v in spgrdict.items() if v in alphas]
provTR = prov(alphafiles[0])['repetition-time']
if hasattr(provTR, '__iter__'):
    provTR = provTR[0]
assert TR == provTR
for a, alpha in enumerate(alphas):
    assert alpha == prov(alphafiles[a])['flip-angle']

xform[TR] = align(alphafiles[1], alignmentTarget, delta=10)

## b1 map
b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))
alignedB1file = b1file.replace('.nii', '_coreg.nii')
applyXformAndSave(xform[TR], b1file, alignmentTarget, 
    newfile=alignedB1file, provenance=provenance)
print('Sampling B1')
B1 = averageByRegion(alignedB1file, vialAtlas).loc[vialOrder]

## transform and sample flip-angle files
adata[TR] = pandas.DataFrame()
for alphafile in alphafiles:
    alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
    applyXformAndSave(xform[TR], alphafile, alignmentTarget, 
        newfile=alignedAlphafile, provenance=provenance)
    print('Sampling signal for one flip angle..')
    vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
    alpha = prov(alignedAlphafile)['flip-angle']
    adata[TR][alpha] = vialAverages
adata[TR] = adata[TR].loc[vialOrder]
alphas = adata[TR].columns.values.tolist()

A = radians(alphas)

## Initial fit on vials
phantom[TR]['fit'] = fitT1(adata[TR], A, B1, TR)
## determine Correction
correction[TR] = correct.create(adata[TR], A, B1, phantom[TR]['model'], 
                                phantom[TR]['fit'], TR)
try:
    if isinstance(correction[TR][0], str):
        correctionname = correction[TR][0]
except Exception as e:
    pass
## apply Correction fit on vials
phantom[TR]['corr'] = correct.apply(correction[TR], adata[TR], A, B1)
## apply Correction fit on brain sample
brain[TR] = pandas.DataFrame(index=sample.index, 
                columns=['fit','corr'], dtype=float)
brainAngles = list(sample.columns.values[-3:])
brain[TR]['fit'] = sample['fit']
brain[TR]['corr'] = correct.apply(correction[TR], sample[brainAngles], 
                                    radians(brainAngles), sample['B1'])

## plotting
plt.figure()
pltname = 'phantom_TR{}_{}'.format(TR, correctionname)
phantom[TR].plot.bar()
plt.title(pltname)
plt.savefig(pltname+'.png')
plt.figure()
pltname = 'brain_TR{}_{}'.format(TR, correctionname)
brain[TR].plot.bar()
plt.title(pltname)
plt.savefig(pltname+'.png')

