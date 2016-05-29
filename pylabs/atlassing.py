import pandas, numpy
from pylabs.regional import statsByRegion

def atlasWiseSignificantVoxelsFrame(statfiles, atlas, pmax=.001):
    thresh2minp = 2-pmax
    varnames = statfiles.keys()
    columns = pandas.MultiIndex.from_product(
        [varnames, ('pos', 'neg'), ('r','k')], 
        names=['variable', 'direction', 'stat'])
    data = pandas.DataFrame(columns = columns)
    for var in varnames:
        print('Atlassing stats for '+var)
        region2minp = statsByRegion(statfiles[var]['2minp'], atlas, 
                                    threshold=thresh2minp)
        regiontpos = statsByRegion(statfiles[var]['tpos'], atlas)
        regioncorr = statsByRegion(statfiles[var]['r'], atlas)

        voxels = pandas.DataFrame(index=region2minp.index)
        voxels['significant'] = region2minp['superthreshold']
        voxels['allpos'] = regiontpos['all'].apply(lambda r: r > 0)
        voxels['allneg'] = voxels['allpos'].apply(lambda r: r == False)
        voxels['pos'] = voxels['significant'] * voxels['allpos']
        voxels['neg'] = voxels['significant'] * voxels['allneg']
        voxels['r'] = regioncorr['all']
        voxels['p'] = 2-region2minp['all']

        for direction in ('pos', 'neg'):
            k = lambda row: row[direction].sum()
            r = lambda row: row['r'][row[direction]].mean()
            data[var, direction, 'k'] = voxels.apply(k, axis=1)
            data[var, direction, 'r'] = voxels.apply(r, axis=1)

    return data
