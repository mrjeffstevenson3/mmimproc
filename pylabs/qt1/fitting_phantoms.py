from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle, sys, shutil
from os.path import join
from collections import defaultdict
import numpy
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit
from pylabs.qt1.naming import qt1filepath


### FITTING
def fitPhantoms(images, projectdir, dirstruct='BIDS', async=False, skipExisting = False, X=None):
    #from multiprocessing import Pool
    #pool = Pool(12)
    outfiles = []
    for key, run in images.items():
        for b1corr in [True, False]:
            image = {
                'date': key[0],
                'method': key[1],
                'TR': key[2],
                'run': key[3],
                'b1corr': b1corr,
                'b1tag': {True:'_b1corr', False:''}[b1corr],
                'TRtag': str(key[2]).replace('.','p')
            }

            if 'b1map' in image['method']:
                continue

            run = [f for f in run if f[1]!='mask']
            files, allx = zip(*sorted(run, key=lambda s: s[1]))
            if X is not None:
                files = [f for f in files if allx[files.index(f)] in X]
            else:
                X = allx
            image['X'] = '-'.join([format(x,'02') for x in X])

            msg = 'Fitting: {date} method: {method} TR: {TR} Run: {run} X: {X}'
            print(msg.format(**image))

            scottybasedir = '/media/DiskArray/shared_data/js'
            jvdbbasedir = '/diskArray/mirror/js'
            files = [f.replace(scottybasedir, jvdbbasedir) for f in files]
            sessiondir = os.sep.join(files[0].split(os.sep)[:-2])
            maskfname = 'orig_seir_ti_3000_tr_4000_mag_1slmni_1_mask.nii'
            maskfile = join(sessiondir,'fitted_seir_qT1',maskfname)
            #b1file = join(sessiondir,'B1map_qT1','b1map_phase_1.nii')
            b1key = [k for k in images.keys() if k[1] == 'b1map_phase' and
                k[0] == image['date']][0]
            b1file = images[b1key][0][0]

            if len(run) < 3:
                print('--> Skipping scan, only {0} files'.format(len(run)))
                continue

            t1filepath = qt1filepath(image, projectdir, dirstruct)
            if not os.path.isdir(os.path.dirname(t1filepath)):
                shutil.makedirs(os.path.dirname(t1filepath))

            if skipExisting and os.path.isfile(t1filepath):
                print('--> File exists, skipping scan.'.format(len(run)))
                outfiles.append(image)
                continue

            kwargs = {}
            if os.path.isfile(maskfile):
                kwargs['maskfile'] = maskfile
            if b1corr:
                kwargs['b1file'] = b1file
            if 'SPGR' in image['method'].upper():
                kwargs['scantype'] = 'SPGR'
                kwargs['TR'] = image['TR']
            kwargs['t1filename'] = t1filepath
            if async:
                kwargs['mute'] = True
                #pool.apply_async(t1fit, [files, X], kwargs)
            else:
                try:
                    t1fit(files, X, **kwargs)
                    outfiles.append(image)
                except Exception as ex:
                    print('\n--> Error during fitting: ', ex)
    #pool.close()
    #pool.join()
    return outfiles

if __name__ == '__main__':
    async = False
    skipExisting = True
    rootdir = join(getlocaldataroot(),'phantom_qT1_disc')
    imageDictFile = join(rootdir,'phantom_disc_dict_dec3.txt')
    with open(imageDictFile) as dfile:
        images = cPickle.load(dfile)
    fitPhantoms(images, projectdir=rootdir, 
        async=async, skipExisting=skipExisting, dirstruct='legacy')




