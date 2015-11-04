from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle, sys
from os.path import join
from collections import defaultdict
import numpy
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit

skipExisting = True

### FITTING

rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
imageDictFile = join(rootdir,'conv_scans_dict.txt')
with open(imageDictFile) as dfile:
    images = cPickle.load(dfile)

## Reformat multi-level dict into dict keyed by tuples
runs = {}
for dateString in images.keys():
    for method in images[dateString].keys():
        for TR in images[dateString][method]:
            for imageTuple in images[dateString][method][TR]:
                runIndex = int(imageTuple[0].split('_')[-1])
                runKey = (dateString, method, TR, runIndex)
                if not runKey in runs:
                    runs[runKey] = []
                runs[runKey].append(imageTuple)

t1fitTimeseries = defaultdict(dict) # (method, TR, run) : {date: t1file}

for key, run in runs.items():
    dateString = key[0]
    date = datetime.datetime.strptime(dateString, '%Y%m%d').date()
    method = key[1]
    TR = key[2]
    runIndex = key[3]

    if method == 'b1map':
        continue

    msg = 'Working on session: {0} method: {1} TR: {2} Run: {3}'
    print(msg.format(date, method.upper(), TR, runIndex))

    datadir = join(rootdir,
        'phantom_qT1_{0}'.format(dateString),
        'fitted_{0}_qT1'.format(method))
    outdir = join(rootdir, 'T1_{0}_TR{1}'.format(method, TR))
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    fnameTemplate = 'T1_{0}_TR{1}_{2}_{3}.nii.gz'
    fname = fnameTemplate.format(method, TR, dateString, runIndex)
    t1filepath = join(outdir, fname)

    if skipExisting and os.path.isfile(t1filepath):
        print('--> File exists, skipping scan.'.format(len(run)))
        if not date in t1fitTimeseries[(method, TR)]:
            t1fitTimeseries[(method, TR)][date] = t1filepath

    if len(run) < 3:
        print('--> Skipping scan, only {0} files'.format(len(run)))
        continue
    files, X = zip(*sorted(run, key=lambda s: s[1]))
    files = [join(datadir, f+'.nii') for f in files]
    try:
        if method.upper() == 'SPGR':
            t1fit(files, X, t1filename=t1filepath, scantype='SPGR', TR=TR)
        else:
            t1fit(files, X, t1filename=t1filepath)
    except Exception as ex:
        print('\n--> Error during fitting: ', ex)
    else:
        if not date in t1fitTimeseries[(method, TR)]:
            t1fitTimeseries[(method, TR)][date] = t1filepath
        else:
            print('--> Already have a run fitted for this date, '+
                'this image not passed on down pipeline.')



#### ATLASSING

atlasfile = 't1_phantom_mask_course.nii.gz'
vialAtlas = join('data','atlases',atlasfile)
labels = atlaslabels(atlasfile)
nvials = len(labels)

for key, timeseries in t1fitTimeseries.items():
    method = key[0]
    TR = key[1]

    plotname = '{0}_{1}.png'.format(method, TR)

    dates = sorted(timeseries.keys())
    scansInOrder = [timeseries[d] for d in dates]
    ntimepoints = len(dates)
    vialTimeseries = numpy.zeros((ntimepoints, nvials))
    for t, scan in enumerate(scansInOrder):
        print('Sampling vials for scan {0} of {1}'.format(t,ntimepoints))
        regionalStats = statsByRegion(scan, vialAtlas)
        vialTimeseries[t, :] = regionalStats['average']

    # Get rid of background
    vialTimeseries = numpy.delete(vialTimeseries, 0, 1)
    del labels[0]

    # plot development over time for each vial
    lines = plt.plot(dates, vialTimeseries) 
    plt.legend(lines, labels, loc=8)
    plt.savefig(plotname)

