# here there are no subj ids, those are called out by the picks list inside SubjIdPicks object.

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for project set in class Optsd used in all pipelines
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
from collections import defaultdict
from pylabs.io.mixed import getTRfromh5
from pylabs.utils import *
from pylabs.conversion.brain_convert import acdc_conv

fs = Path(getnetworkdataroot())
project = 'acdc'

class SubjIdPicks(object):
    pass

class Optsd(object):
    """
    Define constants for acdc project with dict like mapping using opts = Optsd; **vars(opts).
    """
    def __init__(self,
            # define project variables here. will become dict using opts = Optsd; vars(opts).
            project = 'acdc',
            test = False,
            overwrite = True,
            convert = False,
            spm_thresh = 0.80,
            fsl_thresh = 0.20,
            info_fname = fs / project / ('all_' + project + '_info.h5'),
            dwi_pass_qc = '_passqc',
            mf_str = '_mf',    # set to blank string '' to disable median filtering
            run_topup = False,
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
            gaba_ftempl = '{subj}_WIP_{side}GABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT',
            b1corr = False,
            b1maptr = np.array([60., 240.0]),
            vfa_tr = 21.0,
            vfa_fas = [4.0, 25.0],
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

qc_str = opts.dwi_pass_qc

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

# empty freesurfer, T2 file name lists
b1map_fs_fnames = []
freesurf_fnames = []
t2_fnames = []

def get_freesurf_names(subjids_picks):
    fs_picks = []
    b1_ftempl = removesuffix(str(genz_conv['_B1MAP-QUIET_FC_']['fname_template']))
    fs_ftempl = removesuffix(str(genz_conv['MEMP_IFS_0p5mm_2echo_']['fname_template']))
    for subjid in subjids_picks.subjids:
        subjid['b1map_fname'] = str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_B1MAP-QUIET_FC_']))
        subjid['freesurf_fname'] = str(fs_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['MEMP_IFS_0p5mm_2echo_'], dict3={'scan_info': 'ti1200_rms'}))
        fs_picks.append(subjid)
    return fs_picks

def get_dwi_names(subjids_picks):
    dwi_picks = []
    try:
        topup_ftempl = removesuffix(str(acdc_conv['_DWI6_B0_TOPUP_TE97_1p8mm3_']['fname_template']))
        topdn_ftempl = removesuffix(str(acdc_conv['_DWI6_B0_TOPDN_TE97_1p8mm3_']['fname_template']))
        dwi_ftempl = removesuffix(str(acdc_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_TE97_1p8mm3_']['fname_template']))
        for subjid in subjids_picks.subjids:
            subjid['topup_fname'] = str(topup_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI6_B0_TOPUP_TE97_1p8mm3_']))
            subjid['topdn_fname'] = str(topdn_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI6_B0_TOPDN_TE97_1p8mm3_']))
            subjid['dwi_fname'] = str(dwi_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_TE97_1p8mm3_']))
            dwi_picks.append(subjid)
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
        t2_picks.append(subjid)
    return t2_picks