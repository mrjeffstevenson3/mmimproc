# todo: make roll_brain_to_com function with affine transform outfile to place brain at center of image fro ANTS.
# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

# here there are no subj ids, those are called out by the picks list inside SubjIdPicks object.

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for session and run numbers are set here as  well as exceptions to those defaults called out by subject and modality.
import pylabs
pylabs.datadir.target = 'scotty'
from pathlib import *
import numpy as np
from pylabs.utils import *
from pylabs.conversion.brain_convert import self_control_conv, is_empty
from pylabs.io.mixed import getTRfromh5

fs = Path('/media/DiskArray/shared_data/js/')
project = 'self_control/hbm_group_data/qT1'


class SubjIdPicks(object):
    pass

class Optsd(object):
    """
    Define constants for genz project with dict like mapping using opts = Optsd; **vars(opts).
    """
    def __init__(self,
            # define project variables here. will become dict using opts = Optsd; vars(opts).
            project = 'self_control/hbm_group_data/qt1',
            test = True,
            overwrite = True,
            convert = False,
            spm_thresh = 0.80,
            fsl_thresh = 0.20,
            info_fname = fs / 'self_control' / 'all_self_control_info.h5',
            dwi_pass_qc = '_passqc',
            mf_str = '_mf',    # set to blank string '' to disable median filtering
            run_topup = True,
            eddy_corr = True,
            eddy_corr_dir = 'eddy_cuda_repol_v1',   # output dir for eddy
            dwi_fits_dir = 'fits_v1',
            do_ukf = True,
            vtk_dir = 'vtk_v1',
            dwi_reg_dir = 'MNI2dwi',
            run_bedpost = True,
            dwi_bedpost_dir = 'bedpost',
            dwi_fname_excep = ['_DWI64_3SH_B0_B800_B2000_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPDN_TE101_1p8mm3_'],
            gaba_te = 80,
            gaba_dyn = 120,
            gaba_ftempl = '{subj}_WIP_ACCGABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT',
            b1corr = False,
            b1maptr = np.array([51.0, 120.0]),
            vfa_tr = 21.0,
            vfa_fas = [4.0, 25.0],
            spgr_tr = 11.0,
            spgr_fas = [2.0, 10.0, 20.0],
            qt1_source_dir = '{fs}/{project}/hbm_group_data/{subj}/{session}/qt1/mni2dwi',
            reg_mni2dwi = '{fs}/{project}/{subj}/{session}/reg/mni2dwi',
            reg_qt12dwi = '{fs}/{project}/{subj}/{session}/reg/qt12dwi',
            JHU_thr = 5,
            stat_thr = 0.95,
            ants_args = ['-n 30', '-t s', '-p f', '-j 1', '-s 10', '-r 1']
            ):
        # make them accessible as obj.var as well as dict
        self.project = project
        self.test = test
        self.overwrite = overwrite
        self.convert = convert
        self.spm_thresh = spm_thresh
        self.fsl_thresh = fsl_thresh
        self.dwi_pass_qc = dwi_pass_qc
        self.mf_str = mf_str
        self.info_fname = info_fname
        self.run_topup = run_topup
        self.eddy_corr = eddy_corr
        self.eddy_corr_dir = eddy_corr_dir
        self.dwi_fits_dir = dwi_fits_dir
        self.do_ukf = do_ukf
        self.vtk_dir = vtk_dir
        self.dwi_reg_dir = dwi_reg_dir
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
        self.spgr_tr = spgr_tr
        self.spgr_fas = spgr_fas
        self.qt1_source_dir = qt1_source_dir,
        self.reg_mni2dwi = reg_mni2dwi
        self.reg_qt12dwi = reg_qt12dwi
        self.JHU_thr = JHU_thr
        self.stat_thr = stat_thr
        self.ants_args = ants_args

opts = Optsd()

# for partial substitutions
fname_templ_dd = {'subjnum': '{subjnum}', 'subj': '{subj}', 'session': '{session}', 'scan_name': '{scan_name}', 'scan_info': '{scan_info}',
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

def get_spgr_names(subjids_picks):
    qt1_picks = []
    b1_ftempl = fs / project / 'scs{subjnum}/B1map_qT1/{subj}_WIP_B1MAP_SAG_TR51_TR120_60DEG_SPOIL120_SENSE_{wild}_1.nii'
    spgr_ftempl = fs / project / 'scs{subjnum}/source_nii/{subj}_WIP_T1_MAP_{fa}B_SENSE_{wild}_1.nii'
    for subjid in subjids_picks.subjids:
        subjid['wild'] = '*'
        subjid['project'] = project
        subjid['b1map_fname'] = list((Path(str(b1_ftempl).format(**subjid)).parent).glob(Path(str(b1_ftempl).format(**subjid)).name))[0]
        if not subjid['b1map_fname'].is_file():
            raise ValueError('file not found. {missing}'.format({'missing': subjid['b1map_fname']}))
        subjid['b1maptr'] = np.array([60., 120.0])
        subjid['spgr_fas'] = opts.spgr_fas
        subjid['spgr_tr'] = opts.spgr_tr
        for ifa in subjid['spgr_fas']:
            subjid['fa'] = str(int(ifa)).zfill(2)
            spgr_fname = list((Path(str(spgr_ftempl).format(**subjid)).parent).glob(Path(str(spgr_ftempl).format(**subjid)).name))[0]
            subjid['spgr%(fa)s_fname' % subjid] = spgr_fname
            if not spgr_fname.is_file():
                raise ValueError('file not found. {missing}'.format({'missing': spgr_fname}))
        qt1_picks.append(subjid)
    return qt1_picks
