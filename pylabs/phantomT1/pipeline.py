from __future__ import print_function
import os, fnmatch, glob, collections
from os.path import join
import numpy
from nipype.interfaces import fsl
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot

#loop through timepoints, pick a method and parameter,
sessions = glob.glob(join(getlocaldataroot(),'phantom_qT1_disc','phantom*'))
scansByType = collections.defaultdict(list)
for session in sessions:
    for root, dirnames, filenames in os.walk(session):
        for filename in fnmatch.filter(filenames, '*.nii'):
            filepath = join(root, filename)
            scantype = filename.split('.')[0]
            scansByType[scantype].append(filepath)
for scantype in scansByType.keys():
    print('{0} {1}'.format(scantype.ljust(25), len(scansByType[scantype])))

atlasfile = 'all_seir_t1map_mni_mask_1slice.nii.gz'
vialAtlas = join('data','phantoms',atlasfile)
labels = atlaslabels(atlasfile)
nvials = len(labels)
# loop over scantypes here..
sampleScantype = 'orig_seir_ti_3000_1'
scans = scansByType[sampleScantype]
ntimepoints = len(scans)

# get region/vial-wise data for each timepoint
vialTimeseries = numpy.zeros((ntimepoints, nvials))
for t, phantom in enumerate(scans):
    print('Examining scan {0} of {1}'.format(t,ntimepoints))
    regionalStats = statsByRegion(phantom, vialAtlas)
    vialTimeseries[t, :] = regionalStats['average']

# plot development over time for each vial
plt.plot(numpy.arange(ntimepoints), vialTimeseries) 
plt.show()

# data/phantoms/all_seir_t1map_mni_mask.nii.gz
