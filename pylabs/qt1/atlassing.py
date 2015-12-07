from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle, sys
from os.path import join
import numpy
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot
import pylabs.qt1.expected


def findfile(rootdir, method, TR, date, runIndex, b1corr, coreg):
    b1corrtag = {True:'_b1corr',False:''}
    trstr = str(TR).replace('.','p')
    dirvars = (method, trstr)
    if coreg:
        dirtem = 'T1_{0}_TR{1}_reg2723_dec4{2}'
        dirvars += (b1corrtag[b1corr],)
    else:
        dirtem = 'T1_{0}_TR{1}'
    dirpath = join(rootdir, dirtem.format(*dirvars))
    filetem = 'T1_{0}_TR{1}_{2}_{3}{4}.nii.gz'
    filevars = (method, trstr, date, runIndex, b1corrtag[b1corr])
    filepath = join(dirpath, filetem.format(*filevars))
    if not os.path.isfile(filepath):
        return None
    return filepath


### Gather data by vial

coreg = True # Look at coregistered file or non-coregistered files
rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
atlasfname = 'T1_seir_mag_TR4000_2014-07-23_mask.nii.gz'
atlasfpath = join(rootdir,atlasfname)
imageDictFile = join(rootdir,'phantom_disc_dict_dec3.txt')
with open(imageDictFile) as dfile:
    images = cPickle.load(dfile)

vialdata = {}
ndictentries = len(images)*2

print('Method, TR, B1 corr, date                        Found file')
for key, run in images.items():
    date = key[0]
    method = key[1]
    TR = key[2]
    runIndex = key[3]

    for b1corr in [True,False]:
        filepath = findfile(rootdir, method, TR, date, runIndex, b1corr, coreg)
        newkey = (method, TR, b1corr, date)
        print('{0: <65}\t{1}'.format(newkey, (filepath is not None)))
        if filepath is None:
            continue
        if newkey in vialdata:
            print(' --> Already have a run for this key.')
        vialdata[newkey] = statsByRegion(filepath, atlasfpath)

print('\nVialdata for {0} images.\n'.format(len(vialdata.keys())))


labels = atlaslabels(atlasfname)
vizlabels = labels[1:] # remove label for background
nvials = len(labels)

## Get expected data
expectedByDate = pylabs.qt1.expected.readfromfile()
datesWithTemps = expectedByDate.keys()

## Start plotting

plotsubdir = 'coreg'
if not coreg:
    plotsubdir = 'nocoreg'
plotdir = join(rootdir,'plots',plotsubdir)
b1corrtag = {True:'b1corr',False:'notb1c'}
if not os.path.isdir(plotdir):
    os.makedirs(plotdir)

def plotT1Timeseries(dates, data, labels, title, dtype=None):
    ylimPresets = {'t1':[0,2500],'absdiff':[-500,500],'reldiff':[-50,50]}
    plotfpath = join(plotdir,'timeseries_{0}.png'.format(title))
    plt.figure()
    lines = plt.plot(dates, data) 
    axes = plt.gca()
    if dtype in ylimPresets:
        axes.set_ylim(ylimPresets[dtype])
    plt.legend(lines, labels, loc=8)
    plt.savefig(plotfpath)

methods = set([k[:3] for k in vialdata.keys()])
for method in methods:
    methodstr = '{0}_{1}_{2}'.format(method[0], method[1], b1corrtag[method[2]])
    print(methodstr)
    thisMethodKeys = [k for k in vialdata.keys() if k[:3] == method]
    dates = sorted([k[3] for k in thisMethodKeys if k[3] in datesWithTemps])
    regStatsInOrder = [vialdata[method+(d,)]['average'] for d in dates]
    obsVialtc = numpy.array(regStatsInOrder)

    ## Observed data
    obsVialtc = numpy.delete(obsVialtc, 0, 1) # Get rid of background
    plotT1Timeseries(dates, obsVialtc, vizlabels, methodstr, dtype='t1')

    ## Expected plot for same dates
    expVialtc = numpy.array([expectedByDate[d] for d in dates])
    plotT1Timeseries(dates, expVialtc, vizlabels, methodstr+'_expected', dtype='t1')

    ## Difference
    diffVialtc = expVialtc - obsVialtc
    plotT1Timeseries(dates, diffVialtc, vizlabels, methodstr+'_diff', 
        dtype='absdiff')

    ## Relative Difference
    reldiffVialtc = ((expVialtc - obsVialtc)/expVialtc)*100
    plotT1Timeseries(dates, reldiffVialtc, vizlabels, methodstr+'_reldiff',     
        dtype='reldiff')

    


