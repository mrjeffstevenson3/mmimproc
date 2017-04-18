from __future__ import division
from os.path import join
import scipy.stats, math, datetime
from numpy import square, sqrt
from pylabs.utils import progress
import pylabs.io.images
from pathlib import *
import pandas as pd
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



provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
project = 'bbc'
statsdir = fs/project/'stats'/'py_correl_3rdpass'
t_thr=5.0
min_cluster_size=10
index_fname= statsdir/'foster_WM_PPVTSS_tpos_cluster_index_cthr10.nii.gz'
index_num=37
contrl_sid = ['{sid}'.format(sid=s) for s, v in paired_vbm_control_subjs_sorted]
foster_sid = ['{sid}'.format(sid=s) for s, v in paired_vbm_foster_subjs_sorted]
stat_ftempl = '{pool}_{mod}_{behav}_{tstat}.nii.gz'
allfile_ftempl = '{pool}_{mod}.nii'
pool = ['foster', 'control']
modalities = ['FA', 'AD', 'RD', 'MD', 'GM', 'WM']
behaviors = [str(b[1]) for b in behav_list]
tstats = ['tpos', 'tneg', 'r']
all_files = []
for p in pool:
    for m in modalities:
        all_files.append(statsdir/allfile_ftempl.format(pool=p, mod=m))
roi_data = nib.load(str(index_fname)).get_data().astype(int)
roi_mask = np.zeros(roi_data.shape)
roi_mask[roi_data == index_num] = 1
if not 1 in np.unique(roi_mask):
    raise ValueError('index number '+str(index_num)+' not present in roi file')
roi_affine = nib.load(str(index_fname)).affine
roi_zooms = nib.load(str(index_fname)).header.get_zooms()
tmp_list = []
for afile in all_files:
    in_data = nib.load(str(afile)).get_data()
    in_affine = nib.load(str(afile)).affine
    in_zooms = nib.load(str(afile)).header.get_zooms()
    mask = roi_mask
    if not in_data.shape == mask.shape:
        mask, maffine = reslice_roi(mask, roi_affine, roi_zooms, in_affine, in_zooms[:3])
    if len(mask.shape) == 3 and len(in_data.shape) == 4 and in_zooms[3] == 1.0:
        mask = np.repeat(mask[:,:,:,np.newaxis], in_data.shape[3], axis=3)
    assert mask.shape == in_data.shape, 'bad reslice. could be rounding error.'
    mask = np.round(mask, 0)
    maskb = mask[mask == 1]
    mean = in_data[mask == 1.0].mean()

