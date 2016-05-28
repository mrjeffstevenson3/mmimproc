import pandas, numpy
from pylabs.regional import statsByRegion

def atlasWiseSignificantVoxelsFrame(statfiles, atlas, pmax=.001):
    thresh2minp = 2-pmax
    for var in statfiles.keys():
        print('Atlassing stats for '+var)
        region2minp = statsByRegion(statfiles[var]['2minp'], atlas, 
                                    threshold=thresh2minp)
        regiontpos = statsByRegion(statfiles[var]['tpos'], atlas)
        regioncorr = statsByRegion(statfiles[var]['r'], atlas)

        voxels = pandas.DataFrame(index=region2minp.index)
        voxels['significant'] = region2minp['superthreshold']
        voxels['pos'] = regiontpos['all'].apply(lambda r: r > 0)
        voxels['neg'] = data['pos'].apply(lambda r: r == False)
        voxels['sigpos'] = voxels['significant'] * voxels['pos']
        voxels['signeg'] = voxels['significant'] * voxels['neg']

        for directionLabel, d in {'pos': +1, 'neg': -1}.items():
            data[directionLabel] = 


    return region2minp
