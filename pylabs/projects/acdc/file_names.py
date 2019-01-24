# here there are no subj ids, those are called out by the picks list inside SubjIdPicks object.

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for project, session and run numbers are set in class Optsd used in all pipelines as  well as exceptions to those defaults called out by subject and modality.
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import numpy as np
from pylabs.io.mixed import getTRfromh5
from pylabs.utils import *
from pylabs.conversion.brain_convert import acdc_conv, img_conv, is_empty

fs = Path(getnetworkdataroot())
project = 'acdc'
dwi_excluded = {project: []}

class SubjIdPicks(object):
    pass

class Optsd(object):
    """
    Define constants for acdc project with dict like mapping using opts = Optsd; **vars(opts).
    """
    def __init__(self,
            # define project global parameters here. will become dict using opts = Optsd; vars(opts).
            project = 'acdc',
            test = False,
            ext='.nii.gz',
            overwrite = True,
            convert = False,
            spm_thresh = 0.80,
            fsl_thresh = 0.20,
            info_fname = fs / project / ('all_' + project + '_info.h5'),
            dwi_qc = True,
            dwi_pass_qc = '_passqc',
            dwi_qc_b0_alpha = 3.0,
            dwi_qc_b2000_alpha = 3.0,
            dwi_qc_b800_alpha = 3.0,
            dwi_subj_excluded = [],
            mf_str = '_mf',    # set to blank string '' to disable median filtering
            run_topup = True,
            dwi_add_blanks = True,
            eddy_corr = True,
            dwi_bet_ffac = 0.5,                     # fsl bet f factor threshold for mean topup brain (empirical)
            eddy_corr_dir = 'eddy_cuda_repol_v1',   # output dir for eddy
            dwi_fits_dir = 'fits_v1',
            do_ukf = True,
            vtk_dir = 'vtk_v1',
            MNI2dwi_reg_dir = 'MNI2dwi',
            qt12dwi_reg_dir = 'qt12dwi',
            run_bedpost = True,
            dwi_bedpost_dir = 'bedpost',
            dwi_fname_excep = ['_DWI64_3SH_B0_B800_B2000_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPDN_TE101_1p8mm3_'],
            gaba_te = 80,
            gaba_dyn = 120,
            gaba_ftempl = '{subj}_WIP_{side}GABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT',
            b1corr = False,
            b1maptr = np.array([60., 240.0]),
            vfa_tr = 21.0,
            vfa_fas = [4.0, 25.0],
            vfa_pr_shape = (384, 384, 323),
            vfa_subj_excluded = [],
            vfa_run2 = [],
            mpf_img_dtype = np.int16,
            reg_mni2dwi = '{fs}/{project}/{subj}/{session}/reg/mni2dwi',
            reg_qt12dwi = '{fs}/{project}/{subj}/{session}/reg/qt12dwi',
            JHU_thr = 5,
            stat_thr = 0.95,
            ants_args = ['-n 30', '-t s', '-p f', '-j 1', '-s 10', '-r 1']
            ):
        # make them accessible as obj.var as well as dict
        self.project = project
        self.test = test
        self.ext = ext
        self.overwrite = overwrite
        self.convert = convert
        self.spm_thresh = spm_thresh
        self.fsl_thresh = fsl_thresh
        self.info_fname = info_fname
        self.dwi_qc = dwi_qc
        self.dwi_pass_qc = dwi_pass_qc
        self.dwi_qc_b0_alpha = dwi_qc_b0_alpha
        self.dwi_qc_b2000_alpha = dwi_qc_b2000_alpha
        self.dwi_qc_b800_alpha = dwi_qc_b800_alpha
        self.dwi_subj_excluded = dwi_subj_excluded
        self.mf_str = mf_str
        self.run_topup = run_topup
        self.dwi_add_blanks = dwi_add_blanks
        self.eddy_corr = eddy_corr
        self.dwi_bet_ffac = dwi_bet_ffac
        self.eddy_corr_dir = eddy_corr_dir
        self.dwi_fits_dir = dwi_fits_dir
        self.do_ukf = do_ukf
        self.vtk_dir = vtk_dir
        self.MNI2dwi_reg_dir = MNI2dwi_reg_dir
        self.qt12dwi_reg_dir = qt12dwi_reg_dir
        self.run_bedpost = run_bedpost
        self.dwi_bedpost_dir = dwi_bedpost_dir
        self.dwi_fname_excep = dwi_fname_excep
        self.gaba_te = gaba_te
        self.gaba_dyn = gaba_dyn
        self.gaba_ftempl = gaba_ftempl
        self.b1corr = b1corr
        self.b1maptr = b1maptr
        self.vfa_tr = vfa_tr
        self.vfa_fas = vfa_fas
        self.vfa_pr_shape = vfa_pr_shape
        self.vfa_subj_excluded = vfa_subj_excluded
        self.vfa_run2 = vfa_run2
        self.mpf_img_dtype = mpf_img_dtype
        self.reg_mni2dwi = reg_mni2dwi
        self.reg_qt12dwi = reg_qt12dwi
        self.JHU_thr = JHU_thr
        self.stat_thr = stat_thr
        self.ants_args = ants_args

"""
# other future stages to run to move to opts settings
subT2 = False   #wip ??
bet = False
prefilter = False
templating = False
"""

opts = Optsd()

# for partial substitutions
fname_templ_dd = {'subj': '{subj}', 'session': '{session}', 'scan_name': '{scan_name}', 'scan_info': '{scan_info}',
                  'run': '{run}', 'fa': '{fa}', 'tr': '{tr}', 'side': '{side}', 'te': '{te}', 'dyn': '{dyn}',
                  'wild': '{wild}', 'type': '{type}'}

def set_fname_templ_dd(dd, d):
    for k in d.keys():
        dd[k] = d[k]
    return dd

def reset_fname_templ_dd(dd):
    for k in dd.keys():
        dd[k] = '{'+k+'}'
    return dd

def merge_ftempl_dicts(dict1={}, dict2={}, dict3={}, base_dd=fname_templ_dd):
    nd = base_dd.copy()   # start with base default dict fname_templ_dd's keys and values
    nd.update(dict1)
    nd.update(dict2)
    nd.update(dict3)  # modifies base dict with dict1 2 and 3 keys and values
    return nd

def get_freesurf_names(subjids_picks):
    fs_picks = []
    b1_ftempl = removesuffix(str(genz_conv['_B1MAP-QUIET_FC_']['fname_template']))
    fs_ftempl = removesuffix(str(genz_conv['MEMP_IFS_0p5mm_2echo_']['fname_template']))
    for subjid in subjids_picks.subjids:
        subjid['b1map_fname'] = str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_B1MAP-QUIET_FC_']))
        subjid['freesurf_fname'] = str(fs_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['MEMP_IFS_0p5mm_2echo_'], dict3={'scan_info': 'ti1200_rms'}))
        fs_picks.append(mergeddicts(subjid, vars(opts)))
    return fs_picks

def get_dwi_names(subjids_picks):
    dwi_picks = []
    try:
        topup_ftempl = removesuffix(str(acdc_conv['_DWI6_B0_TOPUP_TE97_1p8mm3_']['fname_template']))
        topdn_ftempl = removesuffix(str(acdc_conv['_DWI6_B0_TOPDN_TE97_1p8mm3_']['fname_template']))
        dwi_ftempl = removesuffix(str(acdc_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_TE97_1p8mm3_']['fname_template']))
        for subjid in subjids_picks.subjids:
            if subjid['subj'] in opts.dwi_subj_excluded:
                continue
            subjid['topup_fname'] = str(topup_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI6_B0_TOPUP_TE97_1p8mm3_']))
            subjid['topdn_fname'] = str(topdn_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI6_B0_TOPDN_TE97_1p8mm3_']))
            subjid['dwi_fname'] = str(dwi_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_TE97_1p8mm3_']))
            subjid['anat_path'] = fs / project / '{subj}/{session}/anat'.format(**subjid)
            subjid['dwi_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid)
            subjid['vtk_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.vtk_dir
            subjid['eddy_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.eddy_corr_dir
            subjid['fits_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.dwi_fits_dir
            subjid['bedpost_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.dwi_bedpost_dir
            subjid['qt1_path'] = fs / project / '{subj}/{session}/qt1'.format(**subjid)
            dwi_picks.append(mergeddicts(subjid, vars(opts)))
        return dwi_picks
    except TypeError as e:
            print('subjids needs to a dictionary.')

def get_vfa_names(subjids_picks):
    qt1_picks = []
    b1_ftempl = str(removesuffix(str(acdc_conv['_B1MAP-QUIET_']['fname_template'])))
    vfa_ftempl = str(removesuffix(str(acdc_conv['_VFA_FA4-25_']['fname_template'])))
    for subjid in subjids_picks.subjids:
        subjid.update({'scan_name': acdc_conv['_VFA_FA4-25_']['scan_name'], 'tr': str(opts.vfa_tr).replace('.', 'p')})
        subjid['vfatr'] = getTRfromh5(str(fs/project/'all_acdc_info.h5'), subjid['subj'], subjid['session'], 'qt1', vfa_ftempl.format(**subjid))
        subjid['vfa_fname'] = vfa_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_VFA_FA4-25_']))
        subjid['b1map_fname'] = b1_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_B1MAP_']))
        subjid['b1maptr'] = getTRfromh5(str(fs / project / 'all_acdc_info.h5'), subjid['subj'], subjid['session'], 'fmap', b1_ftempl.format(**subjid))
        qt1_picks.append(subjid)
    return qt1_picks


def get_3dt2_names(subjids_picks):
    t2_picks = []
    t2_ftempl = removesuffix(str(img_conv[project]['_QUIET_3DT2W']['fname_template']))
    for subjid in subjids_picks.subjids:
        subjid['t2_fname'] = str(t2_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_QUIET_3DT2W']))
        t2_picks.append(mergeddicts(subjid, vars(opts)))
    return t2_picks