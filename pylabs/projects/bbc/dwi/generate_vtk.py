import os, inspect
from pathlib import *
import numpy as np
import nibabel as nib
import niprov, pylabs
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
#setup paths and file names to process
fs = Path(getnetworkdataroot())
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'
MNI_atlases = {'mori': pylabs_atlasdir / 'JHU_MNI_SS_WMPM_Type_I_matched.nii.gz',
                'aal_motor': pylabs_atlasdir / 'aal_1mm_motorcortex.nii',
                'mori_LeftPostIntCap-35': pylabs_atlasdir / 'mori_LeftPostIntCap-35.nii',
                'mori_RightPostIntCap-123': pylabs_atlasdir / 'mori_RightPostIntCap-123.nii',
                'mori_base_mask52only': pylabs_atlasdir / 'mori_base_mask52only.nii'
                }
project = 'bbc'
fa2t1_outdir = 'reg_subFA2suborigvbmpaired'
fadir = 'FA_fsl_wls_tensor_mf_ero_paired'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
templdir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space'
MNI2templ_invwarp = templdir / 'bbc_pairedLH_template_reg2MNI_1InverseWarp.nii.gz'
MNI2templ_aff = templdir / 'bbc_pairedLH_template_reg2MNI_0GenericAffine.mat'
dwi2vbmsubjdir = fs / project / 'reg' / 'reg_subFA2suborigvbmpaired'
dwi_reg_append = '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'
