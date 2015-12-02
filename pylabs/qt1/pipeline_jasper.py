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

#vialCoords = numpy.array([[64,175,90],[127,174,90],[33,143,90],[95,144,90],
#[156,143,90],[64,113,90],[126,114,90],[33,82,90],[96,82,90],[157,82,90],
#[65,51,90],[127,52,90]])

### FITTING

rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
imageDictFile = join(rootdir,'phantom_disc_dict_complete_dec1_2015.txt')
with open(imageDictFile) as dfile:
    images = cPickle.load(dfile)


t1fitTimeseries = defaultdict(dict) # (method, TR, run) : {date: t1file}

from multiprocessing import Pool
pool = Pool(10)
async = False
for key, run in images.items():
    date = key[0]
    method = key[1]
    TR = key[2]
    runIndex = key[3]

    if method == 'b1map':
        continue

    msg = 'Working on session: {0} method: {1} TR: {2} Run: {3}'
    print(msg.format(date, method.upper(), TR, runIndex))

    TRstring = str(TR).replace('.','-')
    outdir = join(rootdir, 'T1_{0}_TR{1}'.format(method, TRstring))
    fnameTemplate = 'T1_{0}_TR{1}_{2}_{3}.nii.gz'
    fname = fnameTemplate.format(method, TRstring, 
        str(date), runIndex)
    t1filepath = join(outdir, fname)

    if len(run) < 3:
        print('--> Skipping scan, only {0} files'.format(len(run)))
        continue

    if skipExisting and os.path.isfile(t1filepath):
        print('--> File exists, skipping scan.'.format(len(run)))
        if not date in t1fitTimeseries[(method, TR)]:
            t1fitTimeseries[(method, TR)][date] = t1filepath
        continue

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    files, X = zip(*sorted(run, key=lambda s: s[1]))
    scottybasedir = '/media/DiskArray/shared_data/js'
    jvdbbasedir = '/diskArray/mirror/js'
    files = [f.replace(scottybasedir, jvdbbasedir) for f in files]
    kwargs = {}
    sessiondir = os.sep.join(files[0].split(os.sep)[:-2])
    maskfile = join(sessiondir,'B1map_qT1','b1map_mag_mask_1.nii')
    b1file = join(sessiondir,'B1map_qT1','b1map_mag_1.nii')
    if os.path.isfile(maskfile):
        kwargs['maskfile'] = maskfile
    if os.path.isfile(b1file):
        kwargs['b1file'] = b1file
        t1filepath = t1filepath.replace('.nii.gz', '_b1corr.nii.gz')
    if method.upper() == 'SPGR':
        kwargs['scantype'] = 'SPGR'
        kwargs['TR'] = TR
    kwargs['t1filename'] = t1filepath
    if async:
        kwargs['mute'] = True
        pool.apply_async(t1fit, [files, X], kwargs)
    else:
        try:
            t1fit(files, X, **kwargs)
        except Exception as ex:
            print('\n--> Error during fitting: ', ex)
        else:
            if not date in t1fitTimeseries[(method, TR)]:
                t1fitTimeseries[(method, TR)][date] = t1filepath
            else:
                print('--> Already have a run fitted for this date, '+
                    'this image not passed on down pipeline.')
pool.close()
pool.join()

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

