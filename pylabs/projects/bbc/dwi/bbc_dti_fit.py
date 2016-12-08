import os, inspect, itertools
from pathlib import *
import numpy as np
import nibabel as nib
import pylabs
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
import dipy.denoise.noise_estimate as ne
from dipy.reconst.dti import mode
from scipy.ndimage.filters import median_filter as medianf
#from pylabs.diffusion.dti_fit import DTIFitCmds
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
#eddy corrected method directory. should get from eddy.
ec_meth = 'cuda_repol_std2_v2'
#fit methods to loop over
fitmeth = ['WLS', 'OLS', 'RESTORE']
_ut_rows = np.array([0, 0, 0, 1, 1, 2])
_ut_cols = np.array([0, 1, 2, 1, 2, 2])
_all_cols = np.zeros(9, dtype=np.int)
_all_rows = np.zeros(9, dtype=np.int)
for i, j in enumerate(list(itertools.product(*(range(3), range(3))))):
    _all_rows[i] = int(j[0])
    _all_cols[i] = int(j[1])
#save noise and residual maps only for weighted and restore methods
cam_part1b = ['cat noise_map.Bdouble noise_map.Bdouble | voxel2image -inputdatatype double -header %(mask_fname)s -outputroot noise_map',
             'cat residualmap.Bdouble | voxel2image -inputdatatype double -header %(mask_fname)s -outputroot residualmap',
            ]
#camino results files saved and tensors filtered, processed, and saved
cam_part2b = ['cat tensor.Bfloat | voxel2image -components 8 -header %(fdwi)s -outputroot %(fdwi_basen)s_%(m)s_tensor_',
                'fslmerge -t %(fdwi_basen)s_%(m)s_cam_tensor '
                         '%(fdwi_basen)s_%(m)s_tensor_0003.nii.gz '
                         '%(fdwi_basen)s_%(m)s_tensor_0004.nii.gz '
                         '%(fdwi_basen)s_%(m)s_tensor_0005.nii.gz '
                         '%(fdwi_basen)s_%(m)s_tensor_0006.nii.gz '
                         '%(fdwi_basen)s_%(m)s_tensor_0007.nii.gz '
                         '%(fdwi_basen)s_%(m)s_tensor_0008.nii.gz',
                 'fslmaths %(fdwi_basen)s_%(m)s_cam_tensor -fmedian %(fdwi_basen)s_%(m)s_cam_tensor_medfilt',
                 'nii2dt -inputfile %(fdwi_basen)s_%(m)s_cam_tensor_medfilt.nii.gz -bgmask %(mask_fname)s '
                        '-uppertriangular > tensor_medfilt.Bfloat',
                 'cat tensor.Bfloat | fa -header %(fdwi)s -outputfile %(fdwi_basen)s_%(m)s_cam_FA.nii.gz',
                 'cat tensor_medfilt.Bfloat | fa -header %(fdwi)s -outputfile %(fdwi_basen)s_%(m)s_cam_mf_FA.nii.gz',
                 'cat tensor.Bfloat | md -header %(fdwi)s -outputfile %(fdwi_basen)s_%(m)s_cam_MD.nii.gz',
                 'cat tensor_medfilt.Bfloat | md -header %(fdwi)s -outputfile %(fdwi_basen)s_%(m)s_cam_mf_MD.nii.gz',
                 'cat tensor.Bfloat | dteig | voxel2image -components 12 -inputdatatype double -header %(fdwi)s -outputroot eigsys_',
                 'cat tensor_medfilt.Bfloat | dteig | voxel2image -components 12 -inputdatatype double -header %(fdwi)s -outputroot eigsys_mf_',
                 'imcp eigsys_0001.nii.gz %(fdwi_basen)s_%(m)s_cam_L1',
                 'imcp eigsys_0005.nii.gz %(fdwi_basen)s_%(m)s_cam_L2',
                 'imcp eigsys_0009.nii.gz %(fdwi_basen)s_%(m)s_cam_L3',
                 'imcp eigsys_mf_0001.nii.gz %(fdwi_basen)s_%(m)s_cam_mf_L1',
                 'imcp eigsys_mf_0005.nii.gz %(fdwi_basen)s_%(m)s_cam_mf_L2',
                 'imcp eigsys_mf_0009.nii.gz %(fdwi_basen)s_%(m)s_cam_mf_L3',
                 'fslmaths %(fdwi_basen)s_%(m)s_cam_L2 -add %(fdwi_basen)s_%(m)s_cam_L3 -div 2 %(fdwi_basen)s_%(m)s_cam_RD',
                 'fslmaths %(fdwi_basen)s_%(m)s_cam_mf_L2 -add %(fdwi_basen)s_%(m)s_cam_mf_L3 -div 2 %(fdwi_basen)s_%(m)s_cam_mf_RD',
                 'fslmerge -t %(fdwi_basen)s_%(m)s_cam_V1 eigsys_0002.nii.gz  eigsys_0003.nii.gz  eigsys_0004.nii.gz',
                 'fslmerge -t %(fdwi_basen)s_%(m)s_cam_V2 eigsys_0006.nii.gz  eigsys_0007.nii.gz  eigsys_0008.nii.gz',
                 'fslmerge -t %(fdwi_basen)s_%(m)s_cam_V3 eigsys_0010.nii.gz  eigsys_0011.nii.gz  eigsys_0012.nii.gz',
                 'fslmerge -t %(fdwi_basen)s_%(m)s_cam_mf_V1 eigsys_mf_0002.nii.gz  eigsys_mf_0003.nii.gz  eigsys_mf_0004.nii.gz',
                 'fslmerge -t %(fdwi_basen)s_%(m)s_cam_mf_V2 eigsys_mf_0006.nii.gz  eigsys_mf_0007.nii.gz  eigsys_mf_0008.nii.gz',
                 'fslmerge -t %(fdwi_basen)s_%(m)s_cam_mf_V3 eigsys_mf_0010.nii.gz  eigsys_mf_0011.nii.gz  eigsys_mf_0012.nii.gz',
            ]
#main comand template dictionary for each fit method with %variables to be substituted later by cmdvars
cmds_d = {'RESTORE':
                    {'campart1':
                        ['modelfit -inputfile %(fdwi)s -schemefile ../scheme.txt -model ldt_wtd -noisemap noise_map.Bdouble '
                                '-residualmap residualmap.Bdouble -bgmask %(mask_fname)s -outputfile linear_tensor.Bfloat',
                         ]+ cam_part1b + [
                         'fslmaths noise_map -sqrt sigma_map',
                         'fslstats sigma_map -P 50'],
                    'campart2':
                        ['modelfit -inputfile %(fdwi)s -schemefile ../scheme.txt -model restore -sigma %(sigmac)s '
                         '-outliermap outlier_map.Bbyte -bgmask %(mask_fname)s -outputfile tensor.Bfloat',
                         'cat outlier_map.Bbyte | voxel2image -inputdatatype byte -components %(num_dirs)s -header %(fdwi)s -outputroot %(fdwi_basen)s_%(m)s_outlier_map_'
                         ] + cam_part2b

                     },
            'OLS': {'campart1': ['modelfit -inputfile %(fdwi)s -schemefile ../scheme.txt -model ldt -bgmask %(mask_fname)s -outputfile tensor.Bfloat']
                                + cam_part2b,

                    'fslpart1': ['dtifit --data=%(fdwi)s -m %(mask_fname)s --bvecs=%(fbvecs)s --bvals=%(fbvals)s --sse --save_tensor -o %(fdwi_basen)s_%(m)s_fsl',
                                'fslmaths %(fdwi_basen)s_%(m)s_fsl_tensor -fmedian %(fdwi_basen)s_%(m)s_fsl_tensor_medfilt',
                                'fslmaths %(fdwi_basen)s_%(m)s_fsl_tensor_medfilt -tensor_decomp %(fdwi_basen)s_%(m)s_fsl_tensor_mf'
                                ]
                    },
            'WLS': {'campart1': ['modelfit -inputfile %(fdwi)s -schemefile ../scheme.txt -model ldt_wtd -noisemap noise_map.Bdouble '
                                        '-residualmap residualmap.Bdouble -bgmask %(mask_fname)s -outputfile tensor.Bfloat']
                                 + cam_part1b + cam_part2b,

                    'fslpart1': ['dtifit --data=%(fdwi)s -m %(mask_fname)s --bvecs=%(fbvecs)s --bvals=%(fbvals)s --sse --save_tensor --wls -o %(fdwi_basen)s_%(m)s_fsl',
                                'fslmaths %(fdwi_basen)s_%(m)s_fsl_tensor -fmedian %(fdwi_basen)s_%(m)s_fsl_tensor_medfilt',
                                'fslmaths %(fdwi_basen)s_%(m)s_fsl_tensor_medfilt -tensor_decomp %(fdwi_basen)s_%(m)s_fsl_tensor_mf'
                        ]
            }
    }
#primary loop over subjects dwi
for dwif in dwi_fnames:
    infpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi' / ec_meth
    fdwi_basen = dwif + '_eddy_corrected_repol_std2'
    fdwi = infpath / str(fdwi_basen + '_thr1.nii.gz')
    fbvecs = infpath / str(fdwi_basen + '.eddy_rotated_bvecs')
    fbvals = Path(*infpath.parts[:-1]) / str(dwif + '.bvals')
    mask_fname = Path(*infpath.parts[:-1]) / str(dwif + '_S0_brain_mask.nii')
    #sets up variables to combine with cmds_d
    cmdvars = {'fdwi': str(fdwi), 'mask_fname': str(mask_fname), 'fdwi_basen': fdwi_basen, 'fbvecs': str(fbvecs), 'fbvals': str(fbvals)}
    with WorkingContext(str(infpath)):
        #set up for dipy
        bvals, bvecs = read_bvals_bvecs(str(fbvals), str(fbvecs))
        # make dipy gtab and load dwi data
        gtab = gradient_table(bvals, bvecs)
        cmdvars['num_dirs'] = np.count_nonzero(~gtab.b0s_mask)
        img = nib.load(str(fdwi))
        data = img.get_data()
        mask_img = nib.load(str(mask_fname))
        mask = mask_img.get_data()
        # set up camino for any method in dwi folder
        result = tuple()
        result += run_subprocess('fsl2scheme -bvecfile %(fbvecs)s -bvalfile %(fbvals)s > scheme.txt' % cmdvars)
        # make sure fit method directories exist
        (Path(infpath / m).mkdir() for m in fitmeth if not Path(infpath / m).is_dir())
        # loop over fit methods and used as keys in cmds_d dictionary
        for m in fitmeth:
            cmdvars['m'] = m.lower()
            with WorkingContext(m):
                # 1st do camino fits part1
                result += tuple([run_subprocess(c % cmdvars) for c in cmds_d[m]['campart1']])
                if m == 'RESTORE':
                    # calculate sigma variance for camino restore
                    cmdvars['sigmac'] = str(result[-1][0]).strip(' \n')
                    result += tuple([run_subprocess(c % cmdvars) for c in cmds_d[m]['campart2']])
                    # calculate sigma variance for dipy restore
                    sigmad = ne.estimate_sigma(data, N=1)  # N=1 for SENSE reconstruction (Philips scanners)
                    # now create dipy restore tensor model
                    tenmodel = dti.TensorModel(gtab, fit_method=m, sigma=sigmad, jac=False)
                else:
                    # create dipy tensor model
                    tenmodel = dti.TensorModel(gtab, fit_method=m)
                    # do FSL fits here
                    result += tuple([run_subprocess(c % cmdvars) for c in cmds_d[m]['fslpart1']])

                # dipy restore fails sometimes now with TypeError
                try:
                    fit = tenmodel.fit(data, mask)
                except TypeError:
                    print "Caught RESTORE type error for subj " + dwif
                    print "skipping to next method or subject"
                    pass
                else:
                    # filter and save all dipy files
                    fit_quad_form = fit.quadratic_form
                    fit_quad_form_mf = np.zeros(fit_quad_form.shape)
                    for r, c in zip(_all_rows, _all_cols):
                        fit_quad_form_mf[..., r, c] = medianf(fit_quad_form[..., r, c], size=1, mode='constant', cval=0)
                    tensor_ut = fit_quad_form[..., _ut_rows, _ut_cols]
                    tensor_ut_mf = fit_quad_form_mf[..., _ut_rows, _ut_cols]
                    savenii(tensor_ut, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_tensor.nii'))
                    savenii(tensor_ut_mf, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_tensor_medfilt.nii'))
                    savenii(fit.fa, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_FA.nii'), minmax=(0, 1))
                    savenii(fit.md, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_MD.nii'))
                    savenii(fit.rd, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_RD.nii'))
                    savenii(fit.ad, img.affine,infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_AD.nii'))
                    savenii(fit.mode, img.affine,infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_MO.nii'),minmax=(-1, 1))
                    # calculate eigenvalues for median filtered tensor and then FA, MD, RD etc and save
                    evals, evecs = np.linalg.eigh(fit_quad_form_mf)
                    evals = np.rollaxis(evals, axis=-1)  # order evals
                    all_zero = (evals == 0).all(axis=0)  # remove NaNs
                    ev1, ev2, ev3 = evals  # need to test if ev1 > ev2 > ev3
                    fa_mf = np.sqrt(0.5 * ((ev1 - ev2) ** 2 +
                                            (ev2 - ev3) ** 2 +
                                            (ev3 - ev1) ** 2) /
                                            ((evals * evals).sum(0) + all_zero))
                    savenii(fa_mf, img.affine,infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mf_FA.nii'), minmax=(0, 1))
                    savenii(evals.mean(0), img.affine,infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mf_MD.nii'))
                    savenii(ev1, img.affine, infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mf_AD.nii'))
                    savenii(evals[1:].mean(0), img.affine,infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mf_RD.nii'))
                    savenii(mode(fit_quad_form_mf), img.affine,infpath / m / str(fdwi_basen + '_' + m.lower() + '_dipy_mf_MO.nii'), minmax=(-1, 1))
