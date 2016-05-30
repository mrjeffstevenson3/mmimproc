from __future__ import division
import pandas, numpy
from pandas import MultiIndex, DataFrame
from pylabs.regional import statsByRegion

def atlasWiseSignificantVoxelsFrame(statfiles, atlas, pmax=.001):
    thresh2minp = 2-pmax
    varnames = statfiles.keys()
    data = DataFrame(columns = MultiIndex.from_product(
        [varnames, ('pos', 'neg'), ('r','k')], 
        names=['variable', 'direction', 'stat']))
    for var in varnames:
        print('Atlassing stats for '+var)
        region2minp = statsByRegion(statfiles[var]['2minp'], atlas, 
                                    threshold=thresh2minp)
        regiontpos = statsByRegion(statfiles[var]['tpos'], atlas)
        regioncorr = statsByRegion(statfiles[var]['r'], atlas)

        voxels = DataFrame(index=region2minp.index)
        voxels['significant'] = region2minp['superthreshold']
        voxels['totalk'] = region2minp['k']
        voxels['allpos'] = regiontpos['all'].apply(lambda r: r > 0)
        voxels['allneg'] = voxels['allpos'].apply(lambda r: r == False)
        voxels['pos'] = voxels['significant'] * voxels['allpos']
        voxels['neg'] = voxels['significant'] * voxels['allneg']
        voxels['r'] = regioncorr['all']
        voxels['p'] = 2-region2minp['all']

        for direction in ('pos', 'neg'):
            k = lambda row: row[direction].sum()
            f = lambda row: row[direction].sum() / row['totalk']
            r = lambda row: row['r'][row[direction]].mean()
            data[var, direction, 'k'] = voxels.apply(k, axis=1)
            data[var, direction, 'frac'] = voxels.apply(f, axis=1)
            data[var, direction, 'r'] = voxels.apply(r, axis=1)
    
    return data.round(3)
