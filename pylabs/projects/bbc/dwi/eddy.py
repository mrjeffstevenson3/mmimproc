#this script takes converted bbc dti data, skull strips and performs eddy current correction with and without
#--repol replace outliers
import os, inspect
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
from dipy.segment.mask import applymask
prov = niprov.ProvenanceContext()
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
fs = getnetworkdataroot()
pylabs_basepath = split(split(inspect.getabsfile(pylabs))[0])[0]
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
subjid, sespassqc, runpassqc = zip(*dwi_passed_qc)
methodpassqc = ['dti_15dir_b1000'] * len(dwi_passed_qc)
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in zip(subjid, sespassqc, methodpassqc, runpassqc)]

for dwif in dwi_fnames:
    infpath = join(fs, project, dwif.split('_')[0] , dwif.split('_')[1], 'dwi')
    fdwi = join(infpath, dwif + '.nii')
    fbvecs = join(infpath, dwif + '.bvecs')
    fbvals = join(infpath, dwif + '.bvals')
    fdwell = join(infpath, dwif + '.dwell_time')
    S0_fname = join(infpath, dwif + '_S0.nii')
    with WorkingContext(infpath):
        bvals, bvecs = read_bvals_bvecs(fbvals, fbvecs)
        # make dipy gtab and load dwi data
        gtab = gradient_table(bvals, bvecs)
        img = nib.load(fdwi)
        data = img.get_data()
        # make S0 and bet to get mask
        S0 = data[:, :, :, gtab.b0s_mask]
        nS0_img = nib.Nifti1Image(S0, img.affine)
        nS0_img.set_qform(img.affine, code=1)
        nib.save(nS0_img, S0_fname)
        prov.log(S0_fname, 'S0 dwi from '+dwif, fdwi, code=__file__)
        # make mat file to apply mask and com
        flt.inputs.in_file = join(pylabs_basepath, 'data', 'atlases', 'MNI152_T1_1mm_bet_zcut.nii.gz')
        flt.inputs.reference = S0_fname
        flt.inputs.out_matrix_file = S0_fname[: -6] + 'bet2S0.mat'
        flt.inputs.out_file = S0_fname[: -6] + 'S0_zcut.nii'
        res = flt.run()
        # apply mat file to center of mass ROI in MNI template
        applyxfm.inputs.in_matrix_file = S0_fname[: -6] + 'bet2S0.mat'
        applyxfm.inputs.in_file = join(pylabs_basepath, 'data', 'atlases', 'MNI152_T1_1mm-com-mask8k.nii.gz')
        applyxfm.inputs.out_file = join(infpath, dwif + '_S0_match_bet_com_roi.nii')
        applyxfm.inputs.reference = S0_fname
        applyxfm.inputs.apply_xfm = True
        result = applyxfm.run()
        # apply mat file to MNI mask file to cut off neck
        applyxfm.inputs.in_matrix_file = S0_fname[: -6] + 'bet2S0.mat'
        applyxfm.inputs.in_file = join(pylabs_basepath, 'data', 'atlases', 'MNI152_T1_1mm_bet_zcut_mask.nii.gz')
        applyxfm.inputs.out_file = join(infpath, dwif + '_S0_mask.nii')
        applyxfm.inputs.reference = S0_fname
        applyxfm.inputs.apply_xfm = True
        result = applyxfm.run()
        # chop off neck with MNI zcut
        zcut_data = nib.load(join(infpath, dwif + '_S0_mask.nii')).get_data()
        zcut_data_maskb = zcut_data > 0
        S0_mask = np.zeros(np.squeeze(S0).shape)  # need to add a fourth dim here
        S0_mask[zcut_data_maskb] = 1
        S0_zcut = applymask(S0, S0_mask)
        nzcut_img = nib.nifti1.Nifti1Image(S0_zcut, img.affine)
        nzcut_img.set_qform(img.affine, code=1)
        nib.save(nzcut_img, join(infpath, dwif + '_S0_zcut.nii'))

        # get com for fsl bet
        com_data = nib.load(join(infpath, dwif + '_S0_match_bet_com_roi.nii')).get_data()
        com_data_maskb = com_data > 4000
        com_data_mask = np.zeros(com_data.shape)
        com_data_mask[com_data_maskb] = 1
        match_com = np.round(com(com_data_mask)).astype(int)

        # extract brain and make brain mask before eddy current correction
        brain_outfname = S0_fname[: -6] + 'S0_brain'
        bet.inputs.in_file = join(infpath, dwif + '_S0_zcut.nii')
        bet.inputs.center = list(match_com)
        bet.inputs.frac = 0.3
        bet.inputs.mask = True
        bet.inputs.skull = True
        bet.inputs.out_file = brain_outfname + '.nii'
        betres = bet.run()
        prov.log( brain_outfname + '.nii', 'brain extracted S0 dwi from ' + dwif, S0_fname, code=__file__)
        prov.log(brain_outfname + '_mask.nii', 'dwi brain mask from ' + dwif, S0_fname, code=__file__)
        # make index and acquisition parameters files
        with open(join(infpath, 'index.txt'), 'w') as f:
            f.write('1 ' * len(gtab.bvals))

        with open(fdwell, 'r') as f:
            dwell = f.read().replace('\n', '')

        with open(join(infpath, 'acq_params.txt'), 'w') as f:
            f.write('0 1 0 ' + dwell)
        # execute eddy command in subprocess in local working directory using defaults
        outpath = join(infpath, 'cuda_defaults')
        if not isdir(outpath):
            os.makedirs(outpath)
        cmd = ''
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + fbvals + ' --bvecs=' + fbvecs
        cmd += ' --imain=' + fdwi + ' --index=index.txt --mask=' + brain_outfname + '_mask.nii '
        cmd += '--out=' + join(outpath, dwif + '_eddy_corrected')
        run_subprocess(cmd)
        prov.log(join(outpath, dwif + '_eddy_corrected.nii.gz'), 'dwi eddy current correction using default options', fdwi, code=__file__)
        # execute eddy command in subprocess in local working directory using repol
        outpath = join(infpath, 'cuda_repol')
        if not isdir(outpath):
            os.makedirs(outpath)
        cmd = ''
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + fbvals + ' --bvecs=' + fbvecs
        cmd += ' --imain=' + fdwi + ' --index=index.txt --mask=' + brain_outfname + '_mask.nii '
        cmd += '--out=' + join(outpath, dwif + '_eddy_corrected_repol') + ' --repol'
        run_subprocess(cmd)
        prov.log(join(outpath, dwif + '_eddy_corrected_repol.nii.gz'), 'dwi eddy current correction using --repol options',
                 fdwi, code=__file__)
        # execute eddy command in subprocess in local working directory using repol and lower stddev and linear 2nd level model
        outpath = join(infpath, 'cuda_repol')
        if not isdir(outpath):
            os.makedirs(outpath)
        cmd = ''
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + fbvals + ' --bvecs=' + fbvecs
        cmd += ' --imain=' + fdwi + ' --index=index.txt --mask=' + brain_outfname + '_mask.nii '
        cmd += '--out=' + join(outpath, dwif + '_eddy_corrected_repol') + ' --repol --slm=linear --ol_nstd=2 --fwhm=20,20,0,0,0'
        run_subprocess(cmd)
        prov.log(join(outpath, dwif + '_eddy_corrected_repol.nii.gz'), 'dwi eddy current correction using --repol options',
                 fdwi, code=__file__)