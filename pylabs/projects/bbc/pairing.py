#this file specifies pairing for each modality is in the exact same subject order for zip.
from pathlib import *
from pylabs.utils.paths import getnetworkdataroot
#setup data paths and file names to process
fs = Path(getnetworkdataroot())
project = 'bbc'
ecdir = 'cuda_repol_std2_S0mf3_v5'
filterS0_string = ''
filterS0 = True
if filterS0:
    filterS0_string = '_withmf3S0'
dwitemplate = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_resampled2dwi.nii'
dwitemplatet2 = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz'
vbmtemplate = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'bbc_pairedLH_template.nii.gz'

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
    (253, 1, 'mpr', 1)]
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
    (253, 1, 'dti_15dir_b1000', 1)]

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
    ((120, 1, 'dti_15dir_b1000', 1), (253, 1, 'dti_15dir_b1000', 1), '253-120')]

vbmtuppairing = [
    ((101, 1, 'mpr', 3), (209, 1, 'mpr', 1), '209-101'),
    ((105, 1, 'mpr', 1), (211, 2, 'mpr', 1), '211-105'),
    ((106, 1, 'mpr', 1), (208, 1, 'mpr', 1), '208-106'),
    ((108, 1, 'mpr', 1), (202, 1, 'mpr', 1), '202-108'),
    ((113, 1, 'mpr', 1), (249, 1, 'mpr', 1), '249-113'),
    ((116, 1, 'wempr', 1), (241, 1, 'mpr', 2), '241-116'),
    ((118, 1, 'mpr', 2), (243, 1, 'mpr', 1), '243-118'),
    ((119, 3, 'mpr', 1), (231, 1, 'mpr', 1), '231-119'),
    ((120, 1, 'mpr', 1), (253, 1, 'mpr', 1), '253-120')]

dwi_ftempl = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'+filterS0_string+'_ec_thr1'
dwi_fnames = [dwi_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_ftempl = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_ftempl.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
dwi_ec_paths_fnames = [''] * len(dwi_fnames)
for i, fnm in enumerate(dwi_fnames):
    dwi_ec_paths_fnames[i] = fs / project / fnm.split('_')[0] / fnm.split('_')[1] / 'dwi' / ecdir / str(fnm+'.nii.gz')
