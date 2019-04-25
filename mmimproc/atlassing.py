from __future__ import division
import pandas, numpy
from pandas import MultiIndex, DataFrame
from mmimproc.regional import statsByRegion

def atlasWiseSignificantVoxelsFrame(statfiles, atlas, pmax=.001):
    thresh1minp = 1-pmax
    varnames = statfiles.keys()
    data = DataFrame(columns = MultiIndex.from_product(
        [varnames, ('pos', 'neg'), ('r','k')], 
        names=['variable', 'direction', 'stat']))
    for var in varnames:
        print('Atlassing stats for '+var)
        region1minp = statsByRegion(statfiles[var]['1minp'], atlas, 
                                    threshold=thresh1minp)
        regiontpos = statsByRegion(statfiles[var]['tpos'], atlas)
        regioncorr = statsByRegion(statfiles[var]['r'], atlas)

        voxels = DataFrame(index=region1minp.index)
        voxels['significant'] = region1minp['superthreshold']
        voxels['totalk'] = region1minp['k']
        voxels['allpos'] = regiontpos['all'].apply(lambda r: r > 0)
        voxels['allneg'] = voxels['allpos'].apply(lambda r: r == False)
        voxels['pos'] = voxels['significant'] * voxels['allpos']
        voxels['neg'] = voxels['significant'] * voxels['allneg']
        voxels['r'] = regioncorr['all']
        voxels['p'] = 1-region1minp['all']

        for direction in ('pos', 'neg'):
            k = lambda row: row[direction].sum()
            f = lambda row: row[direction].sum() / row['totalk']
            r = lambda row: row['r'][row[direction]].mean()
            data[var, direction, 'k'] = voxels.apply(k, axis=1)
            data[var, direction, 'frac'] = voxels.apply(f, axis=1)
            data[var, direction, 'r'] = voxels.apply(r, axis=1)
    
    return data.round(3)
