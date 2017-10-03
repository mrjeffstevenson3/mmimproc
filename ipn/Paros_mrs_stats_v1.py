
# coding: utf-8

# In[1]:


# this is awraper function for mrs that collects the disparate mrs data, calculates group stats, and output to google spreadsheet.
# first set global root data directory
get_ipython().magic(u'matplotlib inline')
import seaborn as sb
import pylabs
pylabs.datadir.target = 'scotty'
from pathlib import *
import datetime
import numpy as np
import pandas as pd
import json
import scipy.stats as ss
from pylabs.utils import ProvenanceWrapper, getnetworkdataroot, appendposix, replacesuffix, WorkingContext, run_subprocess, pylabs_dir
from pylabs.projects.nbwr.file_names import project
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
stats_dir = fs / project / 'stats' / 'mrs'
corr_metab = pd.read_hdf(str(stats_dir / 'all_nbwr_mrs_results_csfcorr_fits_forkam.h5'))
asd_grp = corr_metab.index.str.replace('sub-nbwr','').astype('int') < 400
asd_metab = corr_metab[asd_grp]
cntrl_metab = corr_metab[~asd_grp]
ttest_results = pd.Series(ss.ttest_ind(asd_metab, cntrl_metab, axis=0, equal_var=False), index=['t-stat', 'p-value'])
ttest_results_df = pd.DataFrame.from_dict({'t-stat': ttest_results['t-stat'], 'p-value': ttest_results['p-value']})
col_map = {}
for n, c in zip(range(0, len(corr_metab.columns)), corr_metab.columns):
    col_map[n] = c
ttest_results_df.rename(index=col_map,inplace=True)
ttest_results_df.sort_values(by='p-value', ascending=True)


# In[72]:


corr_metab.loc[corr_metab.index[asd_grp], 'group'] = 'asd'
corr_metab.loc[corr_metab.index[~asd_grp], 'group'] = 'typical'

lt_corr_metab = corr_metab.loc[:, [x for x in corr_metab.columns if 'left' in x] + ['group']]
rt_corr_metab = corr_metab.loc[:, [x for x in corr_metab.columns if 'right' in x] + ['group']]

lt_corr_metab.loc[lt_corr_metab.index[asd_grp], [x for x in corr_metab.columns if 'left' in x]]#.sort_values(axis=0)


# In[76]:


#lt_corr_metab[asd_grp].index[
#lt_corr_metab.loc[asd_grp, [x for x in corr_metab.columns if 'left' in x]] <>\
lt_corr_metab.loc[asd_grp, [x for x in corr_metab.columns if 'left' in x]].median().add(lt_corr_metab.loc[asd_grp, [x for x in corr_metab.columns if 'left' in x]].mad().multiply(3))


# In[19]:


bp = sb.boxplot(data=lt_corr_metab,x='group', y=[x for x in corr_metab.columns if 'left' in x][-1], hue='group', )#, markers=['o', 'x'], kind='reg')


# In[31]:


mlr = sb.lmplot(x='right-Glu-80ms', y='right-GABA', hue='group', data=rt_corr_metab)


# In[30]:


bp = sb.factorplot(data=rt_corr_metab, kind='box', hue='group', y='right-Glu-80ms')


# In[4]:


hdf = corr_metab
asd_grp = hdf.index.str.replace('sub-nbwr', '').astype('int') < 400  # ASD only
tvalues, pvalues = ss.ttest_ind(hdf[asd_grp], hdf[~asd_grp], equal_var=False)
descriptives = hdf.groupby(group_by.astype(int)).describe()
descriptives.rename(index={0: 'control', 1: 'asd'}, inplace=True)
descriptives.index.rename('descriptives', inplace=True)
descriptives.T


# In[ ]:





# In[ ]:


## wip scratch code for pd.apply and groupby


# In[32]:


args = (corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') < 400], corr_metab[corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') >= 400]])
corr_metab.groupby((corr_metab.index.str.replace('sub-nbwr','').astype('int') < 400).apply(ss.ttest_ind, axis=0, args=args)


# In[25]:


corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') < 400]


# In[ ]:





# In[28]:


corr_metab[corr_metab[corr_metab['group']]['group'].values].values


# In[23]:


args = (corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') < 400], corr_metab[corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') >= 400]])
corr_metab.apply(ss.ttest_ind, axis=0, args=args)


# In[ ]:


ttest_ind()


# In[ ]:





# In[ ]:





# In[ ]:




