from __future__ import print_function
import os, fnmatch, glob, datetime, sys
from os.path import join
import numpy
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit

skipExisting = True

### FITTING

rootdir = join(getlocaldataroot(),'phantom_qT1_disc')


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
        continue

    if len(run) < 3:
        print('--> Skipping scan, only {0} files'.format(len(run)))
        continue
    files, X = zip(*sorted(run, key=lambda s: s[1]))
    files = [join(datadir, f+'.nii') for f in files]
    try:
        if method.upper() == 'SPGR':
            t1fit(files, X, t1filename=t1filepath, voiCoords=vialCoords,
                scantype='SPGR', TR=TR)
        else:
            t1fit(files, X, t1filename=t1filepath, voiCoords=vialCoords)
    except Exception as ex:
        print('\n--> Error during fitting: ', ex)
    else:
        if not date in t1fitTimeseries[(method, TR)]:
            t1fitTimeseries[(method, TR)][date] = t1filepath
        else:
            print('--> Already have a run fitted for this date, '+
                'this image not passed on down pipeline.')

