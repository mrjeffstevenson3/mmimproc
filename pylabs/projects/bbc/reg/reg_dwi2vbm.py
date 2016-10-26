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

with WorkingContext(str(fs / project / 'reg' / 'FA_fsl_wls_tensor_mf_ero_paired')):
    for d in dwi_fnames[1:]:
        print d
        mask = fs / project / d.split('_')[0] / d.split('_')[1] / 'dwi' / str(d+'_S0_brain_mask.nii')
        oFA = fs / project / d.split('_')[0] / d.split('_')[1] / 'dwi' / 'cuda_repol_std2' / 'WLS' / str(d+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA.nii.gz')
        out = fs / project / 'reg' / 'FA_fsl_wls_tensor_mf_ero_paired' / str(d + '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero.nii.gz')
        cmd = 'fslmaths '+str(mask)+' -ero -mul '+str(oFA)+' '+str(out)
        run_subprocess(cmd)
