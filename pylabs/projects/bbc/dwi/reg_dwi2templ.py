import os, inspect
from pathlib import *
import datetime
from os.path import split
import numpy as np
import nibabel as nib
import pylabs
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

#loop over modality then fit method FA then dipy_wls

mods = ['FA', 'MD']

fitmeths = {'OLS': ['%(m)s_dipy', '%(m)s_cam', '%(m)s_fsl'],
            'WLS': ['%(m)s_dipy', '%(m)s_cam', '%(m)s_fsl'],
            'RESTORE': ['%(m)s_dipy', '%(m)s_cam'],
            }

meths = ['wls_dipy', 'wls_fsl', 'wls_cam', 'wls_dipy_mf', 'wls_fsl_mf', 'wls_cam_mf',
         'ols_dipy', 'ols_fsl', 'ols_cam', 'ols_dipy_mf', 'ols_fsl_mf', 'ols_cam_mf',
         'restore_cam', 'restore_dipy', 'restore_cam_mf', 'restore_dipy_mf']


project = 'bbc'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
templ_ref = templdir / 'bbc_pairedLH_template_resampled2dwi.nii'
MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
dwi2vbmsubjdir = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired_run2'
dwi_reg_append = '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'

for dwif, vbmf in zip(dwi_fnames[1], vbm_fnames[1]):

    fa2t1_outdir = fs / project / 'reg' / 'dwi_in_template_space' / mods / '_'.join([mods, meths, 'warped2templ'])

    for k, m in meths.iteritems():
        execwdir = fs / project /  dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / 'cuda_repol_std2_v2'
        mov = a         # always dwi modality
        ref = str(templ_ref)     # target is subj template t1 resampled to dwi res
        outf = execwdir / str(dwif+'_'+k)
        iwarp_dwi2vbmsub = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired' / str(dwif+ dwi_reg_append +'1InverseWarp.nii.gz')
        iwarp_vbmsubj2templ = templdir / str(vbmf+'InverseWarp.nii.gz')
        aff_dwi2vbmsub = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired' / str(dwif + dwi_reg_append + '0GenericAffine.mat')
        aff_vbmsubj2templ = templdir / str(vbmf+'Affine.txt')
        warpfiles = [str(iwarp_vbmsub2dwi), str(iwarp_templ2vbmsubj)]
        affine_xform = [str(aff_vbmsub2dwi), str(aff_templ2vbmsubj)]


        for km, m in mods.iteritems():
            subj2templ_applywarp(str(mov), str(ref), str(outf)+'.nii', warpfiles, str(execwdir / km), affine_xform=affine_xform)


# need ref, in and out files, t1 to template and dwi to t1 warp and affines.