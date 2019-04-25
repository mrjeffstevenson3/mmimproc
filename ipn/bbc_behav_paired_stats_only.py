
# coding: utf-8

# In[1]:

from pathlib import *
import numpy as np
import pandas as pd
np.set_printoptions(linewidth=999999, precision=6, suppress=True, threshold=99999)
pd.set_option('display.width', 999999)
import nibabel as nib
import matplotlib.pyplot as plt
from scipy import stats as ss
from mmimproc.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())


# In[2]:

sublist = ['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']
bfile = fs / 'bbc' / 'behavior' / 'Behavior_for_MRI_2_22_17_jsedits.csv'
bdata = pd.read_csv(str(bfile), header=1 ,index_col=1, usecols=[0, 1]+range(20, 29))
bdata = bdata.transpose()
for s in sublist:
    bdata[s] = bdata['BBC'+s[:3]] - bdata['BBC'+s[4:7]]
bdata_sub = bdata[sublist].transpose()
bdata_sub.drop('subjnum', axis=1, inplace=True)
bdata_sub_stats = bdata_sub.apply(ss.ttest_1samp, axis=0, args=(0.0,)).apply(pd.Series)
bdata_sub_stats.columns = ['tstat', 'p-value']
bdata_sub_stats.sort_values('p-value')


# In[ ]:



