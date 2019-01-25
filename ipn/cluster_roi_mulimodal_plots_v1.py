
# coding: utf-8

# -  atlases: multi index of mori and JHU in 2 diff res. call each with matching roi from zooms and shape
# -  foster_behav_data: foster and control behavior data in tuplised df.
# -  behav_list: is list of behav tuples
# -  clusters: df of cluster index number and file name
# -  data: df of all multimodal mri
# -  bbcresults: multiindex of multimodal roi and behaviors as in csv saved

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
from pylabs.alignment.resample import reslice_roi
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
output2file = False
project = 'bbc'
statsdir = fs/project/'stats'/'py_correl_5thpass_cthr15_n5000' #'py_correl_2ndpass'   #'py_correl_5thpass_cthr15_n5000'    #'py_correl_3rdpass'   #'py_correl_5thpass'
fname_templ = '{pool}_{mod}.nii'
cluster_idx_fname_templ = '{pool}_{mod}_{behav}_t{dir}_cluster_index.nii.gz'
# prep behavior dataframe
foster_behav_data['pool'] = 'foster'
control_behav_data['pool'] = 'control'
behaviors = pd.concat([foster_behav_data, control_behav_data])

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
clusters['results_index_nm'] = clusters[['name', 'cluster-index']].apply(lambda x: '_roi'.join(x), axis=1)
with WorkingContext(str(statsdir)):
    try:
        for i, row in clusters.iterrows():
            clusters.set_value(i, 'idx_data', nib.load(row['clu_idx_fname'])).astype(object)
    except:
         print('an error has occured loading data into dataframe.')
    else:
         print('successfully entered all cluster index files to dataframe')

# prepare data for correlations
data = pd.DataFrame(index=list(set(clusters['pool'].values)), columns=list(set(clusters['mod'].values)), dtype='object')
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
        
pools = list(set(clusters['pool'].values))
modalities = list(set(clusters['mod'].values))


# In[2]:

#create results container for inclusion into clusters index?? or just add to clusters
#i = 0
#idx = clusters.index[i]
#row = clusters.loc[idx]
#os.chdir(str(statsdir))
with WorkingContext(str(statsdir)):
    for i, (idx, row) in enumerate(clusters.iterrows()):
        index_num = int(row['cluster-index'])
        prime_mod = row['mod']
        prime_behav_tup = [x for x in behav_list if x[1] == row['behav']]
        modalities.insert(0, modalities.pop(modalities.index(prime_mod)))
        cols = ['gp', 'sids', row['behav']] + modalities + ['mori', 'JHUtract', 'pool']
        #setup container for loop
        one_result = pd.DataFrame(index=behaviors.index, columns=cols)
        one_result[row['behav']] = behaviors[prime_behav_tup]
        one_result['pool'] = behaviors['pool']
        one_result.loc[one_result['pool'] == 'foster', 'gp'] = 0
        one_result.loc[one_result['pool'] == 'control', 'gp'] = 1
        one_result['sids'] = behaviors.index.str.strip('BBC')

        roi_data = row['idx_data'].get_data().astype(int)
        roi_mask = np.zeros(roi_data.shape)
        roi_mask[(roi_data == index_num)] = 1
        if not 1 in np.unique(roi_mask):
            raise ValueError('index number '+str(index_num)+' not present in roi file')
        roi_affine = row['idx_data'].affine
        roi_zooms = row['idx_data'].header.get_zooms()
        if np.allclose(roi_zooms, atlases.loc['zooms']['dwi', 'mori']) and np.allclose(roi_data.shape, atlases.loc['shape']['dwi', 'mori']):
            image = 'dwi'
        elif np.allclose(roi_zooms, atlases.loc['zooms']['vbm', 'mori']) and np.allclose(roi_data.shape, atlases.loc['shape']['vbm', 'mori']):
            image = 'vbm'
        else:
            raise ValueError("roi does not have matching atlase shapes.")
        
        # get atlas label(s) for roi
        mori_regions = []
        JHUtract_regions = []
        for a in ['mori', 'JHU_tracts']:
            a_data = atlases.loc['img'][image, a].get_data()
            a_affine = atlases.loc['img'][image, a].affine
            a_zooms = atlases.loc['img'][image, a].header.get_zooms()
            mask = roi_mask
            mask = np.round(mask, 0)
            mdata = a_data * mask

            for r in np.unique(mdata):
                if a == 'mori':
                    if not mori_region_labels[r] == 'Background':
                        mori_regions.append(' '.join(mori_region_labels[r].split('_')))
                if a == 'JHU_tracts':
                    if not JHUtracts_region_labels[r] == 'Background':
                        JHUtract_regions.append(' '.join(JHUtracts_region_labels[r].split('_')))
        one_result['mori'] = ', '.join(mori_regions)
        one_result['JHU_tracts'] = ', '.join(JHUtract_regions)          

        # run modalities
        for mod in modalities:
            for p in pools:
                in_data = data.loc[p, mod].get_data()
                in_affine = data.loc[p, mod].affine
                in_zooms = data.loc[p, mod].header.get_zooms()
                mask = roi_mask
                mask = np.round(mask, 0)
                if not in_data.shape == mask.shape:
                    mask, maffine = reslice_roi(mask, roi_affine, roi_zooms, in_affine, in_zooms[:3])
                if len(mask.shape) == 3 and len(in_data.shape) == 4:
                    mask = np.repeat(mask[:, :, :, np.newaxis], in_data.shape[3], axis=3)
                mdata = in_data*mask
                mdata[mask == 0] = np.nan
                mean = np.nanmean(mdata, axis=(0,1,2))
                if p == 'foster':
                    one_result.loc[one_result['gp'] == 0, mod] = mean
                if p == 'control':
                    one_result.loc[one_result['gp'] == 1, mod] = mean
        
        if output2file:
            outfile = statsdir/str('roi'+str(index_num)+'_'+prime_mod+'_'+prime_behav_tup[1]+'_mm_stats.csv')
            one_result.name = 'roi'+str(index_num)+'_'+prime_mod+'_'+prime_behav_tup[1]
            col_order = ['gp', 'sids', prime_behav_tup[1], prime_mod] + modalities + ['mori', 'JHUtract']
            one_result.to_csv(str(outfile), columns=col_order, index=False)
            provenance.log(str(outfile), 'make multimodal csv from stats index file', str(index_fname), script=__file__,                    provenance={'index': index_num, 'behavior': prime_behav_tup[1], 'modalities': [prime_mod] + modalities, 'cols': col_order})
        


# In[6]:

clusters.head(2)


# In[3]:

one_result


# In[ ]:

result_mi = pd.MultiIndex
bbc_cluster_thr12_results = pd.DataFrame


# In[13]:

clusters['results_index_nm'] = clusters[['name', 'cluster-index']].apply(lambda x: '_roi'.join(x), axis=1)


# In[4]:

data.head(3)


# In[11]:

data.loc['control','MD']


# In[5]:

clusters.head(1)


# In[6]:

foster_behav_data.head(1)


# In[7]:

atlases#.loc['shape']['dwi', 'mori']


# In[16]:

modalities = list(set(clusters['mod'].values)
modalities

                  
res_columns = ['gp', 'sids', row['behav']] + modalities + ['mori', 'JHUtract']


# In[20]:

one_result.head(1)


# In[19]:


#################################



    foster_results = pd.DataFrame(prime_foster_results)
    control_results = pd.DataFrame(prime_control_results)
    foster_results.set_index('subj', inplace=True)
    control_results.set_index('subj', inplace=True)
    foster_results['sids'] = foster_behav_data.index.str.strip('BBC')
    control_results['sids'] = control_behav_data.index.str.strip('BBC')
    foster_results[prime_behav_tup[1]] = foster_behav_data[prime_behav_tup]
    control_results[prime_behav_tup[1]] = control_behav_data[prime_behav_tup]


     
     
    # get prime modality into df first
    prime_foster_results = []
    prime_control_results = []
    for p in pools:
        for mod in modalities:
     
        in_data = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).get_data()
        in_affine = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).affine
        in_zooms = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).header.get_zooms()
        mask = roi_mask
        mask = np.round(mask, 0)
        mdata = in_data * mask
        mdata[mask == 0] = np.nan
        mean = np.nanmean(mdata, axis=(0, 1, 2))
        if p == 'foster':
            for s, m in zip(foster_behav_data.index, mean):
                prime_foster_results.append({'gp': 0, 'subj': s, prime_mod: m})
        if p == 'control':
            for s, m in zip(control_behav_data.index, mean):
                prime_control_results.append({'gp': 1, 'subj': s, prime_mod: m})
    # set up results dataframe
    foster_results = pd.DataFrame(prime_foster_results)
    control_results = pd.DataFrame(prime_control_results)
    foster_results.set_index('subj', inplace=True)
    control_results.set_index('subj', inplace=True)
    foster_results['sids'] = foster_behav_data.index.str.strip('BBC')
    control_results['sids'] = control_behav_data.index.str.strip('BBC')
    foster_results[prime_behav_tup[1]] = foster_behav_data[prime_behav_tup]
    control_results[prime_behav_tup[1]] = control_behav_data[prime_behav_tup]

# run other modalities
for mod in modalities:
    foster_secondary_results = []
    control_secondary_results = []
    for p in pools:
        in_data = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=mod))).get_data()
        in_affine = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=mod))).affine
        in_zooms = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=mod))).header.get_zooms()
        mask = roi_mask
        if not in_data.shape == mask.shape:
            mask, maffine = reslice_roi(mask, roi_affine, roi_zooms, in_affine, in_zooms[:3])
        if len(mask.shape) == 3 and len(in_data.shape) == 4 and in_zooms[3] == 1.0:
            mask = np.repeat(mask[:,:,:,np.newaxis], in_data.shape[3], axis=3)
        assert mask.shape == in_data.shape, 'bad reslice. could be rounding error.'
        mask = np.round(mask, 0)
        mdata = in_data*mask
        mdata[mask == 0] = np.nan
        mean = np.nanmean(mdata, axis=(0,1,2))
        if p == 'foster':
            foster_results[mod] = mean
        if p == 'control':
            control_results[mod] = mean
# put results together into single dataframe and output csv
comb_results = pd.concat([foster_results, control_results])
comb_results['mori'] = atlas_regions['mori']
comb_results['JHUtract'] = atlas_regions['JHUtract']
comb_results[['FA', 'WM', 'GM']] = comb_results[['FA', 'WM', 'GM']].apply(lambda x: x*100)
comb_results[['MD', 'AD', 'RD']] = comb_results[['MD', 'AD', 'RD']].apply(lambda x: x*100000)
comb_results.name = 'roi'+str(index_num)+'_'+prime_mod+'_'+prime_behav_tup[1]
col_order = ['gp', 'sids', prime_behav_tup[1], prime_mod] + modalities + ['mori', 'JHUtract']
comb_results.to_csv(str(outfile), columns=col_order, index=False)
provenance.log(str(outfile), 'make multimodal csv from stats index file', str(index_fname), script=__file__,                provenance={'index': index_num, 'behavior': prime_behav_tup[1], 'modalities': [prime_mod] + modalities, 'cols': col_order})


# In[13]:

pd.concat([foster_behav_data, control_behav_data])


# In[ ]:




# In[18]:

os.chdir(str(statsdir))
for i, (idx, row) in enumerate(clusters.iterrows()):
    print i, idx
    print row['clu_idx_fname']
    print row['idx_data'].get_data().shape
    if i > 10-1:
        break


# In[25]:

for i, (idx, row) in enumerate(clusters.iterrows()):
    print i, type(i), idx, type(idx)
    print row
    if i > 1 -1:
        print 'gt 1'
        break


# In[8]:

data.head(5)


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[2]:

from pathlib import *
import pandas as pd
import numpy as np
import nibabel as nib
import scipy.ndimage.measurements as measurements
from pylabs.correlation.atlas import mori_region_labels, JHUtracts_region_labels
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
"""
makes atlas objects.
"""
project = 'bbc'
atlases_in_templ_sp_dir = fs/project/'reg'/'atlases_in_template_space'
# define atlases for labeling in template space
atlas_midx = pd.MultiIndex.from_arrays([['dwi', 'dwi', 'vbm', 'vbm'], ['mori', 'JHU_tracts', 'mori', 'JHU_tracts']])
atlases = pd.DataFrame(index=['data'], columns=atlas_midx)
# get atlas data
mori_atlas_vbm = atlases_in_templ_sp_dir/'mori_atlas_reg2template.nii.gz'
JHUtracts_atlas_vbm = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template.nii.gz'
mori_atlas_dwi = atlases_in_templ_sp_dir/'mori_atlas_reg2template_resamp2dwi.nii.gz'
JHUtracts_atlas_dwi = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template_resamp2dwi.nii.gz'


# In[30]:

atlases.sort_index(axis=1, inplace=True)
atlases['vbm'].set_value('data', 'mori', nib.load(str(mori_atlas_vbm)))
atlases['vbm'].set_value('data', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)))
atlases['dwi'].set_value('data', 'mori', nib.load(str(mori_atlas_dwi)))
atlases['dwi'].set_value('data', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)))
atlases


# In[51]:

atlases.loc['data', ('dwi', 'JHU_tracts')].get_data().shape


# In[1]:

atlases['vbm'].set_value('data', 'mori', nib.load(str(mori_atlas_vbm)))
atlases['vbm'].set_value('data', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)))
atlases['dwi'].set_value('data', 'mori', nib.load(str(mori_atlas_dwi)).get_data())
atlases['dwi'].set_value('data', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)))


# In[17]:

pd.IndexSlice


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



