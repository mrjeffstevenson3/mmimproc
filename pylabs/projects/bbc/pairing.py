#this file specifies pairing for each modality is in the exact same subject order for zip.
from pathlib import *
import pandas as pd
from pylabs.projects.bbc.fmri.fmr_runs import picks
from pylabs.utils.paths import getnetworkdataroot
#setup data paths and file names to process
fs = Path(getnetworkdataroot())
project = 'bbc'
ecdir = 'cuda_repol_std2_S0mf3_v5'
filterS0_string = '_withmf3S0'
behav_csv_name = 'bbc_behav_2-22-2017_rawsub.csv'
dwitemplate = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_resampled2dwi.nii'
dwitemplatet2 = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz'
vbmtemplate = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template.nii.gz'
vbmtemplatet2 = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_invT2c.nii.gz'
scsqT1templatet2 = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_invT2c_resampled2scsqT1.nii.gz'
# combined tuples are paired indexed successively (0->1, 2->3, ...), paired tuples are ordered indexed matched pairs.
vbmpairing = [
    (101, 1, 'mpr', 3),
    (209, 1, 'mpr', 1),
    (105, 1, 'mpr', 1),
    (211, 2, 'mpr', 1),
    (106, 1, 'mpr', 1),
    (208, 1, 'mpr', 1),
    (108, 1, 'mpr', 1),
    (202, 1, 'mpr', 1),
    (113, 1, 'mpr', 1),
    (249, 1, 'mpr', 1),
    (116, 1, 'wempr', 1),
    (241, 1, 'mpr', 2),
    (118, 1, 'mpr', 2),
    (243, 1, 'mpr', 1),
    (119, 3, 'mpr', 1),
    (231, 1, 'mpr', 1),
    (120, 1, 'mpr', 1),
    (253, 1, 'mpr', 1),
        ]

#here dwi pairing bbc101 ses-2 is a hybrid of ses-1 & 3 due to bad motion on both. eddy does re-alignment with vectors intact
dwipairing = [
    (101, 2, 'dti_15dir_b1000', 1),
    (209, 1, 'dti_15dir_b1000', 1),
    (105, 1, 'dti_15dir_b1000', 1),
    (211, 2, 'dti_15dir_b1000', 1),
    (106, 1, 'dti_15dir_b1000', 1),
    (208, 1, 'dti_15dir_b1000', 1),
    (108, 1, 'dti_15dir_b1000', 1),
    (202, 1, 'dti_15dir_b1000', 1),
    (113, 1, 'dti_15dir_b1000', 1),
    (249, 1, 'dti_15dir_b1000', 1),
    (116, 1, 'dti_15dir_b1000', 1),
    (241, 1, 'dti_15dir_b1000', 1),
    (118, 1, 'dti_15dir_b1000', 1),
    (243, 1, 'dti_15dir_b1000', 1),
    (119, 2, 'dti_15dir_b1000', 2),
    (231, 1, 'dti_15dir_b1000', 1),
    (120, 1, 'dti_15dir_b1000', 1),
    (253, 1, 'dti_15dir_b1000', 1),
        ]

#tuple pairing for subs and concats
dwituppairing = [
    ((101, 2, 'dti_15dir_b1000', 1), (209, 1, 'dti_15dir_b1000', 1), '209-101'),
    ((105, 1, 'dti_15dir_b1000', 1), (211, 2, 'dti_15dir_b1000', 1), '211-105'),
    ((106, 1, 'dti_15dir_b1000', 1), (208, 1, 'dti_15dir_b1000', 1), '208-106'),
    ((108, 1, 'dti_15dir_b1000', 1), (202, 1, 'dti_15dir_b1000', 1), '202-108'),
    ((113, 1, 'dti_15dir_b1000', 1), (249, 1, 'dti_15dir_b1000', 1), '249-113'),
    ((116, 1, 'dti_15dir_b1000', 1), (241, 1, 'dti_15dir_b1000', 1), '241-116'),
    ((118, 1, 'dti_15dir_b1000', 1), (243, 1, 'dti_15dir_b1000', 1), '243-118'),
    ((119, 2, 'dti_15dir_b1000', 2), (231, 1, 'dti_15dir_b1000', 1), '231-119'),
    ((120, 1, 'dti_15dir_b1000', 1), (253, 1, 'dti_15dir_b1000', 1), '253-120'),
        ]

vbmtuppairing = [
    ((101, 1, 'mpr', 3), (209, 1, 'mpr', 1), '209-101'),
    ((105, 1, 'mpr', 1), (211, 2, 'mpr', 1), '211-105'),
    ((106, 1, 'mpr', 1), (208, 1, 'mpr', 1), '208-106'),
    ((108, 1, 'mpr', 1), (202, 1, 'mpr', 1), '202-108'),
    ((113, 1, 'mpr', 1), (249, 1, 'mpr', 1), '249-113'),
    ((116, 1, 'wempr', 1), (241, 1, 'mpr', 2), '241-116'),
    ((118, 1, 'mpr', 2), (243, 1, 'mpr', 1), '243-118'),
    ((119, 3, 'mpr', 1), (231, 1, 'mpr', 1), '231-119'),
    ((120, 1, 'mpr', 1), (253, 1, 'mpr', 1), '253-120'),
        ]

paired_foster_subjs_tup = [
    (101, 2, 'dti_15dir_b1000', 1),
    (105, 1, 'dti_15dir_b1000', 1),
    (106, 1, 'dti_15dir_b1000', 1),
    (108, 1, 'dti_15dir_b1000', 1),
    (113, 1, 'dti_15dir_b1000', 1),
    (116, 1, 'dti_15dir_b1000', 1),
    (118, 1, 'dti_15dir_b1000', 1),
    (119, 2, 'dti_15dir_b1000', 2),
    (120, 1, 'dti_15dir_b1000', 1),
        ]

# abuse occurred for 106 in 2nd placement, and 109, 116.

paired_control_subjs_tup = [
    (202, 1, 'dti_15dir_b1000', 1),
    (208, 1, 'dti_15dir_b1000', 1),
    (209, 1, 'dti_15dir_b1000', 1),
    (211, 2, 'dti_15dir_b1000', 1),
    (231, 1, 'dti_15dir_b1000', 1),
    (241, 1, 'dti_15dir_b1000', 1),
    (243, 1, 'dti_15dir_b1000', 1),
    (249, 1, 'dti_15dir_b1000', 1),
    (253, 1, 'dti_15dir_b1000', 1),
        ]

paired_vbm_foster_subjs_tup = [
    (101, '0000'),
    (105, '0002'),
    (106, '0004'),
    (108, '0006'),
    (113, '0008'),
    (116, '0010'),
    (118, '0012'),
    (119, '0014'),
    (120, '0016'),
    ]

paired_vbm_control_subjs_tup = [
    (209, '0001'),
    (211, '0003'),
    (208, '0005'),
    (202, '0007'),
    (249, '0009'),
    (241, '0011'),
    (243, '0013'),
    (231, '0015'),
    (253, '0017'),
    ]
# sort ascending according to subject id number. paired tuples are ordered indexed matched pairs.
paired_foster_subjs_sorted = sorted(paired_foster_subjs_tup, key=lambda x: x[0])
paired_control_subjs_sorted = sorted(paired_control_subjs_tup, key=lambda x: x[0])
paired_vbm_foster_subjs_sorted = sorted(paired_vbm_foster_subjs_tup, key=lambda x: x[0])
paired_vbm_control_subjs_sorted = sorted(paired_vbm_control_subjs_tup, key=lambda x: x[0])
foster_paired_behav_subjs = ['BBC{sid}'.format(sid=s) for s, ses, m, r in paired_foster_subjs_sorted]
control_paired_behav_subjs = ['BBC{sid}'.format(sid=s) for s, ses, m, r in paired_control_subjs_sorted]
dwi_ftempl = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'+filterS0_string+'_ec_thr1'
dwi_fnames = [dwi_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
dwi_ec_ppaths_fnames = [''] * len(dwi_fnames)
dwi_ec_str_fnames = [''] * len(dwi_fnames)
for i, fnm in enumerate(dwi_fnames):
    dwi_ec_ppaths_fnames[i] = fs / project / fnm.split('_')[0] / fnm.split('_')[1] / 'dwi' / ecdir / str(fnm+'.nii.gz')
    dwi_ec_str_fnames[i] = str(dwi_ec_ppaths_fnames[i])
foster_dwi_fnames = [dwi_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in paired_foster_subjs_sorted]
control_dwi_fnames = [dwi_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in paired_control_subjs_sorted]
vbm_ftempl = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
mods = ['FA', 'MD', 'RD', 'AD']
dwi_mods_ftempl = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_{fit_meth}_{mod}_reg2vbmtempl.nii'
fit_meth = 'wls_fsl_tensor_mf'
mod = 'FA'
FA_paired_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in dwipairing]
FA_foster_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_foster_subjs_sorted]
FA_control_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_control_subjs_sorted]
mod = 'MD'
MD_paired_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in dwipairing]
MD_foster_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_foster_subjs_sorted]
MD_control_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_control_subjs_sorted]
mod = 'RD'
RD_paired_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in dwipairing]
RD_foster_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_foster_subjs_sorted]
RD_control_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_control_subjs_sorted]
mod = 'AD'
AD_paired_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in dwipairing]
AD_foster_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_foster_subjs_sorted]
AD_control_pnames = [fs / project / 'reg' / 'ants_dwiS0_in_template_space' / mod / fit_meth / dwi_mods_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r), fit_meth=fit_meth, mod=mod) for s, ses, m, r in paired_control_subjs_sorted]

#make GM + WM s2 file name templates for foster & control. may need to move or link files to dwi paths for mod to take
gm_s2_ftempl = 'sub-bbc{sid}_GM_mod_s2_vol{vol}.nii.gz'
wm_s2_ftempl = 'sub-bbc{sid}_WM_mod_s2_vol{vol}.nii.gz'
mod = 'GM'
GMVBM_foster_pnames = [fs / project / 'myvbm' / 'ants_vbm_template_pairedLH' / mod / gm_s2_ftempl.format(sid=str(s), vol=str(v)) for s, v in paired_vbm_foster_subjs_sorted]
GMVBM_control_pnames = [fs / project / 'myvbm' / 'ants_vbm_template_pairedLH' / mod / gm_s2_ftempl.format(sid=str(s), vol=str(v)) for s, v in paired_vbm_control_subjs_sorted]
mod = 'WM'
WMVBM_foster_pnames = [fs / project / 'myvbm' / 'ants_vbm_template_pairedLH' / mod / wm_s2_ftempl.format(sid=str(s), vol=str(v)) for s, v in paired_vbm_foster_subjs_sorted]
WMVBM_control_pnames = [fs / project / 'myvbm' / 'ants_vbm_template_pairedLH' / mod / wm_s2_ftempl.format(sid=str(s), vol=str(v)) for s, v in paired_vbm_control_subjs_sorted]


behav_list = [(u'21', u'PATrhyTotSS') , (u'22', u'PATsegTotSS') , (u'23', u'CTOPPphoaCS')  ,(u'24', u'CTOPPrnCS') ,(u'25', u'CTOPPphomCS'), (u'26', u'PPVTSS'), (u'27', u'TOPELeliSS') ,(u'28', u'STIMQ-PSDSscaleScore1-to-15-SUM'), (u'29', u'self-esteem-IAT')]
csvraw = fs / project / 'behavior' / behav_csv_name
data = pd.read_csv(str(csvraw), header=[0,1], index_col=1, tupleize_cols=True)
foster_behav_data = data.loc[foster_paired_behav_subjs, behav_list]
control_behav_data = data.loc[control_paired_behav_subjs, behav_list]
# fmri base file names list
fmri_fname_templ = 'sub-bbc{sid}_ses-{snum}_fmri_{runnum}.nii'
fmri_fnames = [fmri_fname_templ.format(sid=str(s), snum=str(ses), runnum=str(r)) for s, ses, r in picks]

# fsl wls tensor mf fits for warping to template space
# make aligned tensor, warp, affine lists to zip

foster_dwi_fsl_wls_tensor_mf_fnames = [fname+'_wls_fsl_tensor_medfilt.nii.gz' for fname in foster_dwi_fnames]
control_dwi_fsl_wls_tensor_mf_fnames = [fname+'_wls_fsl_tensor_medfilt.nii.gz' for fname in control_dwi_fnames]
dwi_fsl_wls_tensor_mf_fnames = foster_dwi_fsl_wls_tensor_mf_fnames + control_dwi_fsl_wls_tensor_mf_fnames
foster_dwi2templ_warp_fnames = [fname.replace('_withmf3S0_ec_thr1', '_withmf3S0_S0_brain_j1_s10_r1_reg2dwiT2template_1Warp.nii.gz') for fname in foster_dwi_fnames]
control_dwi2templ_warp_fnames = [fname.replace('_withmf3S0_ec_thr1', '_withmf3S0_S0_brain_j1_s10_r1_reg2dwiT2template_1Warp.nii.gz') for fname in control_dwi_fnames]
dwi2templ_warp_fnames = foster_dwi2templ_warp_fnames + control_dwi2templ_warp_fnames
foster_dwi2templ_affine_fnames = [fname.replace('_withmf3S0_ec_thr1', '_withmf3S0_S0_brain_j1_s10_r1_reg2dwiT2template_0GenericAffine.mat') for fname in foster_dwi_fnames]
control_dwi2templ_affine_fnames = [fname.replace('_withmf3S0_ec_thr1', '_withmf3S0_S0_brain_j1_s10_r1_reg2dwiT2template_0GenericAffine.mat') for fname in control_dwi_fnames]
dwi2templ_affine_fnames = foster_dwi2templ_affine_fnames + control_dwi2templ_affine_fnames

# freesurfer subject directories
freesurf_dir_templ = 'sub-bbc{sid}/sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_freesurf'
freesurf_dirs = [fs/project/freesurf_dir_templ.format(sid=s, snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
