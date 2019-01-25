
# coding: utf-8

# In[1]:


get_ipython().magic(u'matplotlib inline')
from pathlib import *
import pandas as pd
import numpy as np
import os, six
import mne
import nibabel as nib
import math
#from surfer import Brain
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


# In[2]:


contrl_sid = ['sub-bbc209', 'sub-bbc211', 'sub-bbc208', 'sub-bbc202', 'sub-bbc249', 'sub-bbc241', 'sub-bbc243', 'sub-bbc231', 'sub-bbc253']
foster_sid = ['sub-bbc101', 'sub-bbc105', 'sub-bbc106', 'sub-bbc108', 'sub-bbc113', 'sub-bbc116', 'sub-bbc118', 'sub-bbc119', 'sub-bbc120']
lh_ct = pd.DataFrame.from_csv('/Users/mrjeffs/Documents/Research/data/bbc/freesurfer_stats_results/grp_parc_stats_lh_cortical_thickness.csv', index_col=None)
rh_ct = pd.DataFrame.from_csv('/Users/mrjeffs/Documents/Research/data/bbc/freesurfer_stats_results/grp_parc_stats_rh_cortical_thickness.csv', index_col=None)


# In[3]:


lh_ct['Subjid'] = lh_ct['lh.aparc.a2009s.thickness'].str.partition('/').drop([2,1], axis=1)
lh_ct = lh_ct.set_index(['Subjid'])
lh_ct = lh_ct.drop('lh.aparc.a2009s.thickness', axis=1)
lh_ct = lh_ct.transpose().astype('float')
rh_ct['Subjid'] = rh_ct['rh.aparc.a2009s.thickness'].str.partition('/').drop([2,1], axis=1)
rh_ct = rh_ct.set_index(['Subjid'])
rh_ct = rh_ct.drop('rh.aparc.a2009s.thickness', axis=1)
rh_ct = rh_ct.transpose().astype('float')


# In[4]:


lh_ct_ctrl = lh_ct[contrl_sid]
lh_ct_fost = lh_ct[foster_sid]
lh_ct['209-101'] = lh_ct['sub-bbc209'] - lh_ct['sub-bbc101']
lh_ct['211-105'] = lh_ct['sub-bbc211'] - lh_ct['sub-bbc105']
lh_ct['208-106'] = lh_ct['sub-bbc208'] - lh_ct['sub-bbc106']
lh_ct['202-108'] = lh_ct['sub-bbc202'] - lh_ct['sub-bbc108']
lh_ct['249-113'] = lh_ct['sub-bbc249'] - lh_ct['sub-bbc113']
lh_ct['241-116'] = lh_ct['sub-bbc241'] - lh_ct['sub-bbc116']
lh_ct['243-118'] = lh_ct['sub-bbc243'] - lh_ct['sub-bbc118']
lh_ct['231-119'] = lh_ct['sub-bbc231'] - lh_ct['sub-bbc119']
lh_ct['253-120'] = lh_ct['sub-bbc253'] - lh_ct['sub-bbc120']
lh_paired_sub = lh_ct[['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']]
lh_paired_sub = lh_paired_sub.transpose()


# In[5]:


lh_paired_sub['lh_S_precentral-inf-part_thickness']


# In[6]:


lh_ct_stats = lh_paired_sub.apply(ss.ttest_1samp, axis=0, args=(0.0,)).apply(pd.Series)
lh_ct_stats.columns = ['lh-tstat', 'lh-p-value']
lh_ct_stats.index.name = 'Region'
lh_ct_stats['Region'] = lh_ct_stats.index.str.replace('lh_', '').str.replace('_thickness', '')
lh_sig_results = lh_ct_stats[lh_ct_stats['lh-p-value'] <= 0.05].sort_values(by='lh-p-value')
lh_sig_results.set_index('Region')


# In[27]:


rh_ct_ctrl = rh_ct[contrl_sid]
rh_ct_fost = rh_ct[foster_sid]
rh_ct['209-101'] = rh_ct['sub-bbc209'] - rh_ct['sub-bbc101']
rh_ct['211-105'] = rh_ct['sub-bbc211'] - rh_ct['sub-bbc105']
rh_ct['208-106'] = rh_ct['sub-bbc208'] - rh_ct['sub-bbc106']
rh_ct['202-108'] = rh_ct['sub-bbc202'] - rh_ct['sub-bbc108']
rh_ct['249-113'] = rh_ct['sub-bbc249'] - rh_ct['sub-bbc113']
rh_ct['241-116'] = rh_ct['sub-bbc241'] - rh_ct['sub-bbc116']
rh_ct['243-118'] = rh_ct['sub-bbc243'] - rh_ct['sub-bbc118']
rh_ct['231-119'] = rh_ct['sub-bbc231'] - rh_ct['sub-bbc119']
rh_ct['253-120'] = rh_ct['sub-bbc253'] - rh_ct['sub-bbc120']
rh_paired_sub = rh_ct[['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']]
rh_paired_sub = rh_paired_sub.transpose()


# In[8]:


rh_ct_stats = rh_paired_sub.apply(ss.ttest_1samp, axis=0, args=(0.0,)).apply(pd.Series)
rh_ct_stats.columns = ['rh-tstat', 'rh-p-value']
rh_ct_stats.index.name = 'Region'
rh_ct_stats['Region'] = rh_ct_stats.index.str.replace('rh_', '').str.replace('_thickness', '')
rh_sig_results = rh_ct_stats[rh_ct_stats['rh-p-value'] <= 0.05].sort_values(by='rh-p-value')
rh_sig_results.set_index('Region')


# In[9]:


rh_sig_results.merge(lh_sig_results, left_on='Region', right_on='Region', how='outer').fillna('').set_index('Region').sort_values(['rh-p-value', 'lh-p-value'])


# In[40]:


sublist = ['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']
bfile = fs / 'bbc' / 'behavior' / 'Behavior_for_MRI_2_22_17_jsedits.csv'
bdata = pd.read_csv(str(bfile), header=1 ,index_col=1, usecols=[0, 1]+range(20, 29))
bdata = bdata.transpose()
for s in sublist:
    bdata[s] = bdata['BBC'+s[:3]] - bdata['BBC'+s[4:7]]
bdata_sub = bdata[sublist].transpose()
bcontrl_sid = [x.replace('sub-', '').upper() for x in contrl_sid]
bfoster_sid = [x.replace('sub-', '').upper() for x in foster_sid]
bdata_foster = bdata[bfoster_sid]
bdata_contrl = bdata[bcontrl_sid]
bdata_foster = bdata_foster.transpose()
bdata_contrl = bdata_contrl.transpose()
bdata_foster.head(9)


# In[52]:


bdata_foster[bdata_foster.columns[1:]]


# In[59]:


lh_ct_fost.corrwith(bdata_foster.TOPELeliSS).sort_values(ascending=False).round(5)


# In[76]:


#lh_ct_fost
bdata_foster


# In[80]:


#corr, p = 
ss.spearmanr(bdata_foster[bdata_foster.columns[1:]], lh_ct_fost, axis=0)


# In[25]:


lh_ct_fost.columns = lh_ct_fost.columns.str.replace('sub-','').str.upper()


# In[33]:


lh_ct_fost = lh_ct_fost.transpose()
bdata = bdata.transpose()


# In[36]:


bdata.head(9)


# In[37]:


lh_ct_fost.corrwith(bdata.transpose(), axis=0, drop=True)


# In[28]:


rh_ct_fost.columns = rh_ct_fost.columns.str.replace('sub-','').str.upper()
rh_ct_fost.transpose().head(9)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[4]:


import mayavi


# In[3]:


os.environ['SUBJECTS_DIR'] = str(fs / 'bbc' / 'reg' / 'ants_vbm_pairedLH_in_template_space')
#templ = Brain("template_hires_br_freesurf_v6", 'lh', 'white')


# In[34]:


file = '/Users/mrjeffs/Documents/Research/data/bbc/reg/ants_vbm_pairedLH_in_template_space/template_hires_br_freesurf_v6/label/lh.aparc.a2009s.annot'
labels = mne.read_labels_from_annot(annot_fname=file, hemi='lh', parc='aparc.a2009s', subject='template_hires_br_freesurf_v6', subjects_dir='/Users/mrjeffs/Documents/Research/data/bbc/reg/ants_vbm_pairedLH_in_template_space',verbose=True)
labels


# In[25]:


pd_labels.iloc[3][0]


# In[33]:


lh_ct_stats.loc['lh_S_oc_middle&Lunatus_thickness']


# In[ ]:





# In[9]:


#paired_sub = paired_sub.groupby('Subjid', axis=0)
#paired_sub.aggregate(ss.ttest_1samp(paired_sub, popmean=0.0, axis=0,))
#paired_sub['mean'] = paired_sub.mean(axis=1)
#paired_sub['std_dev'] = paired_sub.std(axis=1)
#paired_sub['std_err'] = paired_sub['std_dev'] / math.sqrt((len(dwipairing) / 2)-1)

#paired_sub = paired_sub.transpose()
#paired_sub
#lh_ct_tstat, np.sort(lh_ct_pval)
#paired_sub

