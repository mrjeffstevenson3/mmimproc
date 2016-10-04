from __future__ import division
from os.path import join, basename, dirname, isfile, isdir
import pandas, numpy
from fmr_runs import picks
from pylabs.regional import statsByRegion
import shell

atlasfpath = 'data/atlases/AAL.nii'

rootdir = '/diskArray/data/bbc/'
#rootdir = '/Volumes/PINGS_DRIVE/bbc'
feattem = 'sub-bbc{}/ses-{}/fmri/sub-bbc{}_ses-{}_fmri_{}.feat'
contrastId = 1
statToSample = 'cope'


data = pandas.DataFrame()
for s, subjectpick in enumerate(picks):
    subnum, session, run = subjectpick
    msg = 'Sampling data for subject {} of {}: {}.'
    print(msg.format(s+1, len(picks), subnum))
    featdir = feattem.format(subnum, session, subnum, session, run)
    featdir = join(rootdir, featdir)
    if not isdir(featdir):
        print('No FEAT results found.')
        continue

    if not isdir(join(featdir, 'reg_standard')):
        print('Registering stats images to standard space..')
        shell.tryrun(['featregapply', featdir])

    subjectData = {}
    for stat in ('cope','varcope'):
        statfile = join(featdir, 'reg_standard', 'stats', stat+'1.nii.gz')
        subjectData[stat] = statsByRegion(statfile, atlasfpath)
    nvoxelsByRegion = subjectData[stat].k
    if statToSample == 't':
        var = subjectData['varcope'].average.astype(float).apply(numpy.sqrt)
        data[subnum] = subjectData['cope'].average / var
    else:
        data[subnum] = subjectData['cope'].average

data.to_csv(statToSample+'_by_atlas_regions.tsv', sep='\t')
    

    
