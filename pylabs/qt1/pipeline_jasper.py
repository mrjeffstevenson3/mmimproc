from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle
from os.path import join
from collections import defaultdict
import numpy
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit

### FITTING

datadir = join(getlocaldataroot(),'phantom_qT1_disc')
imageDictFile = join(datadir,'conv_scans_dict.txt')
with open(imageDictFile) as dfile:
    images = cPickle.load(dfile)
t1fitImages = defaultdict(lambda: defaultdict(dict)) # method, TR, date
for sessionString in images.keys():
    date = datetime.datetime.strptime(sessionString, '%Y%m%d').date()
    sessiondir = subdir = join(datadir,'phantom_qT1_{0}'.format(sessionString))
    for method in images[sessionString].keys():
        if method == 'b1map':
            continue
        subdir = join(sessiondir,'fitted_{0}_qT1'.format(method))
        for TR in images[sessionString][method]:
            series = images[sessionString][method][TR]
            if len(series) < 3:
                continue
            files, X = zip(*sorted(series, key=lambda s: s[1]))
            files = [join(subdir, f+'.nii') for f in files]
            outdir = join(datadir, 'T1_{0}_TR{1}'.format(method, TR))
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
            fname = 'T1_{0}_TR{1}_{2}'.format(method, TR, sessionString)
            t1filepath = join(outdir, fname)
            if method.upper() == 'SPGR':
                t1fit(files, X, t1filename=t1filepath, scantype='SPGR', TR=TR)
            else:
                t1fit(files, X, t1filename=t1filepath)
            t1fitImages[method][TR][date] = t1filepath


### ATLASSING

atlasfile = 't1_phantom_mask_course.nii.gz'
vialAtlas = join('data','atlases',atlasfile)
labels = atlaslabels(atlasfile)
nvials = len(labels)

for method in t1fitImages.keys():
    for TR in t1fitImages[method].keys():
        plotname = '{0}_{1}.png'.format(method, TR)
        sessions = t1fitImages[method][TR]

        dates = sorted(sessions.keys())
        scansInOrder = [sessions[d] for d in dates]
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

