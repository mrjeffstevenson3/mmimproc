from collections import defaultdict
import pandas as pd
import dill #to use as pickle replacement of lambda dict
#call function that knows pardict[parfile] with parfiledictkey
def convfilepath(projectdir, parfiledictkey, dirstruct):
    if dirstruct == 'legacy':
        outdir = join(projectdir, subjid, method)
    elif dirstruct == 'BIDS':
        outdir = join(projectdir, 'sub-{0}'.format(parfiledictkey['subjid']), '{0}'.format(parfiledictkey['method'])
    else:
        raise ValueError('Unknown directory structure: '+str(dirstruct))
    fnametem = 'sub-{0}_{1}.nii.gz'.format(parfiledictkey['subjid'], parfiledictkey['techinfo'])
    return join(outdir, fnametem)

protocol_dict = defaultdict(lambda: defaultdict(list))

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

subjid = '_'.join(parfile.split('_')[0:parfile.split('_').index('WIP')])
techinfo = '_'.join(parfile.split('_')[parfile.split('_').index('WIP')+1:parfile.split('_').index('SENSE')])


img_conv = {'phantom_qT1_slu': pd.DataFrame(),
            'phantom_qT1_disc': pd.DataFrame(),
            'self_control': pd.DataFrame(),
            'roots_of_empathy': pd.DataFrame()}