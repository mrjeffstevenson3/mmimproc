import pandas
from pylabs.regional import statsByRegion

def atlasWiseSignificantVoxelsFrame(statfiles, atlas, pmax=.001):
    thresh2minp = 2-pmax
    for var in statfiles.keys():
        print('Atlassing stats for '+var)
        region2minp = statsByRegion(statfiles[var]['2minp'], atlas, 
                                    threshold=thresh2minp)
        regiontpos = statsByRegion(statfiles[var]['tpos'], atlas)
        regioncorr = statsByRegion(statfiles[var]['r'], atlas)
    return region2minp
