
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
statsdir = fs/project/'stats'/'py_correl_3rdpass'   #'py_correl_5thpass'
fname_templ = '{pool}_{mod}.nii'
cluster_idx_fname_templ = '{pool}_{mod}_{behav}_t{dir}_cluster_index.nii.gz'


# In[10]:

# prepare cluster roi data
cluster_fname = 'cluster_report.csv'
clusters = pd.DataFrame.from_csv(str(statsdir/cluster_fname))
clusters.rename(index=str, columns={' k': 'k', ' x': 'x', ' y': 'y', ' z': 'z', ' name': 'name', ' mori': 'mori', ' JHU_tracts': 'JHU_tracts'}, inplace=True)
clusters.drop(clusters[(clusters.mori == 'Background') & (clusters.JHU_tracts == 'Background')].index, inplace=True)
clusters['mod'] = clusters['name'].str.split('-').apply(lambda x: x[-1])
clusters['pool'] = clusters['name'].str.split('-').apply(lambda x: x[-2])
clusters['dir'] = clusters['name'].str.split('-').apply(lambda x: x[-3])
clusters['behav'] = clusters['name'].str.split('-').apply(lambda x: x[:-3]).str.join('-')
clusters['clu_idx_fname'] = clusters[['pool', 'mod', 'behav', 'dir']].apply(lambda x : cluster_idx_fname_templ.format(pool=x[0], mod=x[1], behav=x[2], dir=x[3]), axis=1)
with WorkingContext(str(statsdir)):
    try:
        for index, row in clusters.iterrows():
            clusters.set_value(index, 'idx_data', nib.load(row['clu_idx_fname']).get_data())
            clusters.set_value(index, 'idx_zooms', nib.load(row['clu_idx_fname']).header.get_zooms())
            clusters.set_value(index, 'idx_shape', nib.load(row['clu_idx_fname']).get_data().shape)
    except:
        print('an error has occured loading data into dataframe.')
clusters.head(10)


# In[6]:

# prepare data for correlations
data = pd.DataFrame(index=list(set(clusters['pool'].values)), columns=list(set(clusters['mod'].values)))
with WorkingContext(str(statsdir)):
    try:
        for pool in list(set(clusters['pool'].values)):
            for mod in list(set(clusters['mod'].values)):
                fname = fname_templ.format(pool=pool, mod=mod)
                data.set_value(pool, mod, nib.load(fname).get_data())
    except:
        print('an error has occured loading data into dataframe.')


# In[5]:

len(list(set(clusters['clu_idx_fname'].values)))


# In[9]:

for index, row in clusters.iterrows():
    print index
    print row['clu_idx_fname']


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



