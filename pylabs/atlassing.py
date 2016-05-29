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
        voxels['r'] = regioncorr['all']
        voxels['p'] = 2-region2minp['all']

        k = lambda row: row['sigpos'].sum()
        r = lambda row: row['r'][row['sigpos']].mean()
        data = pandas.DataFrame(index=region2minp.index)
        data['k'] = voxels.apply(k, axis=1)
        data['r'] = voxels.apply(r, axis=1)
        #for directionLabel, d in {'pos': +1, 'neg': -1}.items():
        #    data[directionLabel] = 


    return data
