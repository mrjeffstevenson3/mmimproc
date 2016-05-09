#test to process conversion settings to opts object
from pylabs.conversion.parrec2nii_convert import BrainOpts
import pandas as pd
from pylabs.conversion.parrec2nii_convert import brain_proc_file
from collections import defaultdict

#individual project parameters to be set once here. keys are immutable or code will break.
slu_phant_conv = pd.DataFrame({'_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{}_b1map.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'verbose': True, 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{}_spgr_fa_{}_tr_{}_{}.nii',
                        'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_IR': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'seir', 'scan_info': '', 'fname_template': '',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            })
disc_phant_conv = pd.DataFrame({'_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{}_b1map.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'verbose': True, 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{}_spgr_fa_{}_tr_{}_{}.nii',
                        'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_IR': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'seir', 'scan_info': '', 'fname_template': '',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            })

self_control_conv = pd.DataFrame({'_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{}_b1map',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{}_spgr_fa_{}_tr_{}_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            })

roots_conv = pd.DataFrame({'_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{}_b1map',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_T1_MAP_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{}_spgr_fa_{}_tr_{}_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_TOPUP_DTI_32DIR_B1850_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'topup', 'scan_info': '32dir_b1850', 'fname_template': '{}_topup_32dir_b1850_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_TOPDN_DTI_31DIR_B1850_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'topdn', 'scan_info': '32dir_b1850', 'fname_template': '{}_topdn_31dir_b1850_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_WE_MEMPRAGE_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'wemempr', 'scan_info': '', 'fname_template': '{}_wemempr_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_MEMP_VBM_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'vbmmempr', 'scan_info': '', 'fname_template': '{}_vbmmempr_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            '_3DT2W_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{}_3dt2_{}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': 'parse parse', 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False},
            })

#new project DataFrame objects to be added to Panel here
img_conv = pd.Panel({'phantom_qT1_slu': slu_phant_conv,
            'phantom_qT1_disc': disc_phant_conv,
            'self_control': self_control_conv,
            'roots_of_empathy': roots_conv})

opts = BrainOpts()
niftidict = {}

def set_opts(opt_series): #function to extract params from dataframe
    for index, row in opt_series.iteritems():
        setattr(opts, index, row)

def conv_subj(project, subjects, niftiDict=None):
    #loops over subjects for a single project
    if niftiDict is None:
        niftiDict = defaultdict(list)
    if project not in img_conv:
        raise ValueError(project+" not in img_conv Panel. Please check")
    setattr(opts, 'proj', project)
    scans = img_conv[project]
    for subject in subjects:
        setattr(opts, 'subj', subject)
        for scan in scans:
            #col loop is scans
            setattr(opts, 'scan', scan)
            set_opts(scans[scan])
            niftiDict = brain_proc_file(**opts)
    return niftiDict
