from pathlib import *
import pandas as pd
import numpy as np
import nibabel as nib
from pylabs.correlation.atlas import mori_region_labels, JHUtracts_region_labels
from pylabs.alignment.resample import reslice_roi
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.projects.bbc.pairing import foster_behav_data, control_behav_data, behav_list
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
#set up roi
''' MEG auditory regions
11133  ctx_lh_G_temp_sup-G_T_transv
'''
project = 'bbc'
statsdir = fs/project/'stats'/'py_correl_2ndpass'
index_num=384
t_thr=5.0
min_cluster_size=10
index_fname= statsdir/'foster_MD_PPVTSS_tpos_cluster_index_cthr10.nii.gz'
# define atlases for labeling
atlases_in_templ_sp_dir = fs/project/'reg'/'atlases_in_template_space'
mori_atlas = atlases_in_templ_sp_dir/'mori_atlas_reg2template.nii.gz'
JHUtracts_atlas = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template.nii.gz'
prime_mod = str(index_fname.name).split('_')[1]
prime_behav_tup = [x for x in behav_list if x[1] == str(index_fname.name).split('_')[2]][0]
outfile = statsdir/str('roi'+str(index_num)+'_'+prime_mod+'_'+prime_behav_tup[1]+'_mm_stats.csv')
roi_data = nib.load(str(index_fname)).get_data().astype(int)
roi_mask = np.zeros(roi_data.shape)
roi_mask[roi_data == index_num] = 1
if not 1 in np.unique(roi_mask):
    raise ValueError('index number '+str(index_num)+' not present in roi file')
roi_affine = nib.load(str(index_fname)).affine
roi_zooms = nib.load(str(index_fname)).header.get_zooms()
# get atlas label(s) for roi
mori_regions = []
JHUtract_regions = []
for a in [mori_atlas, JHUtracts_atlas]:
    a_data = nib.load(str(a)).get_data()
    a_affine = nib.load(str(a)).affine
    a_zooms = nib.load(str(a)).header.get_zooms()
    mask = roi_mask
    if not a_data.shape == mask.shape:
        mask, maffine = reslice_roi(mask, roi_affine, roi_zooms, a_affine, a_zooms[:3])
    assert mask.shape == a_data.shape, 'bad reslice. could be rounding error.'
    mask = np.round(mask, 0)
    mdata = a_data * mask

    for r in np.unique(mdata):
        if a == mori_atlas:
            if not mori_region_labels[r] == 'Background':
                mori_regions.append(' '.join(mori_region_labels[r].split('_')))
        if a == JHUtracts_atlas:
            if not JHUtracts_region_labels[r] == 'Background':
                JHUtract_regions.append(' '.join(JHUtracts_region_labels[r].split('_')))

atlas_regions = {'mori': ', '.join(mori_regions), 'JHUtract': ', '.join(JHUtract_regions)}

#set up all files to include and test
pools = ['foster', 'control']
modalities = ['FA', 'AD', 'RD', 'MD', 'GM', 'WM']
modalities.remove(prime_mod)
allfile_ftempl = '{pool}_{mod}.nii'
# get prime modality into df first
prime_foster_results = []
prime_control_results = []
for p in pools:
    in_data = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).get_data()
    in_affine = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).affine
    in_zooms = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).header.get_zooms()
    mask = roi_mask
    if not in_data.shape == mask.shape:
        mask, maffine = reslice_roi(mask, roi_affine, roi_zooms, in_affine, in_zooms[:3])
    if len(mask.shape) == 3 and len(in_data.shape) == 4 and in_zooms[3] == 1.0:
        mask = np.repeat(mask[:, :, :, np.newaxis], in_data.shape[3], axis=3)
    assert mask.shape == in_data.shape, 'bad reslice. could be rounding error.'
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
provenance.log(str(outfile), 'make multimodal csv from stats index file', str(index_fname), script=__file__, \
               provenance={'index': index_num, 'behavior': prime_behav_tup[1], 'modalities': [prime_mod] + modalities, 'cols': col_order})