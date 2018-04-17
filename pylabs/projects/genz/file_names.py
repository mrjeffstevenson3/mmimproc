# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

# here there are no subj ids, those are called out by the picks list inside SubjIdPicks object.

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for session and run numbers are set here as  well as exceptions to those defaults called out by subject and modality.
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
from collections import defaultdict
from pylabs.utils import removesuffix, getnetworkdataroot
from pylabs.conversion.brain_convert import img_conv, genz_conv, is_empty
from pylabs.io.mixed import getTRfromh5

fs = Path(getnetworkdataroot())
project = 'genz'


class SubjIdPicks(object):
    pass



class Opts(object):
    project = 'genz'
    spm_thresh = 0.85
    fsl_thresh = 0.23
    dwi_pass_qc = '_passqc'
    info_fname = fs / project / ('all_' + project + '_info.h5')
    dwi_fname_excep = ['_DWI64_3SH_B0_B800_B2000_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPDN_TE101_1p8mm3_']
    gaba_te = 80
    gaba_dyn = 120
    gaba_ftempl = '{subj}_WIP_{side}GABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT'
    vfa_fas = [4.0, 25.0]
    spgr_tr = '21p0'
    gaba_te = 80
    gaba_dyn = 120
    genz_conv = img_conv[project]

opts = Opts()

class Optsd(object):
    """
    Define constants for genz project with dict like mapping using opts = Optsd; **vars(opts).
    """
    def __init__(self,
            # define project variables here. will become dict using opts = Optsd; vars(opts).
            project = 'genz',
            test = False,
            overwrite = True,
            convert = False,
            spm_thresh = 0.85,
            fsl_thresh = 0.20,
            info_fname = fs / project / ('all_' + project + '_info.h5'),
            dwi_pass_qc = '_passqc',
            mf_str = '_mf',    # set to blank string '' to disable median filtering
            run_topup = True,
            eddy_corr = True,
            eddy_corr_dir = 'eddy_cuda_repol_v1',   # output dir for eddy
            dwi_fits_dir = 'fits_v1',
            do_ukf = True,
            dwi_reg_dir = 'MNI2dwi',
            run_bedpost = True,
            dwi_bedpost_dir = 'bedpost',
            dwi_fname_excep = ['_DWI64_3SH_B0_B800_B2000_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPUP_TE101_1p8mm3_', '_DWI6_B0_TOPDN_TE101_1p8mm3_'],
            gaba_te = 80,
            gaba_dyn = 120,
            gaba_ftempl = '{subj}_WIP_ACCGABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT',
            b1corr = False,
            vfa_tr = 21.0,
            vfa_fas = [4.0, 25.0],
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
        self.dwi_reg_dir = dwi_reg_dir
        self.run_bedpost = run_bedpost
        self.dwi_bedpost_dir = dwi_bedpost_dir
        self.dwi_fname_excep = dwi_fname_excep
        self.gaba_te = gaba_te
        self.gaba_dyn = gaba_dyn
        self.gaba_ftempl = gaba_ftempl
        self.b1corr = b1corr
        self.vfa_tr = vfa_tr
        self.vfa_fas = vfa_fas

"""
# other future stages to run to move to opts settings
subT2 = False   #wip ??
bet = False
prefilter = False
templating = False
"""

opts = Optsd()


qc_str = opts.dwi_pass_qc


# known or expected from genz protocol
spgr_tr = '12p0'
spgr_fa = ['05', '10', '15', '20', '30']
gaba_te = 80
gaba_dyn = 120

# for partial substitutions
fname_templ_dd = {'subj': '{subj}', 'session': '{session}', 'scan_name': '{scan_name}', 'scan_info': '{scan_info}',
                  'run': '{run}', 'fa': '{fa}', 'tr': '{tr}', 'side': '{side}', 'te': '{te}', 'dyn': '{dyn}',
                  'wild': '{wild}', 'type': '{type}'}

gaba_ftempl = '{subj}{wild}_WIP_ACCGABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT'

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


# freesurfer, VBM, T2 file name lists
b1map_fs_fnames = []
freesurf_fnames = []
t2_fnames = []
# dwi file name lists
topup_fnames = []
topdn_fnames= []
dwi_fnames = []
# 3 flip qT1 file name lists for testing purposes
for fa in ['05', '15', '30']:
    exec('spgr3_fa%(fa)s_fnames = []' % {'fa': fa})

b1map3_fnames = []
# 5 flip qT1 file name lists
for fa in spgr_fa:
    exec('spgr5_fa%(fa)s_fnames = []' % {'fa': fa})
b1map5_fnames = []


def get_freesurf_names(subjids_picks):
    b1_ftempl = removesuffix(str(genz_conv['_B1MAP-QUIET_FC_']['fname_template']))
    fs_ftempl = removesuffix(str(genz_conv['MEMP_IFS_0p5mm_2echo_']['fname_template']))
    for subjid in subjids_picks.subjids:
        b1map_fs_fnames.append(str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_B1MAP-QUIET_FC_'])))
        freesurf_fnames.append(str(fs_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['MEMP_IFS_0p5mm_2echo_'], dict3={'scan_info': 'ti1200_rms'})))
    return b1map_fs_fnames, freesurf_fnames

def get_dwi_names(subjids_picks):
    dwi_picks = []
    try:
        topup_ftempl = removesuffix(str(genz_conv['_DWI6_B0_TOPUP_']['fname_template']))
        topdn_ftempl = removesuffix(str(genz_conv['_DWI6_B0_TOPDN_']['fname_template']))
        dwi_ftempl = removesuffix(str(genz_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_']['fname_template']))
        for subjid in subjids_picks.subjids:
            subjid['topup_fname'] = str(topup_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI6_B0_TOPUP_']))
            subjid['topdn_fname'] = str(topdn_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI6_B0_TOPDN_']))
            subjid['dwi_fname'] = str(dwi_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI64_3SH_B0_B800_B2000_TOPUP_']))
            dwi_picks.append(subjid)
        return dwi_picks
    except TypeError as e:
            print('subjids needs to a dictionary.')

def get_3dt2_names(subjids_picks):
    t2_ftempl = removesuffix(str(img_conv[project]['_QUIET_3DT2W_0p5mm3_']['fname_template']))
    for subjid in subjids_picks.subjids:
        t2_fnames.append(str(t2_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_QUIET_3DT2W_0p5mm3_'])))
    return t2_fnames

def get_gaba_names(subjids_picks):
    # gaba spectroscopy file lists
    acc_act = []
    acc_ref = []
    for subjid in subjids_picks.subjids:
        source_path = Path(str(subjids_picks.source_path).format(**subjid))
        if not source_path.is_dir():
            raise ValueError('source_sparsdat directory for mrs SDAT not set properly in subjids_picks.source_path. Currently ' + str(source_path))
        # make dict to update
        mrs_dd = {'type': 'act', 'wild': '*', 'te': opts.gaba_te, 'dyn': opts.gaba_dyn, 'side': 'ACC'}
        if is_empty(list(source_path.glob(gaba_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=mrs_dd))))):
            print('cannot find .SPAR file matching '+gaba_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=mrs_dd)))
            continue
        else:
            acc_act.append(list(source_path.glob(gaba_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=mrs_dd))))[0])
            mrs_dd.update({'type': 'ref'})
            acc_ref.append(list(source_path.glob(gaba_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=mrs_dd))))[0])
    return acc_act, acc_ref

def get_matching_voi_names(subjids_picks):
    acc_matching = []
    acc_match_ftempl = removesuffix(str(img_conv[project]['_AX_MATCH_ACC_']['fname_template']))
    for subjid in subjids_picks.subjids:
        source_path = Path(str(subjids_picks.source_path).format(**subjid)).parent / 'mrs'
        acc_matching.append(source_path / str(acc_match_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_AX_MATCH_ACC_'])))
    return acc_matching

def get_vfa_names(subjids_picks):
    qt1_picks = []
    b1_ftempl = str(removesuffix(str(genz_conv['_B1MAP-QUIET_FC_']['fname_template'])))
    vfa_ftempl = str(removesuffix(str(genz_conv['_VFA_FA4-25_QUIET']['fname_template'])))
    for subjid in subjids_picks.subjids:
        subjid.update({'scan_name': genz_conv['_VFA_FA4-25_QUIET']['scan_name'], 'tr': '21p0'})
        subjid['vfatr'] = getTRfromh5(opts.info_fname, subjid['subj'], subjid['session'], 'qt1', vfa_ftempl.format(**subjid))
        subjid['vfa_fname'] = vfa_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=genz_conv['_VFA_FA4-25_QUIET']))
        subjid['b1map_fname'] = b1_ftempl.format(**merge_ftempl_dicts(dict1=subjid, dict2=genz_conv['_B1MAP_']))
        subjid['b1maptr'] = getTRfromh5(opts.info_fname, subjid['subj'], subjid['session'], 'fmap', b1_ftempl.format(**subjid))
        subjid['vfa_fas'] = opts.vfa_fas
        qt1_picks.append(subjid)
    return qt1_picks
