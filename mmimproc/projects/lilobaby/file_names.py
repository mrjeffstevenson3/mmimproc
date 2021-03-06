# todo: make roll_brain_to_com function with affine transform outfile to place brain at center of image for ANTS.
# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy
# todo: vfa fa 25 ec 1 brain extract factor 0.5 best on S220

# here there are no subj ids, those are called out by the picks list inside SubjIdPicks object.

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for session and run numbers are set here as  well as exceptions to those defaults called out by subject and modality.
import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
import numpy as np
from mmimproc.utils import *
from mmimproc.conversion.brain_convert import img_conv, lilobaby_conv, mergeddicts
from mmimproc.io.mixed import getTRfromh5

fs = mmimproc.fs_local
project = 'lilobaby'
dwi_excluded = {project: []}


class SubjIdPicks(object):
    pass

class Optsd(object):
    """
    Define constants for genz project with dict like mapping using opts = Optsd; **vars(opts).
    """
    def __init__(self,
            # define project global parameters here. will become dict using opts = Optsd(); vars(opts).
            project = 'genz',
            test = True,
            ext = '.nii.gz',
            overwrite = True,
            convert = False,
            spm_thresh = 0.80,
            fsl_thresh = 0.20,
            info_fname = fs / project / ('all_' + project + '_info.h5'),
            dwi_pass_qc = '_passqc',
            dwi_qc_b0_alpha = 3.0,
            dwi_qc_b2000_alpha = 3.0,
            dwi_qc_b800_alpha = 3.0,
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
            gaba_ftempl = '{subj}_WIP_ACCGABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT',
            b1corr = False,
            b1maptr = np.array([60., 240.0]),
            vfa_tr = 21.0,
            vfa_fas = [4.0, 25.0],
            vfa_pr_shape = (384,384,290),  # was (384,384,323) changed 290 for dims in vfa
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
        self.dwi_pass_qc = dwi_pass_qc
        self.dwi_qc_b0_alpha = dwi_qc_b0_alpha,
        self.dwi_qc_b2000_alpha = dwi_qc_b2000_alpha,
        self.dwi_qc_b800_alpha = dwi_qc_b800_alpha,
        self.mf_str = mf_str
        self.info_fname = info_fname
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

#unused sofar
mod_map = {'T2': '_3DT2W_', 'lt_match': '_AX_MATCH_LEFT_MEMP_VBM_TI1100_', 'rt_match': '_AX_MATCH_RIGHT_MEMP_VBM_TI1100_', 'b1map': '_B1MAP_',
          'dwi': '_DWI64_3SH_B0_B800_B2000_TOPUP_', 's0_up': '_DWI_B0_TOPDN_', 's0_dn': '_DWI_B0_TOPUP_', 'mpr': '_MEMP_FS_TI1100_', 'spgr': '_T1_MAP_'}

def get_freesurf_names(subjids_picks):
    fs_picks = []
    b1_ftempl = removesuffix(str(lilobaby_conv['_B1MAP-QUIET_']['fname_template']))
    fs_ftempl = removesuffix(str(lilobaby_conv['_MEMP_']['fname_template']))
    for subjid in subjids_picks.subjids:
        subjid['b1map_fname'] = str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_B1MAP-QUIET_']))
        subjid['freesurf_fname'] = str(fs_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_MEMP_'], dict3={'scan_info': 'ti1200_rms'}))
        fs_picks.append(mergeddicts(subjid, vars(opts)))
    return fs_picks

def get_dwi_names(subjids_picks):
    dwi_picks = []
    try:
        topup_ftempl = removesuffix(str(lilobaby_conv['_DWI6_146FH_B0_TOPUP_TE97_1p8mm3_']['fname_template']))
        topdn_ftempl = removesuffix(str(lilobaby_conv['_DWI6_146FH_B0_TOPDN_TE97_1p8mm3_']['fname_template']))
        dwi_ftempl = removesuffix(str(lilobaby_conv['_DWI64_146FH_B0_B800_B2000_TOPUP_TE97_1p8mm3_']['fname_template']))
        for subjid in subjids_picks.subjids:
            subjid['project'] = opts.project
            subjid['topup_fname'] = str(topup_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI6_146FH_B0_TOPUP_TE97_1p8mm3_']))
            subjid['topdn_fname'] = str(topdn_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI6_146FH_B0_TOPDN_TE97_1p8mm3_']))
            subjid['dwi_fname'] = str(dwi_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI64_146FH_B0_B800_B2000_TOPUP_TE97_1p8mm3_']))
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

def get_3dt2_names(subjids_picks):
    t2_picks = []
    t2_ftempl = removesuffix(str(img_conv[project]['_3DT2W_']['fname_template']))
    for subjid in subjids_picks.subjids:
        subjid['t2_fname'] = str(t2_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_3DT2W_']))
        t2_picks.append(subjid)
    return t2_picks

def get_vfa_names(subjids_picks):
    qt1_picks = []
    b1_ftempl = str(removesuffix(str(lilobaby_conv['_B1MAP-QUIET_']['fname_template'])))
    vfa_ftempl = str(removesuffix(str(lilobaby_conv['_VFA_FA4-25_']['fname_template'])))
    for subjid in subjids_picks.subjids:
        subjid.update({'scan_name': lilobaby_conv['_VFA_FA4-25_']['scan_name'], 'tr': '21p0', 'wild': '*'})
        # add bids dirs to dict
        subjid['anat_path'] = fs/project/'{subj}/{session}/anat'.format(**subjid)
        subjid['dwi_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid)
        subjid['vtk_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.vtk_dir
        subjid['eddy_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.eddy_corr_dir
        subjid['fits_path'] = fs / project / '{subj}/{session}/dwi'.format(**subjid) / opts.dwi_fits_dir
        subjid['qt1_path'] = fs / project / '{subj}/{session}/qt1'.format(**subjid)
        subjid['reg2dwi_path'] = fs / project / '{subj}/{session}/reg/'.format(**subjid) / opts.qt12dwi_reg_dir
        subjid['vfa_fname'] = vfa_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=lilobaby_conv['_VFA_FA4-25_']))
        subjid['b1map_fname'] = b1_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=lilobaby_conv['_B1MAP-QUIET_']))
        if opts.info_fname.is_file():
            subjid['vfatr'] = getTRfromh5(opts.info_fname, subjid['subj'], subjid['session'], 'qt1', vfa_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=lilobaby_conv['_VFA_FA4-25_'])))
            subjid['b1maptr'] = getTRfromh5(opts.info_fname, subjid['subj'], subjid['session'], 'fmap', b1_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=lilobaby_conv['_B1MAP-QUIET_'])))
        else:
            print('cannot find all_genz_info.h5 file. using fixed defaults: vfa TR=21.0 and b1map TR = 60.0 and 240.0')
            subjid['vfatr'] = 21.0
            subjid['b1maptr'] = np.array([60., 240.0])
        subjid['vfa_fas'] = opts.vfa_fas
        subjid['topup_brain_fname'] = str(removesuffix(str(lilobaby_conv['_DWI6_146FH_B0_TOPUP_TE97_1p8mm3_']['fname_template']))). \
                                    format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI6_146FH_B0_TOPUP_TE97_1p8mm3_'])) +\
                                    '_topdn_concat_mf_unwarped_mean_brain'
        if subjids_picks.getR1_MPF_nii_fnames:
            subjid['r1_fname'] = subjids_picks.r1_fname_templ.format(**subjid)
            subjid['mpf_fname'] = subjids_picks.mpf_fname_templ.format(**subjid)
            subjid['topup_ftempl'] = removesuffix(str(lilobaby_conv['_DWI6_146FH_B0_TOPUP_TE97_1p8mm3_']['fname_template']))
            subjid['UKF_fname'] = '{subj}_{session}_dwi-topup_64dir-3sh-800-2000_1_topdn_unwarped_ec_mf_clamp1_UKF_whbr.vtk'.format(**subjid)
        if subjids_picks.get_analyse_R1_MPF_names:
            r1_img_files = list(subjid['qt1_path'].glob(subjids_picks.orig_r1_fname_templ.format(**subjid)))
            mpf_img_files = list(subjid['qt1_path'].glob(subjids_picks.orig_mpf_fname_templ.format(**subjid)))
            if len(r1_img_files) == len(mpf_img_files) == 1:
                subjid['orig_r1_fname'] = r1_img_files[0]
                subjid['orig_mpf_fname'] = mpf_img_files[0]
            else:
                raise ValueError('found more than 1 R1 ({lenr1}) or MPF ({lenmpf}).img file. ambiguous choice. Please have only one matching .img file for each in qt1 dir.'.format({'lenr1': len(r1_img_files), 'lenmpf': len(mpf_img_files)}))
        qt1_picks.append(mergeddicts(subjid, vars(opts)))
    return qt1_picks
