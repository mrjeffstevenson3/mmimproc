from __future__ import print_function
import os, fnmatch, glob, collections
from os.path import join
import numpy
from nipype.interfaces import fsl
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fitCombinedFile

# all_ti_mag_b1corr.nii.gz

#loop through timepoints, pick a method and parameter,
sessions = glob.glob(join(getlocaldataroot(),'phantom_qT1_disc','phantom*'))
sessionsByType = collections.defaultdict(list)
for session in sessions:
    scanFolders = glob.glob(join(session,'fitted*'))
    for scanFolder in scanFolders:
        files = glob.glob(join(scanFolder,'*_mag_b1corr.nii.gz'))
        if len(files) > 0:
            scantype = os.path.basename(scanFolder).split('_')[1]
            sessionsByType[scantype].append(files[0])
for scantype in sessionsByType.keys():
    msg = '{0} {1} sessions'
    print(msg.format(scantype.ljust(25), len(sessionsByType[scantype])))

## FITTING

# loop over scantypes here..
sampleScantype = 'seir'
sessions = sessionsByType[sampleScantype]
for s, session in enumerate(sessions):
    print('Fitting session {0} of {1}..'.format(s, len(sessions)))
    try:
        t1image = t1fitCombinedFile(session, [500, 1500, 3000], scantype='IR')
    except ValueError:
        print("Don't have all images for this session. Continuing.")


## ATLASSING

#atlasfile = 'all_seir_t1map_mni_mask_1slice.nii.gz'
#vialAtlas = join('data','phantoms',atlasfile)
#labels = atlaslabels(atlasfile)
#nvials = len(labels)
#ntimepoints = len(scans)

## get region/vial-wise data for each timepoint
#vialTimeseries = numpy.zeros((ntimepoints, nvials))
#for t, phantom in enumerate(scans):
#    print('Examining scan {0} of {1}'.format(t,ntimepoints))
#    regionalStats = statsByRegion(phantom, vialAtlas)
#    vialTimeseries[t, :] = regionalStats['average']

## plot development over time for each vial
#plt.plot(numpy.arange(ntimepoints), vialTimeseries) 
#plt.show()

