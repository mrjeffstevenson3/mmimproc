from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle, sys
from os.path import join
import numpy
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot


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


### ATLASSING

coreg = True
rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
atlasfname = 'T1_seir_mag_TR4000_2014-07-23_mask.nii.gz'
atlasfpath = join(rootdir,atlasfname)
imageDictFile = join(rootdir,'phantom_disc_dict_dec3.txt')
with open(imageDictFile) as dfile:
    images = cPickle.load(dfile)

vialdata = {}
ndictentries = len(images)*2

for key, run in images.items():
    date = key[0]
    method = key[1]
    TR = key[2]
    runIndex = key[3]

    for b1corr in [True,False]:
        # check if we have file
        filepath = findfile(rootdir, method, TR, date, runIndex, b1corr, coreg)
        newkey = (method, TR, b1corr, date)
        print('{0: <65}\t{1}'.format(newkey, (filepath is not None)))
        if filepath is None:
            continue
        if newkey in vialdata:
            print(' --> Already have a run for this key.')
        vialdata[newkey] = statsByRegion(filepath, atlasfpath)

print('\nVialdata for {0} images.\n'.format(len(vialdata.keys())))



#atlasfile = 't1_phantom_mask_course.nii.gz'
#vialAtlas = join('data','atlases',atlasfile)
#labels = atlaslabels(atlasfile)
#nvials = len(labels)

#for key, timeseries in t1fitTimeseries.items():
#    method = key[0]
#    TR = key[1]

#    plotname = '{0}_{1}.png'.format(method, TR)

#    dates = sorted(timeseries.keys())
#    scansInOrder = [timeseries[d] for d in dates]
#    ntimepoints = len(dates)
#    vialTimeseries = numpy.zeros((ntimepoints, nvials))
#    for t, scan in enumerate(scansInOrder):
#        print('Sampling vials for scan {0} of {1}'.format(t,ntimepoints))
#        regionalStats = statsByRegion(scan, vialAtlas)
#        vialTimeseries[t, :] = regionalStats['average']

#    # Get rid of background
#    vialTimeseries = numpy.delete(vialTimeseries, 0, 1)
#    del labels[0]

#    # plot development over time for each vial
#    lines = plt.plot(dates, vialTimeseries) 
#    plt.legend(lines, labels, loc=8)
#    plt.savefig(plotname)
