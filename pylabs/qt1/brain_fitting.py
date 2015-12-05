from __future__ import print_function
import os, glob
from os.path import join
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit

async = False
TR = 11.
rootdir = join(getlocaldataroot(),'self_control','hbm_group_data','qT1')

for subjectdir in glob.glob(join(rootdir, 'scs*')):

    files = glob.glob(join(subjectdir,'fitted_qT1_spgr','*brain.nii.gz'))
    files = sorted(files)
    assert len(files) == 3
    X = [2,10,20]
    maskfile = files[0].replace('brain.nii.gz','brain_mask.nii.gz')
    subject = os.path.basename(subjectdir)
    outfile = join(subjectdir,'T1_{0}.nii.gz'.format(subject))

    kwargs = {}
    kwargs['scantype'] = 'SPGR'
    kwargs['TR'] = TR
    kwargs['t1filename'] = outfile
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


