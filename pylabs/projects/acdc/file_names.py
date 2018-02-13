# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

# here there are no subj ids, those are called out by the picks list inside SubjIdPicks object.

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for session and run numbers are set here as  well as exceptions to those defaults called out by subject and modality.
import pylabs
from pathlib import *
import pandas as pd
from collections import defaultdict
from pylabs.utils import removesuffix, getnetworkdataroot
from pylabs.conversion.brain_convert import acdc_conv

project = 'acdc'

class SubjIdPicks(object):
    pass

fs = Path(getnetworkdataroot())

info_fname = fs/project/('all_'+project+'_info.h5')

# def test_info_file(subjids_picks):
#     if not info_fname.is_file():
#         raise ValueError('hdf info file '+ info_fname + ' not found.')
#     with pd.HDFStore(str(info_fname)) as storeh5:
#         for subj in subjids_picks:




# known or expected from genz protocol
spgr_tr = '12p0'
spgr_fa = ['05', '15', '30']
gaba_te = 80
gaba_dyn = 120

# for partial substitutions
fname_templ_dd = {'subj': '{subj}', 'session': '{session}', 'scan_name': '{scan_name}', 'scan_info': '{scan_info}',
                  'run': '{run}', 'fa': '{fa}', 'tr': '{tr}', 'side': '{side}', 'te': '{te}', 'dyn': '{dyn}',
                  'wild': '{wild}', 'type': '{type}'}

gaba_ftempl = '{subj}_WIP_{side}GABAMM_TE{te}_{dyn}DYN_{wild}_raw_{type}.SDAT'

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

# freesurfer, VBM, T2 file name lists
b1map_fs_fnames = []
freesurf_fnames = []
t2_fnames = []
# dwi file name lists
topup_fnames = []
topdn_fnames= []
dwi_fnames = []
# 3 flip qT1 file name lists for testing purposes
spgr_fa5_fnames = []
spgr_fa15_fnames = []
spgr_fa30_fnames = []
b1map_fnames = []


def get_freesurf_names(subjids_picks):
    b1_ftempl = removesuffix(str(acdc_conv['_B1MAP-QUIET_']['fname_template']))
    fs_ftempl = removesuffix(str(acdc_conv['_MEMP_IFS_0p5mm_']['fname_template']))
    for subjid in subjids_picks.subjids:
        b1map_fs_fnames.append(str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_B1MAP-QUIET_'])))
        freesurf_fnames.append(str(fs_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_MEMP_IFS_0p5mm_'], dict3={'scan_info': 'ti1400_rms'})))
    return b1map_fs_fnames, freesurf_fnames

def get_dwi_names(subjids_picks):
    topup_ftempl = removesuffix(str(acdc_conv['_DWI6_B0_TOPUP_TE101_1p8mm3_']['fname_template']))
    topdn_ftempl = removesuffix(str(acdc_conv['_DWI6_B0_TOPDN_TE101_1p8mm3_']['fname_template']))
    dwi_ftempl = removesuffix(str(acdc_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_TE101_1p8mm3_']['fname_template']))
    for subjid in subjids_picks.subjids:
        topup_fnames.append(str(topup_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI6_B0_TOPUP_TE101_1p8mm3_'])))
        topdn_fnames.append(str(topdn_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI6_B0_TOPDN_TE101_1p8mm3_'])))
        dwi_fnames.append(str(dwi_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_TE101_1p8mm3_'])))
    return topup_fnames, topdn_fnames, dwi_fnames

def get_3spgr_names(subjids_picks):
    b1_ftempl = removesuffix(str(acdc_conv['_B1MAP-QUIET_']['fname_template']))
    spgr_ftempl = removesuffix(str(acdc_conv['_T1_MAP_']['fname_template']))
    for subjid in subjids_picks.subjids:
        subjid.update({'tr': spgr_tr,})
        b1map_fnames.append(str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_B1MAP_'])))
        fa_list_fnames = defaultdict()
        for fa in spgr_fa:
            fad = {'fa': fa, }
            fa_list_fnames['fa_%(fa)s' % fad] = str(spgr_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_T1_MAP_'], dict3=fad))
        spgr_fa5_fnames.append(fa_list_fnames['fa_05'])
        spgr_fa15_fnames.append(fa_list_fnames['fa_15'])
        spgr_fa30_fnames.append(fa_list_fnames['fa_30'])
    return b1map_fnames, spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames

def get_vfa_names(subjids_picks):
    b1_ftempl = removesuffix(str(acdc_conv['_B1MAP-QUIET_']['fname_template']))
    spgr_ftempl = removesuffix(str(acdc_conv['_VFA_']['fname_template']))


    for subjid in subjids_picks.subjids:
        subjid.update({'tr': spgr_tr,})
        b1map_fnames.append(str(b1_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_B1MAP_'])))
        fa_list_fnames = defaultdict()
        for fa in spgr_fa:
            fad = {'fa': fa, }
            fa_list_fnames['fa_%(fa)s' % fad] = str(spgr_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_T1_MAP_'], dict3=fad))
        spgr_fa5_fnames.append(fa_list_fnames['fa_05'])
        spgr_fa15_fnames.append(fa_list_fnames['fa_15'])
        spgr_fa30_fnames.append(fa_list_fnames['fa_30'])
    return b1map_fnames, spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames



def get_3dt2_names(subjids_picks):
    t2_ftempl = removesuffix(str(acdc_conv['_3DT2W_']['fname_template']))
    for subjid in subjids_picks.subjids:
        t2_fnames.append(str(t2_ftempl).format(**merge_ftempl_dicts(dict1=subjid, dict2=acdc_conv['_3DT2W_'])))
    return t2_fnames
