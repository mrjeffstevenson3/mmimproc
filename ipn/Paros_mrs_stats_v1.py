
# coding: utf-8

# In[1]:


# this is awraper function for mrs that collects the disparate mrs data, calculates group stats, and output to google spreadsheet.
# first set global root data directory
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
asd_metab = corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') < 400]
cntrl_metab = corr_metab[corr_metab.index.str.replace('sub-nbwr','').astype('int') >= 400]
col_map = {}
for n, c in zip(range(0, len(corr_metab.columns)), corr_metab.columns):
    col_map[n] = c
ttest_results = pd.Series(ss.ttest_ind(asd_metab, cntrl_metab, axis=0, equal_var=False), index=['t-stat', 'p-value'])
ttest_results_df = pd.DataFrame.from_dict({'t-stat': ttest_results['t-stat'], 'p-value': ttest_results['p-value']})
ttest_results_df.rename(index=col_map,inplace=True)
ttest_results_df


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




