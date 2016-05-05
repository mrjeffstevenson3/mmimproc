from collections import defaultdict
import pandas as pd
from nibabel.mriutils import calculate_dwell_time
import dill #to use as pickle replacement of lambda dict
#call function that knows pardict[parfile] with parfiledictkey
def convfilepath(projectdir, parfiledictkey, dirstruct):
    if dirstruct == 'legacy':
        outdir = join(projectdir, subjid, method)
    elif dirstruct == 'BIDS':
        outdir = join(projectdir, 'sub-{0}'.format(parfiledictkey['subjid']), '{0}'.format(parfiledictkey['method']))
    else:
        raise ValueError('Unknown directory structure: '+str(dirstruct))
    fnametem = 'sub-{0}_{1}.nii.gz'.format(parfiledictkey['subjid'], parfiledictkey['techinfo'])
    return join(outdir, fnametem)

protocol_dict = defaultdict(lambda: defaultdict(list))
#reference image dims and origin all others will be centered on
ref_img = 'xxxxMNI152adult_T1_1mm_head.nii.gz'
a = [(ref_img, {'zcutoff': 8, 'ztrans': 0, 'meg_vox_origin': (90, 104, 30), 'xrot': -18, 'origdims': (182, 218, 182)}),
     ('ANTS6-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 48, 'meg_vox_origin': (71, 80, 60), 'xrot': -16, 'origdims': (147, 170, 176)}),
     ('ANTS12-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 50, 'meg_vox_origin': (74, 93, 68), 'xrot': -22, 'origdims': (149, 178, 190)}),
     ('K13714-0Months_301_WIP_QUIET_MPRAGE_ti1450_head.nii.gz', {'zcutoff': 70, 'meg_vox_origin': (73, 93, 66), 'xrot': -22, 'origdims': (150, 256, 256)}),
     ('ANTS15-0Months_head_bias_corrected.nii.gz', {'zcutoff': 20, 'meg_vox_origin': (80, 90, 41), 'xrot': -22, 'origdims': (150, 180, 155)}),
     ('ANTS18-0Months_head_bias_corrected.nii.gz', {'zcutoff': 19, 'meg_vox_origin': (80, 92, 40), 'xrot': -26, 'origdims': (150, 256, 256)}),
     ('ANTS2-0Years_head_bias_corrected.nii.gz', {'zcutoff': 13, 'meg_vox_origin': (72, 88, 32), 'xrot': -24, 'origdims': (150, 256, 256)}),
     ('ANTS2-5Years_head_bias_corrected.nii.gz', {'zcutoff': 19, 'meg_vox_origin': (75, 87, 38), 'xrot': -18, 'origdims': (150, 256, 256)}),
     ('ANTS3-0Years_head_bias_corrected.nii.gz', {'zcutoff': 22, 'meg_vox_origin': (80, 95, 44), 'xrot': -22, 'origdims': (150, 256, 256)}),
     ('ANTS4-0Years_head_bias_corrected.nii.gz', {'zcutoff': 18, 'meg_vox_origin': (75, 83, 37), 'xrot': -14, 'origdims': (150, 256, 256)}),
      ]
for i in a:
    protocol_dict[i[0]] = i[1]

#subjid = '_'.join(parfile.split('_')[0:parfile.split('_').index('WIP')])
#techinfo = '_'.join(parfile.split('_')[parfile.split('_').index('WIP')+1:parfile.split('_').index('SENSE')])

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
disc_phant_conv = pd.DataFrame({'_B1MAP_': {'--output-dir': 'fmap', '--compressed': False, '--permit-truncated': False, '--bvs': False, '--dwell-time': False,
                        '--field-strength': False, '--origin': 'scanner', '--minmax': 'parse parse', '--store-header': True,
                        '--scaling': 'dv', '--keep-trace': False, '--overwrite': True, '--strict-sort': False},
            '_3D_SPGR_': {'--output-dir': 'anat', '--compressed': False, '--permit-truncated': False, '--bvs': False, '--dwell-time': False,
                        '--field-strength': False, '--origin': 'scanner', '--minmax': 'parse parse', '--store-header': True,
                        '--scaling': 'fp', '--keep-trace': False, '--overwrite': True, '--strict-sort': False},
            '_IR': {'--output-dir': 'anat', '--compressed': False, '--permit-truncated': False, '--bvs': False, '--dwell-time': False,
                        '--field-strength': False, '--origin': 'scanner', '--minmax': 'parse parse', '--store-header': True,
                        '--scaling': 'fp', '--keep-trace': False, '--overwrite': True, '--strict-sort': False},
            })

self_control_conv = pd.DataFrame({'_B1MAP_': {'--output-dir': 'fmap', '--compressed': False, '--permit-truncated': False, '--bvs': False, '--dwell-time': False,
                        '--field-strength': False, '--origin': 'scanner', '--minmax': 'parse parse', '--store-header': True,
                        '--scaling': 'dv', '--keep-trace': False, '--overwrite': True, '--strict-sort': False},
            '_3D_SPGR_': {'--output-dir': 'anat', '--compressed': False, '--permit-truncated': False, '--bvs': False, '--dwell-time': False,
                        '--field-strength': False, '--origin': 'scanner', '--minmax': 'parse parse', '--store-header': True,
                        '--scaling': 'fp', '--keep-trace': False, '--overwrite': True, '--strict-sort': False},
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

if project not in img_conv:
    raise error:



class AnyOpts(object):
    pass

opts = AnyOpts()


def set_opts(opt_dict): #function to extract params from dataframe
    for index, row in opt_dict.iteritems():
        setattr(opts, index, row)
    print opts.scaling

for col in slu_conv:
    set_opts(slu_conv[col])
