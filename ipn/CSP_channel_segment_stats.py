
# coding: utf-8

# In[1]:


get_ipython().magic(u'matplotlib inline')
from pathlib import *
import pandas as pd
import numpy as np
import math
import statsmodels as sm
from scipy import stats as ss
from IPython.core.display import HTML
css = open('style-table.css').read() + open('style-notebook.css').read()
HTML('<style>{}</style>'.format(css))
pd.set_option('display.width', 999999)
pd.options.display.max_colwidth = 250
pd.options.display.max_rows = 999
from pylabs.projects.bbc.pairing import dwipairing
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
#get data from test file
LCSP_fname = fs / 'bbc' / 'reg' / 'dwi_warps_in_template_space' / 'comb_FA_AD_RD_MD_4vol' / 'LeftPostIntCap.csv'
lcsp_data = pd.read_csv(LCSP_fname, header=None)
#lcsp_data.reset_index(level=0, inplace=True)


# In[2]:


#makes subj id fm 1st 10 chars of vtk_file_name
lcsp_data['Subjid'] = lcsp_data.iloc[:, 0].str[0:10]
lcsp_data.head(4)


# In[3]:


lcsp_data.rename(columns = {lcsp_data.columns[0]: 'fname', lcsp_data.columns[1]: 'modality', lcsp_data.columns[2]: 'seg1', lcsp_data.columns[3]: 'seg2', lcsp_data.columns[4]: 'seg3', lcsp_data.columns[5]: 'seg4', lcsp_data.columns[6]: 'seg5', lcsp_data.columns[7]: 'seg6', lcsp_data.columns[8]: 'seg7', lcsp_data.columns[9]: 'seg8', lcsp_data.columns[10]: 'seg9', lcsp_data.columns[11]: 'seg10'}, inplace = True)
lcsp_data.drop('fname', axis=1, inplace=True)


# In[4]:


lcsp_data.set_index(['Subjid', 'modality'], inplace=True)
lcsp_data.head(7)


# In[5]:


lcsp_data = lcsp_data.unstack(0)
lcsp_data.head(7)


# In[6]:


lcsp_fa = lcsp_data.loc[['fa']]
lcsp_fa = lcsp_fa.stack(0)
lcsp_ad = lcsp_data.loc[['ad']]
lcsp_ad = lcsp_ad.stack(0)
lcsp_rd = lcsp_data.loc[['rd']]
lcsp_rd = lcsp_rd.stack(0)
lcsp_md = lcsp_data.loc[['md']]
lcsp_md = lcsp_md.stack(0)
lcsp_fa.head(10), lcsp_ad.head(10),lcsp_rd.head(10),lcsp_md.head(10)


# In[7]:


lcsp_fa['209-101'] = lcsp_fa['sub-bbc209'] - lcsp_fa['sub-bbc108']
lcsp_fa['211-105'] = lcsp_fa['sub-bbc211'] - lcsp_fa['sub-bbc105']
lcsp_fa['208-106'] = lcsp_fa['sub-bbc208'] - lcsp_fa['sub-bbc106']
lcsp_fa['202-108'] = lcsp_fa['sub-bbc202'] - lcsp_fa['sub-bbc108']
lcsp_fa['249-113'] = lcsp_fa['sub-bbc249'] - lcsp_fa['sub-bbc113']
lcsp_fa['241-116'] = lcsp_fa['sub-bbc241'] - lcsp_fa['sub-bbc116']
lcsp_fa['243-118'] = lcsp_fa['sub-bbc243'] - lcsp_fa['sub-bbc118']
lcsp_fa['231-119'] = lcsp_fa['sub-bbc231'] - lcsp_fa['sub-bbc119']
lcsp_fa['253-120'] = lcsp_fa['sub-bbc253'] - lcsp_fa['sub-bbc120']
lcsp_fa[['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']]


# In[8]:


#lcsp_fa.drop('fa', axis=0, inplace=True)
lcsp_fa_sub = lcsp_fa[['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']]
lcsp_fa_sub = lcsp_fa_sub.transpose()
lcsp_fa_sub.fillna(0, inplace=True)


# In[13]:





# In[14]:


lcsp_fa_sub


# In[16]:


(0.0,)*10


# In[24]:


lcsp_fa_sub_stats = lcsp_fa_sub['fa'].apply(ss.ttest_1samp, axis=0, args=(0.0,)).apply(pd.Series)
lcsp_fa_sub_stats.columns = ['fa-tstat', 'fa-p-value']
lcsp_fa_sub_stats


# In[ ]:





# In[6]:


lcsp_data = lcsp_data.stack(0)
lcsp_data.head(7)


# In[7]:


lcsp_data = lcsp_data.unstack(0)
lcsp_data.head(10)


# In[ ]:





# In[8]:


lcsp_data['211-105'] = lcsp_data['sub-bbc211']['fa'] - lcsp_data['sub-bbc105']['fa']
lcsp_data['211-105']


# In[13]:


lcsp_data.head(7)


# In[ ]:





# In[ ]:


lcsp_data.set_index(['Subjid', 'modality'])


# In[ ]:


list(result.columns.levels[0])


# In[ ]:


lcsp_data.unstack(level=0)
lcsp_data.unstack(level=0)
lcsp_data.T
lcsp_data


# In[ ]:





# In[12]:


lcsp_data.T
lcsp_data


# In[ ]:




