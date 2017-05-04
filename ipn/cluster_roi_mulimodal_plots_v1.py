
# coding: utf-8

# In[1]:

from pathlib import *
import numpy as np
import pandas as pd
import mne
import six, os
np.set_printoptions(linewidth=999999, precision=6, suppress=True, threshold=99999)
pd.set_option('display.width', 999999)
pd.set_option('display.max_colwidth', 300)
import nibabel as nib
import matplotlib.pyplot as plt
#plt.interactive(False)
from pylabs.correlation.atlas import mori_region_labels, JHUtracts_region_labels
from pylabs.projects.bbc.pairing import foster_behav_data, control_behav_data, behav_list
from pylabs.projects.bbc.correl.atlases import atlases
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
project = 'bbc'
statsdir = fs/project/'stats'/'py_correl_5thpass_cthr15_n5000' #'py_correl_2ndpass'   #'py_correl_5thpass_cthr15_n5000'    #'py_correl_3rdpass'   #'py_correl_5thpass'
fname_templ = '{pool}_{mod}.nii'
cluster_idx_fname_templ = '{pool}_{mod}_{behav}_t{dir}_cluster_index.nii.gz'


# In[2]:

# prepare cluster roi data
cluster_fname = 'cluster_report.csv'
clusters = pd.read_csv(str(statsdir/cluster_fname), index_col=False, dtype='object')
clusters.rename(index=str, columns={' k': 'k', ' x': 'x', ' y': 'y', ' z': 'z', ' name': 'name', ' mori': 'mori', ' JHU_tracts': 'JHU_tracts'}, inplace=True)
clusters.drop(clusters[(clusters.mori == 'Background') & (clusters.JHU_tracts == 'Background')].index, inplace=True)
clusters['mod'] = clusters['name'].str.split('-').apply(lambda x: x[-1])
clusters['pool'] = clusters['name'].str.split('-').apply(lambda x: x[-2])
clusters['dir'] = clusters['name'].str.split('-').apply(lambda x: x[-3])
clusters['behav'] = clusters['name'].str.split('-').apply(lambda x: x[:-3]).str.join('-')
clusters['clu_idx_fname'] = clusters[['pool', 'mod', 'behav', 'dir']].apply(lambda x : cluster_idx_fname_templ.format(pool=x[0], mod=x[1], behav=x[2], dir=x[3]), axis=1)
with WorkingContext(str(statsdir)):
    try:
        for i, row in clusters.iterrows():
            clusters.ix[i, 'idx_data'] = nib.load(row['clu_idx_fname'])
    except:
        print('an error has occured loading data into dataframe.')
    else:
        print('successfully entered all cluster index files to dataframe')


# In[6]:

# prepare data for correlations
data = pd.DataFrame(index=list(set(clusters['pool'].values)), columns=list(set(clusters['mod'].values)))
with WorkingContext(str(statsdir)):
    try:
        for pool in list(set(clusters['pool'].values)):
            for mod in list(set(clusters['mod'].values)):
                fname = fname_templ.format(pool=pool, mod=mod)
                data.set_value(pool, mod, nib.load(fname))
    except:
        print('an error has occured loading data into dataframe.')
    else:
        print('successfully entered all multimodal files to dataframe')


# In[15]:




# In[9]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



