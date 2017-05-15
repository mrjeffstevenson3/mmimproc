from pathlib import *
import numpy as np
import nibabel as nib
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

mean_tensor_fname = 'mean_fsl_wls_tensor_mf.nii'
ec_dir = 'cuda_repol_std2_S0mf3_v5'
fit_method = 'WLS'
regdir = fs/'bbc'/'reg'/'ants_dwiS0_in_template_space'
outdir = fs/'bbc'/'reg'/ 'ants_wls_tensor_mf_template_space'
ref = regdir / 'bbc_pairedLH_template_invT2c_resampled2dwi.nii.gz'

if not outdir.is_dir():
    outdir.mkdir(parents=True)

tensor_fnames = []
for d, w,a in zip(dwi_fsl_wls_tensor_mf_fnames, dwi2templ_warp_fnames, dwi2templ_affine_fnames):
    tdir = fs/'bbc'/d.split('_')[0] / d.split('_')[1] / 'dwi'/ ec_dir/fit_method
    tensor = tdir/d
    warpfiles = [str(regdir/w)]
    affine_xform = [str(regdir / a)]
    outf = outdir/ appendposix(d, '_reg2dwiT2template')
    subj2templ_applywarp(str(tensor), str(ref), str(outf), warpfiles, str(outdir), dims=4, affine_xform=affine_xform, args=[' --use-BSpline'])
    nii2nrrd(str(outf), str(outf).replace('.nii.gz', '.nhdr'), istensor=True)
    tensor_fnames.append(str(outf))

tensor_affine = nib.load(tensor_fnames[0]).affine
tensor_hdr = nib.load(tensor_fnames[0]).header
tensor_shape = nib.load(tensor_fnames[0]).get_data().shape
component_shape = tensor_shape[:3] + (len(tensor_fnames),)
tensor0 = np.zeros(component_shape)
tensor1 = np.zeros(component_shape)
tensor2 = np.zeros(component_shape)
tensor3 = np.zeros(component_shape)
tensor4 = np.zeros(component_shape)
tensor5 = np.zeros(component_shape)

for i, ten in enumerate(tensor_fnames):
    tendata = nib.load(ten).get_data()
    tensor0[:, :, :, i] = tendata[:, :, :, 0]
    tensor1[:, :, :, i] = tendata[:, :, :, 1]
    tensor2[:, :, :, i] = tendata[:, :, :, 2]
    tensor3[:, :, :, i] = tendata[:, :, :, 3]
    tensor4[:, :, :, i] = tendata[:, :, :, 4]
    tensor5[:, :, :, i] = tendata[:, :, :, 5]

mean_tensor0 = np.mean(tensor0, axis=3)
mean_tensor1 = np.mean(tensor1, axis=3)
mean_tensor2 = np.mean(tensor2, axis=3)
mean_tensor3 = np.mean(tensor3, axis=3)
mean_tensor4 = np.mean(tensor4, axis=3)
mean_tensor5 = np.mean(tensor5, axis=3)

mean_tensors = [mean_tensor0[:,:,:,None], mean_tensor1[:,:,:,None], mean_tensor2[:,:,:,None], mean_tensor3[:,:,:,None], mean_tensor4[:,:,:,None], mean_tensor5[:,:,:,None]]
mean_tensor = np.zeros(tensor_shape)
mean_tensor = np.concatenate(mean_tensors, axis=3)

mean_tensor_img = nib.Nifti1Image(mean_tensor, tensor_affine, tensor_hdr)
mean_tensor_img.set_qform(tensor_affine, code=2)
mean_tensor_img.set_sform(tensor_affine, code=2)
nib.save(mean_tensor_img, str(outdir/mean_tensor_fname))
provenance.log(str(outdir/mean_tensor_fname), 'reg to template and calculate mean tensor', tensor_fnames, script=__file__)
nii2nrrd(str(outdir/mean_tensor_fname), str(outdir/mean_tensor_fname).replace('.nii', '.nhdr'), istensor=True)

