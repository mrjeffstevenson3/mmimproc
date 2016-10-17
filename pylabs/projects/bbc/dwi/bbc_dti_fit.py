import os, inspect
from pathlib import *
from os.path import join, basename, dirname, isfile, isdir, split
import numpy as np
import nibabel as nib
import niprov, pylabs
from scipy.ndimage.measurements import center_of_mass as com
from nipype.interfaces import fsl
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI')
bet = fsl.BET(output_type='NIFTI')
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
import dipy.denoise.noise_estimate as ne
from dipy.segment.mask import applymask
prov = niprov.ProvenanceContext()
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
fs = Path(getnetworkdataroot())
pylabs_basepath = split(split(inspect.getabsfile(pylabs))[0])[0]
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
subjid, sespassqc, runpassqc = zip(*dwi_passed_qc)
methodpassqc = ['dti_15dir_b1000'] * len(dwi_passed_qc)
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in zip(subjid, sespassqc, methodpassqc, runpassqc)]

for dwif in dwi_fnames:
    for ec_meth in ['cuda_defaults', 'cuda_repol', 'cuda_repol_std2']:
        infpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth
        fdwi_basen = dwif + '_eddy_corrected'
        if ec_meth == 'cuda_repol':
            fdwi_basen += '_repol'
        fdwi = infpath / str(fdwi_basen + '.nii.gz')
        fbvecs = infpath / str(fdwi_basen + '.eddy_rotated_bvecs')
        fbvals = Path(*infpath.parts[:-1]) / str(dwif + '.bvals')
        mask_fname = Path(*infpath.parts[:-1]) / str(dwif + '_S0_brain_mask.nii')
        with WorkingContext(str(infpath)):
            bvals, bvecs = read_bvals_bvecs(str(fbvals), str(fbvecs))
            # make dipy gtab and load dwi data
            gtab = gradient_table(bvals, bvecs)
            img = nib.load(str(fdwi))
            data = img.get_data()
            mask_img = nib.load(str(mask_fname))
            mask = mask_img.get_data()
            for m in ['WLS', 'OLS']: # 'RESTORE']:
                if m == 'RESTORE':
                    sigma = ne.estimate_sigma(data)
                    tenmodel = dti.TensorModel(gtab, fit_method=m, sigma=sigma)
                else:
                    tenmodel = dti.TensorModel(gtab, fit_method=m)
                fit = tenmodel.fit(data, mask)
                fa = fit.fa
                fa_img = nib.nifti1.Nifti1Image(fa, img.affine)
                fa_img.set_qform(img.affine, code=1)
                nib.save(fa_img, str(infpath / str(fdwi_basen +'_'+m+'_fa.nii')))
                md = fit.md
                md_img = nib.nifti1.Nifti1Image(md, img.affine)
                md_img.set_qform(img.affine, code=1)
                nib.save(md_img, str(infpath / str(fdwi_basen +'_'+m+'_md.nii')))
                rd = fit.rd
                rd_img = nib.nifti1.Nifti1Image(rd, img.affine)
                rd_img.set_qform(img.affine, code=1)
                nib.save(rd_img, str(infpath / str(fdwi_basen +'_'+m+'_rd.nii')))
                ad = fit.ad
                ad_img = nib.nifti1.Nifti1Image(ad, img.affine)
                ad_img.set_qform(img.affine, code=1)
                nib.save(ad_img, str(infpath / str(fdwi_basen +'_'+m+'_ad.nii')))
                mo = fit.mode
                mo_img = nib.nifti1.Nifti1Image(mo, img.affine)
                mo_img.set_qform(img.affine, code=1)
                nib.save(mo_img, str(infpath / str(fdwi_basen +'_'+m+'_mo.nii')))



