from __future__ import division
from os.path import join
import scipy.stats, math, datetime
from numpy import square, sqrt
from pylabs.utils import progress
import pylabs.io.images
from pathlib import *
import pandas as pd
from pandas.tools.util import cartesian_product
import numpy as np
import nibabel as nib
from scipy.stats import spearmanr as sp_correl
from pylabs.alignment.resample import reslice_roi
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.io.images import loadStack
from pylabs.projects.bbc.pairing import FA_foster_pnames, FA_control_pnames, \
    MD_foster_pnames, MD_control_pnames, RD_foster_pnames, RD_control_pnames, \
    AD_foster_pnames, AD_control_pnames, GMVBM_foster_pnames, GMVBM_control_pnames, WMVBM_foster_pnames, \
    WMVBM_control_pnames, foster_paired_behav_subjs, control_paired_behav_subjs, \
    foster_behav_data, control_behav_data, behav_list, paired_vbm_foster_subjs_sorted, paired_vbm_control_subjs_sorted


#set up roi
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
project = 'bbc'
statsdir = fs/project/'stats'/'py_correl_3rdpass'
t_thr=5.0
min_cluster_size=10
index_fname= statsdir/'foster_WM_PPVTSS_tpos_cluster_index_cthr10.nii.gz'
index_num=37
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
            prime_foster_results.append({'subj': s, prime_mod: m, 'gp': 0})
    if p == 'control':
        for s, m in zip(control_behav_data.index, mean):
            prime_control_results.append({'subj': s, prime_mod: m, 'gp': 1})

foster_results = pd.DataFrame(prime_foster_results)
control_results = pd.DataFrame(prime_control_results)
foster_results.set_index('subj', inplace=True)
control_results.set_index('subj', inplace=True)
foster_results[prime_behav_tup[1]] = foster_behav_data[prime_behav_tup]
control_results[prime_behav_tup[1]] = control_behav_data[prime_behav_tup]
foster_results['sids'] = foster_behav_data.index.str.strip('BBC')
control_results['sids'] = control_behav_data.index.str.strip('BBC')

#behav_labels = [str(b[1]) for b in behav_list]
#tstats = ['tpos', 'tneg', 'r']
# stat_ftempl = '{pool}_{mod}_{behav}_{tstat}.nii.gz'
# all_files = []
# for p in pools:
#     for m in modalities:
#         all_files.append(statsdir/allfile_ftempl.format(pool=p, mod=m))
#
# subjs = [s for s in foster_paired_behav_subjs + control_paired_behav_subjs]
# gp = [0] * len(foster_paired_behav_subjs) + [1] * len(control_paired_behav_subjs)
# results_mi = pd.MultiIndex.from_arrays(cartesian_product([subjs,gp,behav_list]), names=('subject', 'group', 'behavior'))
#
# results = pd.DataFrame()

for mod in modalities:
    foster_secondary_results = []
    control_secondary_results = []
    for p in pools:
        in_data = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).get_data()
        in_affine = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).affine
        in_zooms = nib.load(str(statsdir/allfile_ftempl.format(pool=p, mod=prime_mod))).header.get_zooms()
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

comb_results = pd.concat([foster_results, control_results])

        #
        # for s, m in zip(foster_behav_data.index, mean):
        #     results_list.append({'subj': s, 'FA': m, 'gp': 0})
        #     # how to make 'FA' a param? use % with string format?
        # results = pd.DataFrame()
        #
        # pool, mod = str(afile.name).split('.')[0].split('_')

        if pool == 'foster':
            behav = foster_behav_data[behavior]
            sids = pd.Series(foster_behav_data.index.str.strip('BBC'))
            gp = pd.Series([0]*len(sids))
        elif pool == 'control':
            behav = control_behav_data[behavior]
            sids = pd.Series(control_behav_data.index.str.strip('BBC'))
            gp = pd.Series([1] * len(sids))

