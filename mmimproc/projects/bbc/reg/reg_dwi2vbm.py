#erode FA and run antsregsyn on all FA to vbm
#gather pathway files from FA to vbm template and applywarpmultixfm !what interp?!
#combine into all_FA in stats dir

import os, inspect
from pathlib import *
from os.path import split
import numpy as np
import nibabel as nib
import niprov, mmimproc
from mmimproc.projects.bbc.pairing import vbmpairing, dwipairing
from mmimproc.utils.paths import getnetworkdataroot
from mmimproc.utils import run_subprocess, WorkingContext
#setup paths and file names to process
fs = mmimproc.fs_local
mmimproc_atlasdir = Path(*Path(inspect.getabsfile(mmimproc)).parts[:-2]) / 'data' / 'atlases'
antsregscript = Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh'
if not antsregscript.is_file():
    raise ValueError('Cannot find ANTs Registration script using ANTSPATH: ', antsregscript)
ncpu = 12
project = 'bbc'
fa2t1_outdir = 'reg_subFA2suborigvbmpaired_run2'
fadir = 'FA_fsl_wls_tensor_mf_ero_paired_run2'
cudadir = 'cuda_repol_std2_v2'
dwi_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [dwi_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwipairing]
vbm_templ = 'bbc_pairedLH_sub-bbc{sid}_ses-{snum}_{meth}_{runnum}_brain_susan_nl_comroll'
vbm_fnames = [vbm_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in vbmpairing]
orig_vbmdir = fs / project / 'reg' / 'orig_paired_vbm_staring_point'
fa_regdir = fs / project / 'reg' / fadir
if not orig_vbmdir.is_symlink():
    orig_vbmdir.symlink_to(Path('../myvbm/ants_vbm_template_pairedLH/orig_vbm'), target_is_directory=True)
if not fa_regdir.is_dir():
    fa_regdir.mkdir()
if not (fs / project / 'reg' / fa2t1_outdir).is_dir():
    (fs / project / 'reg' / fa2t1_outdir).mkdir()
#1st we erode FA 1 pixel to clean up edges.
with WorkingContext(str(fa_regdir)):
    for d in dwi_fnames:
        mask = fs / project / d.split('_')[0] / d.split('_')[1] / 'dwi' / str(d+'_S0_brain_mask.nii')
        oFA = fs / project / d.split('_')[0] / d.split('_')[1] / 'dwi' / cudadir / 'WLS' / str(d+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA.nii.gz')
        out = fs / project / 'reg' / fadir / str(d + '_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero.nii.gz')
        cmd = 'fslmaths '+str(mask)+' -ero -mul '+str(oFA)+' '+str(out)
        run_subprocess(cmd)
#run ants on every FA reg to subj VBM comroll (starting point of templating)
regsyn_output = ()
with WorkingContext(str(fs / project / 'reg')):
    for fa, t1 in zip(dwi_fnames, vbm_fnames):
        mov = fs / project / 'reg' / fadir / str(fa+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero.nii')
        ref = orig_vbmdir.resolve() / str('_'.join(t1.split('_')[2:])+'.nii.gz')
        out = fa2t1_outdir+'/'+fa+'_eddy_corrected_repol_std2_wls_fsl_tensor_mf_FA_ero_reg2sorigvbm_'
        cmd = str(antsregscript)+' -d 3 -f '+str(ref)+' -m '+str(mov)+' -o '+str(out)+' -n '+str(ncpu)
        regsyn_output += run_subprocess(cmd)
    with open('regsyn_fa2t1.log', mode='a') as logf:
        logf.write(regsyn_output)
    print(regsyn_output)
