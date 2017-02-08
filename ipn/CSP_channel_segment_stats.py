
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
LCSP_fname = fs / 'bbc' / 'LeftPostIntCap.csv'
lcsp_data = pd.read_csv(LCSP_fname, index_col=0, header=None)
lcsp_data.reset_index(level=0, inplace=True)


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

lcsp_data = lcsp_data.stack(0)
lcsp_data.head(7)


# In[7]:

lcsp_data = lcsp_data.unstack(0)
lcsp_data.head(7)


# In[16]:

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



