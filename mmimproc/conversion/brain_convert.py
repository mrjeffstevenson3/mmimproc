# todo: break apart individual project dataframes into file in each project folder.
# todo: refactor conv_subjs to put in hdf file name and remove niftiDict
# todo: capture spectroscopy meta data if present

import mmimproc
mmimproc.datadir.target = 'jaba'
from mmimproc.conversion.parrec2nii_convert import BrainOpts
from pathlib import *
import pandas as pd
import nibabel
import nipype
from nipype.interfaces import fsl
from mmimproc.conversion.parrec2nii_convert import brain_proc_file
from mmimproc.utils.sessions import make_sessions_fm_dict
from mmimproc.io.mixed import conv_df2h5, backup_source_dirs, get_h5_keys
import os
from os.path import join
from datetime import datetime
import subprocess
from collections import defaultdict
from mmimproc.conversion.parrec2nii_convert import mergeddicts
from mmimproc.utils import getnetworkdataroot, ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = mmimproc.fs_local

print(fs)
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')


#individual project parameters to be set once here. keys are immutable or code will break.
slu_phant_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,), 'rms': False},
            '_T1_MAP_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'verbose': True, 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_fa_{fa}_tr_{tr}_{run}.nii',
                        'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,), 'rms': False},
            '_IR': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'seir', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_tr_{tr}_ti_{ti}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,), 'rms': False},
            })

disc_phant_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,), 'rms': False},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'verbose': True, 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_fa_{fa}_tr_{tr}_{run}.nii',
                        'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,), 'rms': False},
            '_IR': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'seir', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_tr_{tr}_ti_{ti}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,), 'rms': False},
            })

self_control_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,)},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_fa-{fa}-tr-{tr}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0,)},
            })

roots_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_T1_MAP_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_fa-{fa}-tr-{tr}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_TOPUP_DTI_32DIR_B1850_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'topup', 'scan_info': '32dir_b1850', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_TOPDN_DTI_31DIR_B1850_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'topdn', 'scan_info': '32dir_b1850', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_WE_MEMPRAGE_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'wemempr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': True},
            '_MEMP_VBM_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'vbmmempr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': True},
            '_3DT2W_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            })

bbc_conv = pd.DataFrame({
            '_3DB0_MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b0map', 'scan_info': '',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'b1corr': False, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3),
                        'rms': False},
            '_DTI_MED_RES_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dti', 'scan_info': '15dir_b1000',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True,
                        'dwell_time': True, 'b1corr': False, 'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True,
                        'multisession': (1, 2, 3), 'rms': False},
            '_QUIET_MPRAGE2_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'mpr', 'scan_info': '',
                        'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'b1corr': True, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': False},
            '_WE_MPRAGE2_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'wempr', 'scan_info': '',
                        'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'b1corr': True, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3),
                        'rms': False},
            '_FMRI1_': {'dirstruct': 'BIDS', 'outdir': 'fmri', 'scan_name': 'fmri', 'scan_info': '',
                        'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': False, 'dwell_time': False,
                        'b1corr': False, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3),
                        'rms': False},
            })

nbwr_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map-fp', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_T1_MAP_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_fa-{fa}-tr-{tr}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI64_3SH_B0_B800_B2000_TOPUP_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '64dir-3sh-800-2000', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI_B0_TOPDN_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topdn', 'scan_info': '6S0',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True,
                        'dwell_time': True, 'b1corr': False, 'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner',
                        'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': False},
            '_DWI_B0_TOPUP_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '6S0', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_WIP_MEMP_VBM_TI850_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'vbmmempr', 'scan_info': 'ti850', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': True},
            '_MEMP_FS_TI1100_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'fsmempr', 'scan_info': 'ti1100',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                        'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': True},
            '_AX_MATCH_RIGHT_MEMP_VBM_TI850_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'right_match_mrs', 'scan_info': 'ti850',
                         'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                         'dwell_time': False, 'b1corr': False,
                         'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                         'minmax': ('parse', 'parse'), 'store_header': True,
                         'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                         'multisession': (1, 2, 3), 'rms': False},
            '_AX_MATCH_LEFT_MEMP_VBM_TI850_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'left_match_mrs',
                          'scan_info': 'ti850',
                          'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                          'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                          'dwell_time': False, 'b1corr': False,
                          'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                          'minmax': ('parse', 'parse'), 'store_header': True,
                          'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                          'multisession': (1, 2, 3), 'rms': False},
            '_AX_MATCH_RIGHT_MEMP_VBM_TI1100_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'right_match_mrs',
                          'scan_info': 'ti1100',
                          'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                          'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                          'dwell_time': False, 'b1corr': False,
                          'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                          'minmax': ('parse', 'parse'), 'store_header': True,
                          'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                          'multisession': (1, 2, 3), 'rms': False},
            '_AX_MATCH_LEFT_MEMP_VBM_TI1100_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'left_match_mrs',
                         'scan_info': 'ti1100',
                         'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                         'dwell_time': False, 'b1corr': False,
                         'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                         'minmax': ('parse', 'parse'), 'store_header': True,
                         'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                         'multisession': (1, 2, 3), 'rms': False},

            '_3DT2W_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            })

genz_conv = pd.DataFrame({
            '_B1MAP-QUIET_FC_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': 'fc', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'take_lowest_recon': False, 'multisession': (1, 2, 3), 'rms': False},
            '_VFA_FA4-25_QUIET': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'vfa', 'scan_info': 'fa-4-25',   # hard code flip angles because vy patch can't assign correct values in PAR file
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}-tr-{tr}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'take_lowest_recon': False, 'multisession': (1, 2, 3), 'rms': False},
            '_MT_MPF_QUIET': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'mt', 'scan_info': 'mpf', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                           'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                           'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                           'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'take_lowest_recon': False, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI64_3SH_B0_B800_B2000_TOPUP_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '64dir-3sh-800-2000', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'take_lowest_recon': False, 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False, },
            '_DWI6_B0_TOPDN_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topdn', 'scan_info': '6S0',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True,
                        'dwell_time': True, 'b1corr': False, 'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner',
                        'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False, 'take_lowest_recon': False,
                        'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_B0_TOPUP_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '6S0', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False, 'take_lowest_recon': False, 'multisession': (1, 2, 3), 'rms': False},
            'MEMP_IFS_0p5mm_2echo_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'fsmempr', 'scan_info': 'ti1200',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': False,
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                        'dwell_time': False, 'b1corr': False,'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True,'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': True},
            '_MPR_QUIET_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'right_match_mrs',
                          'scan_info': 'ti1100', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': False,
                          'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                          'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                          'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_AX_MATCH_ACC_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'match_acc_mrs', 'scan_info': 'ti1200',
                         'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                         'dwell_time': False, 'b1corr': False, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'take_lowest_recon': False,
                         'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_QUIET_3DT2W': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'take_lowest_recon': False, 'multisession': (1, 2, 3), 'rms': False},
            '_AX_T2_MATCH_ACC_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'match_acc_mrs', 'scan_info': 't2',
                       'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                       'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False, 'field_strength': False, 'vol_info': False,
                       'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': False,
                       'overwrite': True, 'strict_sort': True, 'take_lowest_recon': False, 'multisession': (1, 2, 3), 'rms': False},
            })

acdc_conv = pd.DataFrame({
            '_B1MAP-QUIET_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map-fp', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_VFA_FA4-25_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'vfa', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_fa-4-25-tr-{tr}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI64_3SH_B0_B800_B2000_TOPUP_TE97_1p8mm3_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '64dir-3sh-800-2000', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_B0_TOPDN_TE97_1p8mm3_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topdn', 'scan_info': '6S0',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True,
                        'dwell_time': True, 'b1corr': False, 'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner',
                        'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_B0_TOPUP_TE97_1p8mm3_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '6S0', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_MEMP_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'fsmempr', 'scan_info': 'ti1200',        # 1.3S1.5P2200SI_OPTION_
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                        'dwell_time': False, 'b1corr': False, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': True},
            '_3DT2W_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_3DI_MC_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'angio', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_MT_MPF_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'mt', 'scan_info': 'mpf', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            })

tadpole_conv = pd.DataFrame({
            '_MEMP_VBM_TI1100_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'fsmempr', 'scan_info': 'ti1100',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                        'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': True},
            '_MATCHING_SV_': {'dirstruct': 'BIDS', 'outdir': 'mrs', 'scan_name': 'left_match_mrs', 'scan_info': 'ti1100',
                         'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                         'dwell_time': False, 'b1corr': False,
                         'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                         'minmax': ('parse', 'parse'), 'store_header': True,
                         'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                         'multisession': (1, 2, 3), 'rms': False},
            })
lilomom_conv = pd.DataFrame({
            '_B1MAP-QUIET_FC_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': 'fc', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_VFA_FA4-25_QUIET': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'vfa', 'scan_info': 'fa-4-25',   # hard code flip angles because vy patch can't assign correct values in PAR file
                                   'fname_template': '{subj}_{session}_{scan_name}_{scan_info}-tr-{tr}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_MT_MPF_QUIET': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'mt', 'scan_info': 'mpf',
                           'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                           'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                           'dwell_time': False, 'b1corr': False,
                           'field_strength': False, 'vol_info': False, 'origin': 'scanner',
                           'minmax': ('parse', 'parse'), 'store_header': True,
                           'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False,
                           'multisession': (1, 2, 3), 'rms': False},
            '_DWI64_3SH_B0_B800_B2000_TOPUP_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '64dir-3sh-800-2000', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_B0_TOPDN_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topdn', 'scan_info': '6S0',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True,
                        'dwell_time': True, 'b1corr': False, 'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner',
                        'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_B0_TOPUP_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '6S0', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            'MEMP_IFS_0p5mm_2echo_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'fsmempr', 'scan_info': 'ti1200',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                        'dwell_time': False, 'b1corr': False,'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True,'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': True},
            '_QUIET_3DT2W': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_3DI_MC_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'angio', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                         'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                         'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                         'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            })

lilobaby_conv = pd.DataFrame({
            '_B1MAP-QUIET_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map-fp', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_VFA_FA4-25_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'vfa', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_fa-4-25-tr-{tr}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI64_146FH_B0_B800_B2000_TOPUP_TE97_1p8mm3_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '64dir-3sh-800-2000', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_146FH_B0_TOPDN_TE97_1p8mm3_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topdn', 'scan_info': '6S0',
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True,
                        'dwell_time': True, 'b1corr': False, 'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner',
                        'minmax': ('parse', 'parse'), 'store_header': True, 'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False,
                        'multisession': (1, 2, 3), 'rms': False},
            '_DWI6_146FH_B0_TOPUP_TE97_1p8mm3_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'dwi-topup', 'scan_info': '6S0', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': True, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_MEMP_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'fsmempr', 'scan_info': 'ti1200',        # 1.3S1.5P2200SI_OPTION_
                        'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii', 'take_lowest_recon': True,
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False,
                        'dwell_time': False, 'b1corr': False, 'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'),
                        'store_header': True, 'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': True},
            '_3DT2W_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_3DI_MC_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'angio', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                        'take_lowest_recon': True, 'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            '_MT_MPF_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'mt', 'scan_info': 'mpf', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': True, 'multisession': (1, 2, 3), 'rms': False},
            })

#new project DataFrame objects to be added to Panel here
img_conv = {'phantom_qT1_slu': slu_phant_conv,
            'phantom_qT1_disc': disc_phant_conv,
            'self_control': self_control_conv,
            'roots_of_empathy': roots_conv,
            'bbc': bbc_conv,
            'nbwr': nbwr_conv,
            'tadpole': tadpole_conv,
            'genz': genz_conv,
            'acdc': acdc_conv,
            'lilomom': lilomom_conv,
            'lilobaby': lilobaby_conv,
            }

opts = BrainOpts()

def set_opts(opt_series): #function to extract params from dataframe
    for index, row in opt_series.items():
        setattr(opts, index, row)

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        print('Structure is empty. skipping...')
        return True

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

def find_subjs2conv(project, idthresh=800, leadalphan=False, wild_multipl=1):

    if leadalphan:
        wild = '?' * len(str(idthresh)) + '?' * wild_multipl
    else:
        wild = '?' * len(str(idthresh))
    converted = sorted(get_h5_keys(fs/project/'all_{project}_info.h5'.format(**{'project': project}), 'conv'))
    conv_subj_ses = sorted(['/'.join(x.split('/')[1:3]) for x in sorted(converted) if int(x.split('/')[1][-len(str(idthresh)):]) < idthresh])
    subjid_list_dirs = sorted(list((fs/project).glob('sub-{project}{wild}'.format(**{'project': project, 'wild': wild}))))
    subjid_list_dirs_wses, hassesdir = [], []
    for sid_ses_dirs in subjid_list_dirs:
        for s in img_conv[project][img_conv[project].keys()[0]]['multisession']:
            subjid_list_dirs_wses.append(sid_ses_dirs.joinpath('ses-'+str(s)))
    for d in subjid_list_dirs_wses:
        if d.is_dir() and int(d.parts[-2][-len(str(idthresh)):]) < idthresh:
            hassesdir.append('/'.join(d.parts[-2:]))
    subjects = sorted([x.split('/')[0] for x in list(set(hassesdir) - set(conv_subj_ses))])
    return subjects

def conv_subjs(project, subjects, hdf_fname=None):
    niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    niftiDF = pd.DataFrame()
    if project not in img_conv:
        raise ValueError(project+" not in img_conv dictionary. Please check brain_convert module.")
    setattr(opts, 'proj', project)
    scans = img_conv[project]
    scans.dropna(axis=1, how='all', inplace=True)
    # 1st make backup links
    backup_source_dirs(project, subjects)
    # loop over subjects in project
    for subject in subjects:
        subj_dd = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        setattr(opts, 'subj', subject)
        for scan in scans:                 #col loop is individual scans
            if all(scans[scan].isnull()) == True:
                continue
            setattr(opts, 'scan', scan)
            set_opts(scans[scan])
            subj_dd = brain_proc_file(opts, subj_dd)
        if not is_empty(subj_dd):
            subjDF = make_sessions_fm_dict(subj_dd, project, subject)
            niftiDF = niftiDF.append(subjDF, sort=True)
            niftiDict = mergeddicts(niftiDict, subj_dd)
            # save scan info to hdf info file for pipelines
            if not hdf_fname == None:
                conv_df2h5(subjDF, Path(hdf_fname), append=False)
            elif hdf_fname == None:
                conv_df2h5(subjDF, Path(fs / project / ('all_'+project+'_info.h5')), append=False)
            else:
                raise ValueError('missing hdf file name.')
    return niftiDict, niftiDF

def get_dwi_picks(project, idthresh=800, leadalphan=False, wild_multipl=1, excluded=[]):
    """

    :param project:  name of project as in 'acdc' or 'genz'
    :param idthresh:  threshold integer subj id number above which is excluded as in test subjs or devel scans
    :param leadalphan:  True only if 1 or more letters precede id number and not in project name eg C6124
    :param wild_multipl:  default is 1 letter before id number, change if more than 1 qualifier letter as in CG6124 = 2
    :param excluded:  list of subject/session combos to exclude from picks lists
    :return:  auto_qc_picks, vis_qc_picks, preproc_picks
    :auto_qc_picks: are the subjects that haven't had the auto qc script run\n
    :vis_qc_picks: are the subjects who have had the auto_qc run but NOT the visual qc\n
    :preproc_picks: are the subjects who have had BOTH the auto_qc AND the visual qc run but have NOT been pre processed\n
    """
    if project == 'genz' and excluded == []:
        excluded = ['sub-genz403/ses-1', 'sub-genz301/ses-1', 'sub-genz309/ses-1',]   ## has bad or no  dwi
    if leadalphan:
        wild = '?' * len(str(idthresh)) + '?' * wild_multipl
    else:
        wild = '?' * len(str(idthresh))
    auto_qc_subjs = sorted(get_h5_keys(fs/project/'all_{project}_info.h5'.format(**{'project': project}), 'auto_qc'))
    auto_qc_subjs = sorted(['/'.join(x.split('/')[1:3]) for x in sorted(auto_qc_subjs) if int(x.split('/')[1][-len(str(idthresh)):]) < idthresh])
    vis_qc_subjs = sorted(get_h5_keys(fs/project/'all_{project}_info.h5'.format(**{'project': project}), 'vis_qc'))
    vis_qc_subjs = sorted(['/'.join(x.split('/')[1:3]) for x in sorted(vis_qc_subjs) if int(x.split('/')[1][-len(str(idthresh)):]) < idthresh])
    subjid_list_dirs = sorted(list((fs/project).glob('sub-{project}{wild}'.format(**{'project': project, 'wild': wild}))))
    all_subjids = sorted([Path(x.parts[-1]) for x in subjid_list_dirs if int(x.parts[-1][-len(str(idthresh)):]) < idthresh])
    all_subjids_ses, has_ses, hasbedpdir = [], [], []
    for s in all_subjids:
        for sn in img_conv[project][img_conv[project].keys()[0]]['multisession']:
            all_subjids_ses.append(s.joinpath('ses-'+str(sn)))
    for s in all_subjids_ses:
        if (fs/project).joinpath(s, 'dwi/bedpost.bedpostX').is_dir():
            hasbedpdir.append(str(s))
        if (fs/project).joinpath(s, 'dwi').is_dir():
            has_ses.append(str(s))

    no_auto_qc = sorted(list(set(has_ses) - set(auto_qc_subjs) - set(excluded)))
    no_vis_qc = sorted(list(set(auto_qc_subjs) - set(vis_qc_subjs) - set(excluded)))
    no_preproc = sorted(list(set(vis_qc_subjs) - set(hasbedpdir) - set(excluded)))
    auto_qc_picks, vis_qc_picks, preproc_picks = [], [], []
    for p in no_auto_qc:
        auto_qc_picks.append({'subj': p.split('/')[0], 'session': p.split('/')[1], 'run': '1', })
    for p in no_vis_qc:
        vis_qc_picks.append('/'+p+'/dwi/auto_qc')
    for p in no_preproc:
        preproc_picks.append({'subj': p.split('/')[0], 'session': p.split('/')[1], 'run': '1', })
    return auto_qc_picks, vis_qc_picks, preproc_picks



# this is now obsolete with new b1map
def b1corr_anat(project, niftiDict):
    """
    now obsolete with new b1map methods
    :param project:
    :param niftiDict:
    :return:
    """
    for akey in niftiDict.keys():
        if akey[2] == 'anat':
            for bkey in niftiDict[akey].keys():
                if niftiDict[akey][bkey]['b1corr']:
                    fmap_akey = (akey[0], akey[1], 'fmap')
                    #this will only handle b1 maps. B0 maps in same session are conflicted here.
                    if len(niftiDict[fmap_akey].keys()) != 1:
                        raise ValueError('field map not found or not sure which one to use for '+str(fmap_akey))
                    fmap_bkey = niftiDict[fmap_akey].keys()[0]
                    b1map_fname = niftiDict[fmap_akey][fmap_bkey]['b1map2'+niftiDict[akey][bkey]['scan_name']+'_fname']
                    if not os.path.isfile(b1map_fname):
                        ref = niftiDict[akey][bkey]['outfilename']
                        outmat_fname = join(niftiDict[fmap_akey][fmap_bkey]['outpath'], fmap_bkey + '_b1mag2' +
                                                   niftiDict[akey][bkey]['scan_name']+'.mat')
                        outmat_key = 'b1mag2' + niftiDict[akey][bkey]['scan_name']+'_mat_fname'
                        flt.inputs.in_file = niftiDict[fmap_akey][fmap_bkey]['outfilename']
                        flt.inputs.reference = ref
                        flt.inputs.out_matrix_file = outmat_fname
                        res = flt.run()
                        niftiDict[fmap_akey][fmap_bkey][outmat_key] = outmat_fname
                        phase_fname = join(niftiDict[fmap_akey][fmap_bkey]['outpath'],fmap_bkey + '_b1phase')
                        cmd = ['fslroi', niftiDict[fmap_akey][fmap_bkey]['outfilename'], phase_fname, 2, 1]
                        subprocess.check_call(cmd, shell=True)
                        niftiDict[fmap_akey][fmap_bkey]['phase_fname'] = phase_fname
                        applyxfm.inputs.in_matrix_file = niftiDict[fmap_akey][fmap_bkey][outmat_key]
                        applyxfm.inputs.in_file = niftiDict[fmap_akey][fmap_bkey]['phase_fname']
                        base_b1phase2_fname = phase_fname + '2' + niftiDict[akey][bkey]['scan_name']
                        applyxfm.inputs.out_file = base_b1phase2_fname + '.nii'
                        applyxfm.inputs.reference = ref
                        applyxfm.inputs.apply_xfm = True
                        result = applyxfm.run()
                        cmd = ['fslmaths', base_b1phase2_fname, '-s', 6, base_b1phase2_fname + '_s6']
                        subprocess.check_call(cmd, shell=True)
                        niftiDict[fmap_akey][fmap_bkey][b1map_fname] = base_b1phase2_fname + '.nii.gz'
                        niftiDict[fmap_akey][fmap_bkey][b1map_fname] = base_b1phase2_fname + '.nii.gz'
                        provenance.log(niftiDict[fmap_akey][fmap_bkey][b1map_fname], 'b1map registered to '+ bkey, \
                                   niftiDict[fmap_akey][fmap_bkey]['outfilename'], script=__file__, opts=opts)

                    cmd = ['fslmaths', niftiDict[akey][bkey]['outfilename'],'-div', \
                              niftiDict[fmap_akey][fmap_bkey][b1map_fname], '-mul', 100, \
                              join(niftiDict[akey][bkey]['outpath'], bkey + '_b1corr')]
                    subprocess.check_call(cmd, shell=True)
                    niftiDict[akey][bkey]['b1corr_fname'] = join(niftiDict[akey][bkey]['outpath'], bkey + '_b1corr.nii.gz')
                    b1corrDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
                    b1corr_middlekey = bkey + '_b1corr'
                    b1corrDict[akey][b1corr_middlekey] = niftiDict[akey][bkey]
                    b1corrDict[akey][b1corr_middlekey]['outfilename'] = join(niftiDict[akey][bkey]['outpath'], bkey + '_b1corr.nii.gz')
                    b1corrDict[akey][b1corr_middlekey]['basefilename'] = bkey + '_b1corr.nii.gz'
                    b1corrDict[akey][b1corr_middlekey]['qform'] = nibabel.load(b1corrDict[akey][b1corr_middlekey]['outfilename']).get_affine()
                    b1corrDict[akey][b1corr_middlekey]['b1corr'] = False
                    mergeddicts(niftiDict, b1corrDict)
    return niftiDict