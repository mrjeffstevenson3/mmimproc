from os.path import join
import collections, itertools, os
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fit
from multiprocessing import Pool
pool = Pool(11)
## Evaluate which flip angles are required to do an adequate SPGR QT1

fs = getlocaldataroot()
projectdir = join(fs, 'tadpole', 'tadpole')
subj = 'sub-901'
outdir = join(projectdir, subj, 'anat')
t1filetem = join(outdir,'t1_spgr_{0}{1}.nii.gz')

async = True

b1dir = '/diskArray/mirror/js/tadpole/tadpole/TADPOLE901/B1map_qT1'
spgrdir = '/diskArray/mirror/js/tadpole/tadpole/TADPOLE901/fitted_qT1_spgr'
b1file = join(b1dir, 'TADPOLE901_b1map_phase_reg2spgr_s6.nii.gz')
spgrtem = join(spgrdir, 'spgr_{0:0>2}_mag_01_brain.nii.gz')
maskfile = join(spgrdir, 'spgr_07_mag_01_brain_mask.nii.gz')

allAngles = [7,10,15,20,30]
xcombs = list(itertools.combinations(allAngles, 3))
xcombs.insert(0, allAngles) # Add all-angles fit

b1corrtags = {True:'_b1corr', False:'_b1unco'}

for xcomb in xcombs:
    for b1corr in [True, False]:

        kwargs = {}
        kwargs['scantype'] = 'SPGR'
        kwargs['TR'] = 14.
        kwargs['maskfile'] = maskfile
        if b1corr:
            kwargs['b1file'] = b1file
        xcombStr = '-'.join([str(x) for x in xcomb])
        kwargs['t1filename'] = t1filetem.format(xcombStr, b1corrtags[b1corr])

        files = [spgrtem.format(x) for x in xcomb]

        print('Working on '+kwargs['t1filename'])
        if async:
            kwargs['mute'] = True
            pool.apply_async(t1fit, [files, xcomb], kwargs)
        else:
            try:
                t1fit(files, xcomb, **kwargs)
            except Exception as ex:
                print('\n--> Error during fitting: ', ex)





