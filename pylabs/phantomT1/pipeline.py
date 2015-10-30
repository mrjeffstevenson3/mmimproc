from __future__ import print_function
import os, fnmatch, glob, collections, datetime
from os.path import join
import numpy
from nipype.interfaces import fsl
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.qt1.fitting import t1fitCombinedFile

def dateFromPath(path):
    dateSegment = path.split('/')[-3]
    dateStr = dateSegment.split('_')[2]
    return datetime.datetime.strptime(dateStr, '%Y%m%d').date()
    

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
seirSessions = dict()
for s, session in enumerate(sessions):
    print('Fitting session {0} of {1}..'.format(s, len(sessions)))
    t1filename = session.replace('.nii','_t1.nii')
    date = dateFromPath(t1filename)
    seirSessions[date] = t1filename
    if not os.path.isfile(t1filename):
        try:
            IRs = [500, 1500, 3000]
            t1fitCombinedFile(session, IRs, scantype='IR', t1filename=t1filename)
        except ValueError:
            print("Don't have all images for this session. Continuing.")


## ATLASSING

atlasfile = 't1_phantom_mask_course.nii.gz'
vialAtlas = join('data','atlases',atlasfile)
labels = atlaslabels(atlasfile)
nvials = len(labels)

# get region/vial-wise data for each timepoint
dates = sorted(seirSessions.keys())
scansInOrder = [seirSessions[d] for d in dates]
ntimepoints = len(dates)
vialTimeseries = numpy.zeros((ntimepoints, nvials))
for t, scan in enumerate(scansInOrder):
    print('Sampling vials for scan {0} of {1}'.format(t,ntimepoints))
    if not os.path.isfile(scan): # temp fix to deal with session with only two vols
        print('Missing t1 image: '+scan)
        continue
    regionalStats = statsByRegion(scan, vialAtlas)
    vialTimeseries[t, :] = regionalStats['average']

vialTimeseries = numpy.delete(vialTimeseries, 0, 1)
del labels[0]

# plot development over time for each vial
lines = plt.plot(dates, vialTimeseries) 
plt.legend(lines, labels, loc=8)
plt.show()

