#erode FA and run antsregsyn on all FA to vbm
#gather pathway files from FA to vbm template and applywarpmultixfm !what interp?!
#combine into all_FA in stats dir

import os, inspect
from pathlib import *
from os.path import split
import numpy as np
import nibabel as nib
import niprov, pylabs
from pylabs.projects.bbc.pairing import vbmpairing, dwipairing
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext

fs = Path(getnetworkdataroot())
pylabs_atlasdir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2]) / 'data' / 'atlases'
project = 'bbc'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
orig_vbmdir = fs / project / 'reg' / 'orig_paired_vbm_staring_point'
if not orig_vbmdir.is_symlink():
    orig_vbmdir.symlink_to(fs / project / 'myvbm' / 'ants_vbm_template_pairedLH' / 'orig_vbm', target_is_directory=True)

with WorkingContext(str(fs / project / 'reg' / 'FA_fsl_wls_tensor_mf_ero_paired')):
    for d in dwi_fnames[1:]:
        mask = fs / project / d.split('_')[0] / d.split('_')[1] / 'dwi' / str(d+'_S0_brain_mask.nii')
        oFA = fs / project / d.split('_')[0] / d.split('_')[1] / 'dwi' / 'cuda_repol_std2' / 'WLS' / str(d+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA.nii.gz')
        out = fs / project / 'reg' / 'FA_fsl_wls_tensor_mf_ero_paired' / str(d + '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero.nii.gz')
        cmd = 'fslmaths '+str(mask)+' -ero -mul '+str(oFA)+' '+str(out)
        run_subprocess(cmd)

with WorkingContext(str(fs / project / 'reg')):
    for fa, t1 in zip(dwi_fnames[1:], vbm_fnames[1:]):
        mov = fs / project / 'reg' / 'FA_fsl_wls_tensor_mf_ero_paired' / str(fa+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero.nii.gz')
        ref = orig_vbmdir.resolve() / str('_'.join(vbm_fnames[1].split('_')[2:])+'.nii.gz')
        out = 'reg_subFA2suborigvbmpaired/'+fa+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'
        cmd = 'antsRegistrationSyN.sh -d 3 -f '+str(ref)+' -m '+str(mov)+' -o '+str(out)+' -n 20'
        run_subprocess(cmd)
