import os, inspect, itertools
from pathlib import *
import numpy as np
import nibabel as nib
import pylabs
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
from dipy.reconst.dti import mode
from scipy.ndimage.filters import median_filter as medianf
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc, dwi_passed_101
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.io.images import savenii
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-1])
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwi_passed_qc]
_ut_rows = np.array([0, 0, 0, 1, 1, 2])
_ut_cols = np.array([0, 1, 2, 1, 2, 2])
_all_cols = np.zeros(9, dtype=np.int)
_all_rows = np.zeros(9, dtype=np.int)
for i, j in enumerate(list(itertools.product(*(range(3), range(3))))):
    _all_rows[i] = int(j[0])
    _all_cols[i] = int(j[1])

for dwif in dwi_fnames:
    # for ec_meth in ['cuda_repol_std2']:     # death match ['cuda_defaults', 'cuda_repol', 'cuda_repol_std2']:
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
                # dipy restore fails
                # sigma = ne.estimate_sigma(data, N=1)  #N=1 for SENSE reconstruction (Philips scanners)
                # tenmodel = dti.TensorModel(gtab, fit_method=m, sigma=sigma, jac=False)
                run_subprocess('fsl2scheme -bvecfile '+str(fbvecs)+' -bvalfile '+str(fbvals)+' > '+m+'/scheme.txt')
                cmd = 'modelfit -inputfile '+str(fdwi)+' -schemefile '+m+'/scheme.txt -model ldt_wtd -noisemap '
                cmd += m+'/noise_map.Bdouble -bgmask '+str(mask_fname)+' -outputfile '+m+'/linear_tensor.Bfloat'
                run_subprocess(cmd)
                ## grab noise map twice b/c of strange camino bug where the noise map is undersized
                cmd = 'cat '+m+'/noise_map.Bdouble '+m+'/noise_map.Bdouble | voxel2image -inputdatatype double -header '
                cmd += str(mask_fname)+' -outputroot '+m+'/noise_map'
                run_subprocess(cmd)
                ## square root of the variance of the noise is sigma
                run_subprocess('fslmaths '+m+'/noise_map -sqrt '+m+'/sigma_map')
                ## get median of sigma map
                result = run_subprocess('fslstats '+m+'/sigma_map -P 50')
                sigma = result[0].strip(' \n')
                ## do the fitting
                cmd = 'modelfit -inputfile '+str(fdwi)+' -schemefile '+m+'/scheme.txt -model restore -sigma '
                cmd += sigma+' -outliermap '+m+'/outlier_map.Bbyte -bgmask '
                cmd += str(mask_fname)+' -outputfile '+m+'/restore_tensor.Bfloat'
                run_subprocess(cmd)
                with WorkingContext(m):
                    ## rename and convert files back to nii
                    run_subprocess('cat restore_tensor.Bfloat | fa -header '+str(fdwi)+' -outputfile '+str(
                        fdwi_basen)+'_'+m.lower()+'_fa.nii.gz')
                    run_subprocess('cat restore_tensor.Bfloat | md -header '+str(fdwi)+' -outputfile '+str(
                        fdwi_basen)+'_'+m.lower()+'_md.nii.gz')
                    run_subprocess('cat restore_tensor.Bfloat | voxel2image -components 8 -header '+str(
                        fdwi)+' -outputroot '+str(fdwi_basen)+'_'+m.lower()+'_tensor_')
                    run_subprocess('cat outlier_map.Bbyte | voxel2image -inputdatatype byte -components '+str(
                        num_dirs)+' -header '+str(fdwi)+' -outputroot '+str(fdwi_basen+'_'+m.lower()+'_outlier_map_'))
                    run_subprocess('cat restore_tensor.Bfloat | dteig | voxel2image -components 12 '
                                   '-inputdatatype double -header '+str(fdwi)+' -outputroot eigsys_')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_cam2fsl_tensor '
                                   +str(fdwi_basen)+'_'+m.lower()+'_tensor_0003.nii.gz '
                                   +str(fdwi_basen)+'_'+m.lower()+'_tensor_0004.nii.gz '
                                   +str(fdwi_basen)+'_'+m.lower()+'_tensor_0005.nii.gz '
                                   +str(fdwi_basen)+'_'+m.lower()+'_tensor_0006.nii.gz '
                                   +str(fdwi_basen)+'_'+m.lower()+'_tensor_0007.nii.gz '
                                   +str(fdwi_basen)+'_'+m.lower()+'_tensor_0008.nii.gz ')
                    run_subprocess('fslmaths '+str(fdwi_basen)+'_'+m.lower()+'_cam2fsl_tensor -fmedian '+str(
                        fdwi_basen + '_' + m.lower()+ '_cam2fsl_tensor_medfilt'))
                    run_subprocess('fslmaths '+str(fdwi_basen)+'_'+m.lower()+'_cam2fsl_tensor_medfilt -tensor_decomp '+str(
                        fdwi_basen+'_'+m.lower()+'_cam2fsl_tensor_mf'))
                    run_subprocess('imcp eigsys_0001.nii.gz '+str(fdwi_basen)+'_'+m.lower()+'_L1')
                    run_subprocess('imcp eigsys_0005.nii.gz '+str(fdwi_basen)+'_'+m.lower()+'_L2')
                    run_subprocess('imcp eigsys_0009.nii.gz '+str(fdwi_basen)+'_'+m.lower()+'_L3')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_V1 '
                                    'eigsys_0002.nii.gz  eigsys_0003.nii.gz  eigsys_0004.nii.gz')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_V2 '
                                    'eigsys_0006.nii.gz  eigsys_0007.nii.gz  eigsys_0008.nii.gz')
                    run_subprocess('fslmerge -t '+str(fdwi_basen)+'_'+m.lower()+'_V3 '
                                    'eigsys_0010.nii.gz  eigsys_0011.nii.gz  eigsys_0012.nii.gz')
                    #fix output headers
                    for f in [str(fdwi_basen)+'_'+m.lower()+'_fa.nii.gz', str(fdwi_basen)+'_'+m.lower()+'_md.nii.gz', str(fdwi_basen)+'_'+m.lower()+'_L1.nii.gz']:
                        r_img = nib.load(f)
                        savenii(r_img.get_data(), img.affine, f)
            else:
                tenmodel = dti.TensorModel(gtab, fit_method=m)
                fit = tenmodel.fit(data, mask)
                fit_quad_form = fit.quadratic_form
                fit_quad_form_mf = np.zeros(fit_quad_form.shape)
                for r, c in zip(_all_rows, _all_cols):
                    fit_quad_form_mf[..., r, c] = medianf(fit_quad_form[..., r, c], size=3, mode='constant', cval=0)
                tensor_ut = fit_quad_form[..., _ut_rows, _ut_cols]
                tensor_ut_mf = fit_quad_form_mf[..., _ut_rows, _ut_cols]
                savenii(tensor_ut, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_tensor.nii'))
                savenii(tensor_ut_mf, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_tensor_medfilt.nii'))
                savenii(fit.fa, img.affine, infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_fa.nii'), minmax=(0,1))
                savenii(fit.md, img.affine, infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_md.nii'))
                savenii(fit.rd, img.affine, infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_rd.nii'))
                savenii(fit.ad, img.affine, infpath / m / str(fdwi_basen +'_'+m.lower()+'_dipy_ad.nii'))
                savenii(fit.mode, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mo.nii'), minmax=(-1,1))
                #calculate eigenvalues for median filtered tensor and then FA, MD, RD etc and save
                evals, evecs = np.linalg.eigh(fit_quad_form_mf)
                evals = np.rollaxis(evals, axis=-1)  #order evals
                all_zero = (evals == 0).all(axis=0)  #remove NaNs
                ev1, ev2, ev3 = evals
                fa_mf = np.sqrt(0.5 * ((ev1 - ev2) ** 2 +
                                       (ev2 - ev3) ** 2 +
                                       (ev3 - ev1) ** 2) /
                                ((evals * evals).sum(0) + all_zero))
                savenii(fa_mf, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_fa_mf.nii'), minmax=(0, 1))
                savenii(evals.mean(0), img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_md_mf.nii'))
                savenii(ev1, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_ad_mf.nii'))
                savenii(evals[1:].mean(0), img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_rd_mf.nii'))
                savenii(mode(fit_quad_form_mf), img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mode_mf.nii'), minmax=(-1, 1))
                if m == 'OLS':
                    run_subprocess('dtifit --data='+str(fdwi)+' -m '+str(mask_fname)+' --bvecs='+str(fbvecs)+' --bvals='+str(
                        fbvals)+' --sse --save_tensor -o '+str(infpath / m / str(fdwi_basen +'_'+m.lower()+'_fsl')))
                    with WorkingContext(str(infpath / m)):
                        run_subprocess('fslmaths '+str(fdwi_basen)+ '_'+m.lower()+'_fsl_tensor -fmedian '+str(fdwi_basen+'_'+m.lower()+'_fsl_tensor_medfilt'))
                        run_subprocess('fslmaths '+str(fdwi_basen)+'_'+m.lower()+'_fsl_tensor_medfilt -tensor_decomp '+str(fdwi_basen+'_'+m.lower()+'_fsl_tensor_mf'))
                if m == 'WLS' and not dwif == 'sub-bbc101_ses-2_dti_15dir_b1000_1':
                    run_subprocess('dtifit --data='+str(fdwi)+' -m '+str(mask_fname)+' --bvecs='+str(fbvecs)+' --bvals='+str(
                            fbvals)+' --sse --save_tensor --wls -o '+str(infpath / m / str(fdwi_basen+'_'+m.lower()+'_fsl')))
                    with WorkingContext(str(infpath / m)):
                        run_subprocess('fslmaths ' + str(fdwi_basen) + '_' + m.lower() + '_fsl_tensor -fmedian ' + str(
                            fdwi_basen + '_' + m.lower() + '_fsl_tensor_medfilt'))
                        run_subprocess('fslmaths ' + str(fdwi_basen) + '_' + m.lower() + '_fsl_tensor_medfilt -tensor_decomp ' + str(
                            fdwi_basen + '_' + m.lower() + '_fsl_tensor_mf'))

