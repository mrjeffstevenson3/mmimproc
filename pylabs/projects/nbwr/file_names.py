# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

# here there are no subj ids, those are called out by the picks list and and

# class object to pass list of subject ids and passed to functions here using the SubjIdPicks class object.
# defaults for session and run numbers are set here as  well as exceptions to those defaults called out by subject and modality.
from collections import defaultdict
from pylabs.utils import removesuffix
from pylabs.conversion.brain_convert import nbwr_conv

class SubjIdPicks(object):
    pass


project = 'nbwr'
# known from protocol
spgr_tr = 12
spgr_fa = ['05', '10', '15', '20', '30']

# old method of creating file names
ftempl = 'sub-nbwr{}_ses-{}_{}_{}'


b1map_fname_dd = defaultdict()
fs_fname_dd = defaultdict()
topup_fname_dd = defaultdict()
topdn_fname_dd = defaultdict()
dwi_fname_dd = defaultdict()
t2_fname_dd = defaultdict()
spgr_fname_dd = defaultdict()
# freesurfer, VBM, T2 file name lists
b1map_fs_fnames = []
vbm_fnames = []
freesurf_fnames = []
t2_fnames = []
# dwi file name lists
topup_fnames = []
topdn_fnames= []
dwi_fnames = []
# 3 flip qT1 file name lists
spgr_fa5_fnames = []
spgr_fa15_fnames = []
spgr_fa30_fnames = []
b1map_fnames = []
# 5 flip qT1 file name lists
spgr5_fa5_fnames = []
spgr5_fa10_fnames = []
spgr5_fa15_fnames = []
spgr5_fa20_fnames = []
spgr5_fa30_fnames = []
b1map5_fnames = []

# default file name endings
b1map_fname_tail = ('ses-1', 'b1map', '', 1)
fs_rms_fname_tail = ('ses-1', 'fsmempr_ti1100', 'rms', 1)
topup_fname_tail = ('ses-1', 'dwi-topup', '6S0', 1)
topdn_fname_tail = ('ses-1', 'dwi-topdn', '6S0', 1)
dwi_fname_tail = ('ses-1', 'dwi-topup', '64dir-3sh-800-2000', 1)
t2_fname_tail = (1, '3dt2', '', 1)
spgr5_fname_tail = (1, 'spgr', '%(fa)s', '%(tr)sp0', 1)

vbm_rms = [
    ('998', 1, 'vbmmempr_ti850_rms', 1),
    ]

def get_vbm_names(subjids_picks):
    for vbm in vbm_rms:
        if vbm[0] in subjids_picks.subjids:
            vbm_fnames.append(ftempl.format(*vbm))
    return vbm_fnames

def get_freesurf_names(subjids_picks):
    b1_ftempl = removesuffix(str(nbwr_conv['_B1MAP_']['fname_template']))
    fs_ftempl = removesuffix(str(nbwr_conv['_MEMP_FS_TI1100_']['fname_template']))
    for subjid in subjids_picks.subjids:
        b1map_fname_dd['subj'], b1map_fname_dd['session'], b1map_fname_dd['scan_name'], b1map_fname_dd['scan_info'], b1map_fname_dd['run'] = ('sub-' + project + subjid,) + b1map_fname_tail
        fs_fname_dd['subj'], fs_fname_dd['session'], fs_fname_dd['scan_name'], fs_fname_dd['scan_info'], fs_fname_dd['run'] =  ('sub-' + project + subjid,) + fs_rms_fname_tail
        b1map_fs_fnames.append(str(b1_ftempl).format(**b1map_fname_dd))
        freesurf_fnames.append(str(fs_ftempl).format(**fs_fname_dd))
    return b1map_fs_fnames, freesurf_fnames

def get_dwi_names(subjids_picks):
    topup_ftempl = removesuffix(str(nbwr_conv['_DWI_B0_TOPUP_']['fname_template']))
    topdn_ftempl = removesuffix(str(nbwr_conv['_DWI_B0_TOPDN_']['fname_template']))
    dwi_ftempl = removesuffix(str(nbwr_conv['_DWI64_3SH_B0_B800_B2000_TOPUP_']['fname_template']))
    for subjid in subjids_picks.subjids:
        topup_fname_dd['subj'], topup_fname_dd['session'], topup_fname_dd['scan_name'], topup_fname_dd['scan_info'], topup_fname_dd['run'] = ('sub-' + project + subjid,) + topup_fname_tail
        topdn_fname_dd['subj'], topdn_fname_dd['session'], topdn_fname_dd['scan_name'], topdn_fname_dd['scan_info'], topdn_fname_dd['run'] =  ('sub-' + project + subjid,) + topdn_fname_tail
        dwi_fname_dd['subj'], dwi_fname_dd['session'], dwi_fname_dd['scan_name'], dwi_fname_dd['scan_info'], dwi_fname_dd['run'] =  ('sub-' + project + subjid,) + dwi_fname_tail
        topup_fnames.append(str(topup_ftempl).format(**topup_fname_dd))
        topdn_fnames.append(str(topdn_ftempl).format(**topdn_fname_dd))
        dwi_fnames.append(str(dwi_ftempl).format(**dwi_fname_dd))
    return topup_fnames, topdn_fnames, dwi_fnames

def get_5spgr_names(subjids_picks):
    b1_ftempl = removesuffix(str(nbwr_conv['_B1MAP_']['fname_template']))
    spgr_ftempl = removesuffix(str(nbwr_conv['_T1_MAP_']['fname_template']))
    for subjid in subjids_picks.subjids:
        b1map_fname_dd['subj'], b1map_fname_dd['session'], b1map_fname_dd['scan_name'], b1map_fname_dd['scan_info'], b1map_fname_dd['run'] = ('sub-' + project + subjid,) + b1map_fname_tail
        b1map5_fnames.append(str(b1_ftempl).format(**b1map_fname_dd))
        fa_list_fnames = defaultdict()
        for fa in spgr_fa:
            fad = {'fa': fa, 'tr': spgr_tr}
            spgr_fname_dd['subj'], spgr_fname_dd['session'], spgr_fname_dd['scan_name'], spgr_fname_dd['fa'], spgr_fname_dd['tr'],\
            spgr_fname_dd['run'] = ('sub-' + project + subjid,) + spgr5_fname_tail
            spgr_fname_dd['fa'] = spgr_fname_dd['fa'] % fad
            spgr_fname_dd['tr'] = spgr_fname_dd['tr'] % fad
            fa_list_fnames['fa_%(fa)s' % fad] = str(spgr_ftempl).format(**spgr_fname_dd)
        spgr5_fa5_fnames.append(fa_list_fnames['fa_05'])
        spgr5_fa10_fnames.append(fa_list_fnames['fa_10'])
        spgr5_fa15_fnames.append(fa_list_fnames['fa_15'])
        spgr5_fa20_fnames.append(fa_list_fnames['fa_20'])
        spgr5_fa30_fnames.append(fa_list_fnames['fa_30'])
    return b1map5_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames


def get_3dt2_names(subjids_picks):
    t2_ftempl = removesuffix(str(nbwr_conv['_3DT2W_']['fname_template']))
    for subjid in subjids_picks.subjids:
        t2_fname_dd['subj'], t2_fname_dd['session'], t2_fname_dd['scan_name'], t2_fname_dd['scan_info'], t2_fname_dd['run'] =  ('sub-' + project + subjid,) + t2_fname_tail
        t2_fnames.append(str(t2_ftempl).format(**t2_fname_dd))
    return t2_fnames
