from __future__ import print_function
import os, glob
from os.path import join
from mmimproc.utils.paths import getlocaldataroot
from mmimproc.qt1.fitting import t1fit
from multiprocessing import Pool


async = False
TR = 14.
pool = Pool(10)
rootdir = join(getlocaldataroot(),'tadpole')

for subjectdir in glob.glob(join(rootdir, 'TADPOLE901')):
    subject = os.path.basename(subjectdir)
    files = glob.glob(join(subjectdir,'fitted_qT1_spgr','*brain.nii.gz'))
22    files = sorted(files)
    assert len(files) == 5
    X = [7,10,15,20,30]
    maskfile = files[0].replace('brain.nii.gz','brain_mask.nii.gz')
    b1file = join(subjectdir,'B1map_qT1',
        '{0}_b1map_phase_reg2spgr_s6.nii.gz'.format(subject))
    outfile = join(subjectdir,'T1_{0}_b1corr.nii.gz'.format(subject))
    print(files)
    print(b1file)
    kwargs = {}
    kwargs['scantype'] = 'SPGR'
    kwargs['TR'] = TR
    kwargs['t1filename'] = outfile
    if os.path.isfile(b1file):
        kwargs['b1file'] = b1file
    else:
        print('No B1 file for subject {0}'.format(subject))
    if os.path.isfile(maskfile):
        kwargs['maskfile'] = maskfile
    if async:
        kwargs['mute'] = True
        pool.apply_async(t1fit, [files, X], kwargs)
    else:
        try:
            t1fit(files, X, **kwargs)
        except Exception as ex:
            print('\n--> Error during fitting: ', ex)


