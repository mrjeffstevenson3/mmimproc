import pandas
from pylabs.regional import statsByRegion

def atlasWiseSignificantVoxelsFrame(statfiles, atlas, pmax=.001):
    thresh2minp = 2-pmax
    for var in statfiles.keys():
        region2minp = statsByRegion(statfiles[var]['2minp'], 
                                    atlas, threshold=thresh2minp)
    return region2minp
