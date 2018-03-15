
# coding: utf-8

# In[1]:


from pathlib import *
import pandas as pd
import numpy as np
from pylabs.utils import *
import qgrid
qgrid.enable
fs = Path(getnetworkdataroot())
project = 'acdc'
store = pd.HDFStore(str(fs/project/('all_'+project+'_info.h5')))
testdf = store.select('/sub-genz996/ses-2/mrs/gaba_fit_info')
store.close()
qgrid.show_grid(testdf)


# In[4]:


qgrid_widget = qgrid.QgridWidget(df=testdf, show_toolbar=True)
qgrid_widget
#qgrid.show_grid


# In[8]:


qgrid.show_grid(testdf)


# In[9]:


qgrid.nbinstall(overwrite=True)

