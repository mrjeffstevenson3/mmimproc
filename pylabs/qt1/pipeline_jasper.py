from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle, sys
from os.path import join
from collections import defaultdict
import numpy
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit

skipExisting = True

vialCoords = numpy.array([[57,159],[112,164],[30,130],[88,134],[143,139],[61,103],[116,108],[37,71],[93,77],[149,83],[68,47],[124,54]])

### FITTING

rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
imageDictFile = join(rootdir,'phantom_disc_dict_dec3.txt')
with open(imageDictFile) as dfile:
    images = cPickle.load(dfile)

t1fitTimeseries = defaultdict(dict) # (method, TR, run) : {date: t1file}

from multiprocessing import Pool
pool = Pool(12)
async = True
for key, run in images.items():
    date = key[0]
    method = key[1]
    TR = key[2]
    runIndex = key[3]

    if 'b1map' in method:
        continue

    msg = 'Working on session: {0} method: {1} TR: {2} Run: {3}'
    print(msg.format(date, method.upper(), TR, runIndex))

    run = [f for f in run if f[1]!='mask']
    files, X = zip(*sorted(run, key=lambda s: s[1]))
    scottybasedir = '/media/DiskArray/shared_data/js'
    jvdbbasedir = '/diskArray/mirror/js'
    files = [f.replace(scottybasedir, jvdbbasedir) for f in files]
    sessiondir = os.sep.join(files[0].split(os.sep)[:-2])
    maskfname = 'orig_seir_ti_3000_tr_4000_mag_1slmni_1_mask.nii'
    maskfile = join(sessiondir,'fitted_seir_qT1',maskfname)
    b1file = join(sessiondir,'B1map_qT1','b1map_phase_1.nii')
    TRstring = str(TR).replace('.','p')
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

    kwargs = {}
    if os.path.isfile(maskfile):
        kwargs['maskfile'] = maskfile
    if os.path.isfile(b1file):
        kwargs['b1file'] = b1file
    if 'SPGR' in method.upper():
        kwargs['scantype'] = 'SPGR'
        kwargs['TR'] = TR
    kwargs['t1filename'] = t1filepath
    #kwargs['voiCoords'] = vialCoords
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



