import os, inspect
from pathlib import *
from os.path import join, basename, dirname, isfile, isdir, split
import numpy as np
import nibabel as nib
import niprov, pylabs
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
import dipy.denoise.noise_estimate as ne
prov = niprov.ProvenanceContext()
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc, dwi_passed_101
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
fs = Path(getnetworkdataroot())
pylabs_basepath = split(split(inspect.getabsfile(pylabs))[0])[0]
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwi_passed_101]

for dwif in dwi_fnames:
#    for ec_meth in ['cuda_repol_std2']:     # death match ['cuda_defaults', 'cuda_repol', 'cuda_repol_std2']:
    ec_meth = 'cuda_repol_std2'
    infpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth
    fdwi_basen = dwif + '_eddy_corrected'
    if ec_meth == 'cuda_repol':
        fdwi_basen += '_repol'
    elif ec_meth == 'cuda_repol_std2':
        fdwi_basen += '_repol_std2'
    fdwi = infpath / str(fdwi_basen + '.nii.gz')
    fbvecs = infpath / str(fdwi_basen + '.eddy_rotated_bvecs')
    fbvals = Path(*infpath.parts[:-1]) / str(dwif + '.bvals')
    mask_fname = Path(*infpath.parts[:-1]) / str(dwif + '_S0_brain_mask.nii')
    with WorkingContext(str(infpath)):
        bvals, bvecs = read_bvals_bvecs(str(fbvals), str(fbvecs))
        # make dipy gtab and load dwi data
        gtab = gradient_table(bvals, bvecs)
        num_dirs = np.count_nonzero(~gtab.b0s_mask)
        img = nib.load(str(fdwi))
        data = img.get_data()
        mask_img = nib.load(str(mask_fname))
        mask = mask_img.get_data()
        for m in ['WLS', 'OLS', 'RESTORE']:
            if not os.path.isdir(m):
                os.makedirs(m)
            if m == 'RESTORE':
                #dipy restore fails
                # sigma = ne.estimate_sigma(data, N=1)  #N=1 for SENSE reconstruction (Philips scanners)
                # tenmodel = dti.TensorModel(gtab, fit_method=m, sigma=sigma, jac=False)
                run_subprocess('fsl2scheme -bvecfile '+str(fbvecs)+' -bvalfile '+str(fbvals)+' > '+m+'/scheme.txt')
                cmd = 'modelfit -inputfile '+str(fdwi)+' -schemefile scheme.txt -model ldt_wtd -noisemap noise_map.Bdouble -bgmask '
                cmd += str(mask_fname)+' -outputfile '+m+'/linear_tensor.Bfloat'  # -residualmap $tmpdir/residual_map.Bdouble
                run_subprocess(cmd)
                ## grab noise map twice b/c of strange camino bug where the noise map is undersized
                cmd = 'cat '+m+'/noise_map.Bdouble '+m+'/noise_map.Bdouble | voxel2image -inputdatatype double -header '+str(mask_fname)+' -outputroot '+m+'/noise_map'
                run_subprocess(cmd)
                ## square root of the variance of the noise is sigma
                run_subprocess('fslmaths '+m+'/noise_map -sqrt '+m+'/sigma_map')
                ## get median of sigma map
                result = run_subprocess('fslstats '+m+'/sigma_map -P 50')
                sigma = result[0].strip(' \n')
                ## do the fitting
                cmd = 'modelfit -inputfile '+str(fdwi)+' -schemefile '+m+'/scheme.txt -model restore -sigma '+sigma+' -outliermap '+m+'/outlier_map.Bbyte -bgmask '
                cmd += str(mask_fname)+' -outputfile '+m+'/restore_tensor.Bfloat'
                run_subprocess(cmd)
                with WorkingContext(m):
                    ## rename and convert files back to nii
                    run_subprocess('cat restore_tensor.Bfloat | fa -header '+str(fdwi)+' -outputfile '+str(fdwi_basen)+'_'+m.lower()+'_fa.nii.gz')
                    run_subprocess('cat restore_tensor.Bfloat | md -header '+str(fdwi)+' -outputfile '+str(fdwi_basen)+'_'+m.lower()+'_md.nii.gz')
                    run_subprocess('cat restore_tensor.Bfloat | voxel2image -components 8 -header '+str(fdwi)+' -outputroot '+str(fdwi_basen)+'_'+m.lower()+'_tensor_')
                    run_subprocess('cat outlier_map.Bbyte | voxel2image -inputdatatype byte -components '+str(num_dirs)+' -header '+str(fdwi)+' -outputroot '+str(fdwi_basen+'_'+m.lower()+'_outlier_map_'))
                    run_subprocess('cat restore_tensor.Bfloat | dteig | voxel2image -components 12 -inputdatatype double -header '+str(fdwi)+' -outputroot eigsys_')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0001.nii.gz exit_code')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0002.nii.gz log_s0')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0003.nii.gz dxx')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0004.nii.gz dxy')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0005.nii.gz dxz')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0006.nii.gz dyy')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0007.nii.gz dyz')
                    run_subprocess('imcp '+str(fdwi_basen)+'_'+m+'_tensor_0008.nii.gz dzz')
                    run_subprocess('imcp eigsys_0001.nii.gz '+str(fdwi_basen)+'_'+m.lower()+'_L1')
                    run_subprocess('imcp eigsys_0005.nii.gz '+str(fdwi_basen)+'_'+m.lower()+'_L2')
                    run_subprocess('imcp eigsys_0009.nii.gz '+str(fdwi_basen)+'_'+m.lower()+'_L3')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_V1 eigsys_0002.nii.gz  eigsys_0003.nii.gz  eigsys_0004.nii.gz')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_V2 eigsys_0006.nii.gz  eigsys_0007.nii.gz  eigsys_0008.nii.gz')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_V3 eigsys_0010.nii.gz  eigsys_0011.nii.gz  eigsys_0012.nii.gz')
                    #fix output headers
                    for f in [str(fdwi_basen)+'_'+m.lower()+'_fa.nii.gz', str(fdwi_basen)+'_'+m.lower()+'_md.nii.gz', str(fdwi_basen)+'_'+m.lower()+'_L1.nii.gz']:
                        r_img = nib.load(f)
                        r_img.set_qform(img.affine, code=1)
                        r_img.set_sform(img.affine, code=1)
                        np.testing.assert_almost_equal(img.affine, r_img.get_qform(), 4,
                                                       err_msg='output qform in header does not match input qform')
                        nib.save(r_img, f)

            else:
                tenmodel = dti.TensorModel(gtab, fit_method=m)
                fit = tenmodel.fit(data, mask)
                fa = fit.fa
                fa_img = nib.nifti1.Nifti1Image(fa, img.affine)
                fa_img.header['cal_max'] = 1
                fa_img.set_qform(img.affine, code=1)
                np.testing.assert_almost_equal(img.affine, fa_img.get_qform(), 4,
                                               err_msg='output qform in header does not match input qform')
                nib.save(fa_img, str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_fa.nii')))
                md = fit.md
                md_img = nib.nifti1.Nifti1Image(md, img.affine)
                md_img.header['cal_max'] = 1e-9
                md_img.header['cal_min'] = 0
                md_img.set_qform(img.affine, code=1)
                np.testing.assert_almost_equal(img.affine, md_img.get_qform(), 4,
                                               err_msg='output qform in header does not match input qform')
                nib.save(md_img, str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_md.nii')))
                rd = fit.rd
                rd_img = nib.nifti1.Nifti1Image(rd, img.affine)
                rd_img.header['cal_max'] = 1e-9
                rd_img.header['cal_min'] = 0
                rd_img.set_qform(img.affine, code=1)
                np.testing.assert_almost_equal(img.affine, rd_img.get_qform(), 4,
                                               err_msg='output qform in header does not match input qform')
                nib.save(rd_img, str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_rd.nii')))
                ad = fit.ad
                ad_img = nib.nifti1.Nifti1Image(ad, img.affine)
                ad_img.header['cal_max'] = 1e-9
                ad_img.header['cal_min'] = 0
                ad_img.set_qform(img.affine, code=1)
                np.testing.assert_almost_equal(img.affine, ad_img.get_qform(), 4,
                                               err_msg='output qform in header does not match input qform')
                nib.save(ad_img, str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_ad.nii')))
                mo = fit.mode
                mo_img = nib.nifti1.Nifti1Image(mo, img.affine)
                mo_img.header['cal_max'] = 1
                mo_img.header['cal_min'] = -1
                mo_img.set_qform(img.affine, code=1)
                np.testing.assert_almost_equal(img.affine, mo_img.get_qform(), 4,
                                               err_msg='output qform in header does not match input qform')
                nib.save(mo_img, str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_mo.nii')))
                if m == 'OLS':
                    run_subprocess('dtifit --data='+str(fdwi)+' -m '+str(mask_fname)+'--bvecs='+str(fbvecs)+' --bvals='+str(fbvals)+'--sse --save_tensor -o '+str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_fsl')))
                    with WorkingContext(str(infpath / m)):
                        run_subprocess('fslmaths '+str(fdwi_basen)+ '_'+m.lower()+'_fsl_tensor -fmedian '+str(fdwi_basen + '_' + m.lower() + '_fsl_tensor_mf'))
                        run_subprocess('fslmaths '+str(fdwi_basen)+'_'+m.lower()+'_fsl_tensor_mf -tensor_decomp '+str(fdwi_basen + '_' + m.lower() + '_fsl_tensor_mf'))
                if m == 'WLS':
                    run_subprocess(
                        'dtifit --data=' + str(fdwi) + ' -m ' + str(mask_fname) + '--bvecs=' + str(fbvecs) + ' --bvals=' + str(
                            fbvals) + '--sse --save_tensor --wls -o ' + str(infpath / m / str(fdwi_basen + '_' + m.lower() + '_fsl')))
                    with WorkingContext(str(infpath / m)):
                        run_subprocess('fslmaths ' + str(fdwi_basen) + '_' + m.lower() + '_fsl_tensor -fmedian ' + str(
                            fdwi_basen + '_' + m.lower() + '_fsl_tensor_mf'))
                        run_subprocess('fslmaths ' + str(fdwi_basen) + '_' + m.lower() + '_fsl_tensor_mf -tensor_decomp ' + str(
                            fdwi_basen + '_' + m.lower() + '_fsl_tensor_mf'))

