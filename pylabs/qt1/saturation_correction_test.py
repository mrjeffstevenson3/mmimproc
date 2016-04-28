from __future__ import division
import collections, numpy, glob, datetime, pandas, itertools
from numpy import cos, sin, exp, tan, radians, power
import matplotlib.pyplot as plt
from os.path import join, isfile
from niprov import Context
from pylabs.utils.paths import getlocaldataroot
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

## settings
fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subjectsByTR = {14.0:datetime.date(2016, 3, 2),
                28.0:datetime.date(2016, 3, 2), 
                56.0:datetime.date(2016, 3, 11)}
alignmentTarget = join(projectdir, 'phantom_flipangle_alignment_target.nii')
vialAtlas = join(projectdir,'phantom_alignment_target_round_mask.nii.gz')
usedVials = range(7, 18+1)
vialOrder = [str(v) for v in vialNumbersByAscendingT1 if v in usedVials]

import pylabs.qt1.corrections.dummy as dummy
correctT1 = dummy.correct

TRs = subjectsByTR.keys()
xform = {}
xform = {14.0: {'rxy': 0, 'tx': 0, 'ty': 0}, 
         28.0: {'rxy': -3, 'tx': 1, 'ty': 0}}
adata = {}
overview = {}
expected = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
fit = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
corrected = pandas.DataFrame(columns=TRs, index=vialOrder, dtype=float)
for TR in TRs:
    if TR ==56:
        continue
    date = subjectsByTR[TR]
    subject = 'sub-phant'+str(date)
    subjectdir = join(projectdir, subject)

    ## par2nii
    #niftiDict = convertSubjectParfiles(subject, subjectdir)

    ## model_pipeline
    expected[TR] = modelForDate(date, 'slu')[vialOrder]

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

    ## Initial fit
    fit[TR] = fitT1(adata[TR], A, B1, TR)


    corrected[TR] = correctT1(adata[TR], A, B1, expected[TR], fit[TR], TR)

    ## plotting
    overview[TR] = pandas.DataFrame({'model':expected[TR], 'fit':fit[TR], 'corrected':corrected[TR]})
    plt.figure()
    overview[TR].plot.bar()
    plt.savefig('correction_TR{}.png'.format(TR))

