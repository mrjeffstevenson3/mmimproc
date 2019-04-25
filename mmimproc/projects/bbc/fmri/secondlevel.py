from __future__ import division
import pandas, scipy.stats, numpy

from bbcfunc.behavior.data import everything as subjectinfo

data = pandas.read_csv('cope_by_atlas_regions.tsv', sep='\t', index_col=0).T
data.set_index(data.index.values.astype(int), inplace=True)
regions = data.columns.values
expgroup = [s for s in data.index.values if s < 200]
matches = [subjectinfo.match[s] for s in expgroup]
paired = data.loc[expgroup] - data.loc[matches].set_index(data.loc[expgroup].index)
stats = pandas.DataFrame(index=paired.columns)
stats['t'], stats['p'] = scipy.stats.ttest_1samp(paired, 0, axis=0)

""" Raizada ROIs
Heschl3s gyrus, inferior frontal gyrus (opercular, orbital and
triangular parts separately, and also all three together),
inferior parietal cortex, middle temporal gyrus, superior temporal gyrus,
supramarginal gyrus, and the angular gyrus
"""
keywords = ['Heschl', 'Frontal_Inf', 'Parietal_Inf', 'Temporal_Mid',
            'Temporal_Sup', 'Supra', 'Angular']
ROIs = []
for keyword in keywords:
    ROIs += [r for r in regions if keyword in r]
roistats = stats.loc[ROIs]

## FDR
alpha = .05
m = len(regions)
K = numpy.arange(m)+1

sorted(stats.p) <= (K/m*alpha)
