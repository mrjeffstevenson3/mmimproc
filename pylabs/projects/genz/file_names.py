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
from pylabs.conversion.brain_convert import img_conv

project = 'genz'
qc_str = '_passqc'

class SubjIdPicks(object):
    pass

fs = Path(getnetworkdataroot())

info_fname = fs/project/('all_'+project+'_info.h5')


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
    b1_ftempl = removesuffix(str(img_conv[project]['_B1MAP-QUIET_FC_TR60-180_SP-100_']['fname_template']))
    fs_ftempl = removesuffix(str(img_conv[project]['_MEMP_IFS_0p5mm_TI1100_']['fname_template']))
    for subjid in subjids_picks.subjids:
        b1map_fs_fnames.append(str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_B1MAP-QUIET_FC_TR60-180_SP-100_'])))
        freesurf_fnames.append(str(fs_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_MEMP_IFS_0p5mm_TI1100_'], dict3={'scan_info': 'ti1100_rms'})))
    return b1map_fs_fnames, freesurf_fnames

def get_dwi_names(subjids_picks):
    try:
        topup_ftempl = removesuffix(str(img_conv[project]['_DWI_B0_TOPUP_']['fname_template']))
        topdn_ftempl = removesuffix(str(img_conv[project]['_DWI_B0_TOPDN_']['fname_template']))
        dwi_ftempl = removesuffix(str(img_conv[project]['_DWI64_3SH_B0_B800_B2000_TOPUP_']['fname_template']))
        for subjid in subjids_picks.subjids:
            topup_fnames.append(str(topup_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI_B0_TOPUP_'])))
            topdn_fnames.append(str(topdn_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_DWI_B0_TOPDN_'])))
            dwi_fnames.append(str(dwi_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_AX_MATCH_RIGHT_MEMP_VBM_TI1100_'])))
        return topup_fnames, topdn_fnames, dwi_fnames
    except TypeError, e:
            print('subjids needs to a dictionary.')


def get_5spgr_names(subjids_picks):
    try:
        b1_ftempl = removesuffix(str(img_conv[project]['_B1MAP_']['fname_template']))
        spgr_ftempl = removesuffix(str(img_conv[project]['_T1_MAP_']['fname_template']))
        for subjid in subjids_picks.subjids:
            b1map5_fnames.append(str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=img_conv[project]['_B1MAP_'])))
            fa_list_fnames = defaultdict()
            for fa in spgr_fa:
                fa_list_fnames['fa_%(fa)s' % {'fa': fa}] = str(spgr_ftempl).format(**merge_ftempl_dicts(
                    dict1=subjid, dict2=img_conv[project]['_T1_MAP_'], dict3={'fa': fa, 'tr': spgr_tr,}))
                exec('spgr5_fa%(fa)s_fnames.append(fa_list_fnames[\'fa_%(fa)s\'])' % {'fa': fa})
        return b1map5_fnames, spgr5_fa05_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames
    except TypeError, e:
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
        mrs_dd = {'type': 'act', 'wild': '*', 'te': gaba_te, 'dyn': gaba_dyn}
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
