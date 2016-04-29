from __future__ import division
import collections, numpy, glob, datetime, pandas
from numpy import radians
import matplotlib.pyplot as plt
from os.path import join, isfile
from niprov import Context
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.model_pipeline import modelForDate
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.regional import averageByRegion
from pylabs.alignment.phantom import align, applyXformAndSave
from pylabs.qt1.simplefitting import fitT1
provenance = Context()

## settings
fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_disc')
subject = 'phantom_qT1_20140723'
subjectdir = join(projectdir,subject)
alignmentTarget = join(projectdir, 'phantom_flipangle_alignment_target.nii')
vialAtlas = join(projectdir,'phantom_alignment_target_round_mask.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]

import pylabs.qt1.corrections.dummy as correct

## Get brain sample:
#from pylabs.qt1.brainsampling import sample

xform = {}
adata = {}
correction = {}
phantom = {}
brain = {}
TR = 11.

phantom[TR] = pandas.DataFrame(index=vialOrder, 
                columns=['model','fit','corr'], dtype=float)

## par2nii
niftiDict = convertSubjectParfiles(subject, subjectdir)

raise ValueError
## model_pipeline
phantom[TR]['model'] = modelForDate(date, 'slu')[vialOrder]

## Gather files & align
alphafilter = '*{}*1.nii'.format(int(TR))
alphafiles = sorted(glob.glob(join(subjectdir,'anat',alphafilter)))
assert TR == provenance.get(forFile=alphafiles[0]).provenance['repetition-time']
if not xform:
    xform[TR] = align(alphafiles[0], alignmentTarget, delta=10)

## b1 map
b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))
alignedB1file = b1file.replace('.nii', '_coreg.nii')
if not xform:
    applyXformAndSave(xform[TR], b1file, alignmentTarget, 
        newfile=alignedB1file, provenance=provenance)
print('Sampling B1')
B1 = averageByRegion(alignedB1file, vialAtlas).loc[vialOrder]

## transform and sample flip-angle files
adata[TR] = pandas.DataFrame()
for alphafile in alphafiles:
    alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
    if not xform:
        applyXformAndSave(xform[TR], alphafile, alignmentTarget, 
            newfile=alignedAlphafile, provenance=provenance)
    print('Sampling signal for one flip angle..')
    vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
    alpha = provenance.get(forFile=alignedAlphafile).provenance['flip-angle']
    adata[TR][alpha] = vialAverages
adata[TR] = adata[TR].loc[vialOrder]
alphas = adata[TR].columns.values.tolist()

A = radians(alphas)

## Initial fit on vials
phantom[TR]['fit'] = fitT1(adata[TR], A, B1, TR)
## determine Correction
correction[TR] = correct.create(adata[TR], A, B1, phantom[TR]['model'], 
                                phantom[TR]['fit'], TR)
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
phantom[TR].plot.bar()
plt.savefig('phantom_TR{}.png'.format(TR))
plt.figure()
brain[TR].plot.bar()
plt.savefig('brain_TR{}.png'.format(TR))

