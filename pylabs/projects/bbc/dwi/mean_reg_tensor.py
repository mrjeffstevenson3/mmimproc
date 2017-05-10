from pathlib import *
from pylabs.projects.bbc.pairing import dwi_fsl_wls_tensor_mf_fnames, dwi2templ_warp_fnames, dwi2templ_affine_fnames
from pylabs.utils import appendposix
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.utils.paths import getnetworkdataroot
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())

ec_dir = 'cuda_repol_std2_S0mf3_v5'
fit_method = 'WLS'
regdir = fs/'bbc'/'reg'/'ants_dwiS0_in_template_space'
outdir = fs/'bbc'/'reg'/ 'ants_wls_tensor_mf_template_space'
ref = regdir / 'bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz'

if not outdir.is_dir():
    outdir.mkdir(parents=True)

for d, w,a in zip(dwi_fsl_wls_tensor_mf_fnames, dwi2templ_warp_fnames, dwi2templ_affine_fnames):
    tdir = fs/'bbc'/d.split('_')[0] / d.split('_')[1] / 'dwi'/ ec_dir/fit_method
    tensor = tdir/d
    warpfiles = [str(regdir/w)]
    affine_xform = [str(regdir / a)]
    outf = outdir/ appendposix(d, '_reg2dwiT2template')
    subj2templ_applywarp(str(tensor), str(ref), str(outf), warpfiles, str(outdir), dims=4, affine_xform=affine_xform, args=[' --use-BSpline'])
    nii2nrrd(str(outf), str(outf).replace('.nii.gz', '.nhdr'), istensor=True)