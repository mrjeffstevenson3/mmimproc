from __future__ import division
import collections, numpy, glob, datetime, pandas, itertools
from numpy import cos, sin, exp, tan, radians, power
import matplotlib.pyplot as plt
from os.path import join, isfile, basename
from niprov import Context
from pylabs.utils.paths import getnetworkdataroot
from pylabs.conversion.helpers import convertSubjectParfiles
from pylabs.qt1.fitting import spgrformula
from pylabs.qt1.model_pipeline import modelForDate
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.qt1.formulas import jloss
from pylabs.regional import averageByRegion
from pylabs.alignment.phantom import align, applyXformAndSave
from pylabs.qt1.simplefitting import fitT1
from pylabs.stats import ScaledPolyfit
provenance = Context()
provget = lambda  f: provenance.get(forFile=f).provenance
singletr = lambda tr: tr[0] if isinstance(tr, list) else tr

## settings
fs = getnetworkdataroot()
projectdir = join(fs, 'phantom_qT1_disc')
alignmentTarget = join(projectdir, 'phantom_flipangle_alignment_target.nii')
vialAtlas = join(projectdir,'phantom_alignment_target_round_mask.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]
scanner = 'disc'

import pylabs.qt1.corrections.polycurvet1 as correct
correctionname = correct.__name__.split('.')[-1]

xform = {}
adata = {}
correction = {}
phantom = {}
brain = {}

TR = 11.
subjectdirs = glob.glob(join(projectdir, 'phantom_qT1_*'))
for subjectdir in subjectdirs:
    subject = basename(subjectdir)
    date = datetime.datetime.strptime(subject.split('_')[2], '%Y%m%d').date()
    phantom[date] = pandas.DataFrame(index=vialOrder, 
                    columns=['model','fit'], dtype=float)

    ## par2nii
    niftiDict = convertSubjectParfiles(subject, subjectdir)

    ## Gather files & align
    alphafilter = '*tr_{}*1.nii'.format(int(TR))
    alphafiles = sorted(glob.glob(join(subjectdir,'anat',alphafilter)))
    if not alphafiles:
        print('\n\n\nNO SPGRS TR11 FOUND FOR {}\n\n\n'.format(subject))
        continue
    assert TR == singletr(provget(alphafiles[0])['repetition-time'])
    if not xform:
        xform[date] = align(alphafiles[0], alignmentTarget, delta=10)

    ## model_pipeline
    phantom[date]['model'] = modelForDate(date, scanner)[vialOrder]

    ## b1 map
    b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))
    alignedB1file = b1file.replace('.nii', '_coreg.nii')
    if not xform:
        applyXformAndSave(xform[date], b1file, alignmentTarget, 
            newfile=alignedB1file, provenance=provenance)
    print('Sampling B1')
    B1 = averageByRegion(alignedB1file, vialAtlas).loc[vialOrder]

    ## transform and sample flip-angle files
    adata[date] = pandas.DataFrame()
    for alphafile in alphafiles:
        alignedAlphafile = alphafile.replace('.nii', '_coreg.nii')
        if not xform:
            applyXformAndSave(xform[date], alphafile, alignmentTarget, 
                newfile=alignedAlphafile, provenance=provenance)
        print('Sampling signal for one flip angle..')
        vialAverages = averageByRegion(alignedAlphafile, vialAtlas)
        alpha = provenance.get(forFile=alignedAlphafile).provenance['flip-angle']
        adata[date][alpha] = vialAverages
    adata[date] = adata[date].loc[vialOrder]
    alphas = adata[date].columns.values.tolist()

    A = radians(alphas)

    ## Initial fit on vials
    phantom[date]['fit'] = fitT1(adata[date], A, B1, TR)
    ## determine Correction
    correction[date] = correct.create(adata[date], A, B1, phantom[date]['model'], 
                                    phantom[date]['fit'], TR)

    try:
        if isinstance(correction[date][0], str):
            correctionname = correction[date][0]
    except Exception as e:
        pass
    ## apply Correction fit on vials
    phantom[date]['corr'] = correct.apply(correction[date], adata[date], A, B1)
    ## apply Correction fit on brain sample
    brain[date] = pandas.DataFrame(index=sample.index, 
                    columns=['fit','corr'], dtype=float)
    brainAngles = list(sample.columns.values[-3:])
    brain[date]['fit'] = sample['fit']
    brain[date]['corr'] = correct.apply(correction[date], sample[brainAngles], 
                                        radians(brainAngles), sample['B1'])

    ## plotting
    plt.figure()
    pltname = 'phantom_TR{}_{}'.format(TR, correctionname)
    phantom[date].plot.bar()
    plt.title(pltname)
    plt.savefig(pltname+'.png')
    plt.figure()
    pltname = 'brain_TR{}_{}'.format(TR, correctionname)
    brain[date].plot.bar()
    plt.title(pltname)
    plt.savefig(pltname+'.png')

