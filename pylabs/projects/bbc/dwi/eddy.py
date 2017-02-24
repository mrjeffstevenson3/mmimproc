#this script takes converted bbc dti data, skull strips and performs eddy current correction with and without
#--repol replace outliers
import os, inspect, datetime
from pathlib import *
from os.path import join, basename, dirname, isfile, isdir, split
import numpy as np
import nibabel as nib
import pylabs
from scipy.ndimage.measurements import center_of_mass as com
from scipy.ndimage.filters import median_filter as medianf
from nipype.interfaces import fsl
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI')
bet = fsl.BET(output_type='NIFTI')
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.segment.mask import applymask
from pylabs.io.images import savenii
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc, dwi_passed_101
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
pylabs_basepath = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2])
MNI_bet_zcut = pylabs_basepath / 'data' / 'atlases' / 'MNI152_T1_1mm_bet_zcut.nii.gz'
MNI_bet_zcut_mask = pylabs_basepath / 'data' / 'atlases' / 'MNI152_T1_1mm_bet_zcut_mask.nii.gz'
MNI_bet_com = pylabs_basepath / 'data' / 'atlases' / 'MNI152_T1_1mm-com-mask8k.nii.gz'
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwi_passed_101]

for dwif in dwi_fnames:
    infpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
    fdwi = infpath / str(dwif + '.nii')
    fbvecs = infpath / str(dwif + '.bvecs')
    fbvals = infpath / str(dwif + '.bvals')
    fdwell = infpath / str(dwif + '.dwell_time')
    S0_fname = infpath / str(dwif + '_S0.nii')
    with WorkingContext(infpath):
        bvals, bvecs = read_bvals_bvecs(str(fbvals), str(fbvecs))
        # make dipy gtab and load dwi data
        gtab = gradient_table(bvals, bvecs)
        img = nib.load(str(fdwi))
        data = img.get_data()
        # make S0 and bet to get mask
        S0 = data[:, :, :, gtab.b0s_mask]
        S0 = medianf(S0, size=3)
        nS0_img = nib.Nifti1Image(S0, img.affine)
        nS0_img.set_qform(img.affine, code=1)
        nib.save(nS0_img, str(S0_fname))
        provenance.log(str(S0_fname), 'S0 dwi from '+str(fdwi), str(fdwi), code=__file__)
        #setup result object capture
        fslresult = ()
        dt = datetime.datetime.now()
        fslresult += (str(dt),'flirt_zcut2S0')
        # make mat file to apply mask and com
        flt.inputs.in_file = str(MNI_bet_zcut)
        flt.inputs.reference = str(S0_fname)
        flt.inputs.out_matrix_file = str(S0_fname)[: -6] + 'bet2S0.mat'
        flt.inputs.out_file = str(S0_fname)[: -6] + 'S0_zcut.nii'
        result = flt.run()
        fslresult += (result,)
        # apply mat file to center of mass ROI in MNI template
        dt = datetime.datetime.now()
        fslresult += (str(dt),'applyxfm_com2S0')
        applyxfm.inputs.in_matrix_file = str(S0_fname)[: -6] + 'bet2S0.mat'
        applyxfm.inputs.in_file = str(MNI_bet_com)
        applyxfm.inputs.out_file = str(infpath / str(dwif + '_S0_match_bet_com_roi.nii'))
        applyxfm.inputs.reference = str(S0_fname)
        applyxfm.inputs.apply_xfm = True
        result = applyxfm.run()
        fslresult += (result,)
        # apply mat file to MNI mask file to cut off neck
        dt = datetime.datetime.now()
        fslresult += (str(dt),'applyxfm_mask2S0')
        applyxfm.inputs.in_matrix_file = str(S0_fname)[: -6] + 'bet2S0.mat'
        applyxfm.inputs.in_file = str(MNI_bet_zcut_mask)
        applyxfm.inputs.out_file = str(infpath / str(dwif + '_S0_mask.nii'))
        applyxfm.inputs.reference = str(S0_fname)
        applyxfm.inputs.apply_xfm = True
        result = applyxfm.run()
        fslresult += (result,)
        # chop off neck with MNI zcut
        zcut_data = nib.load(str(infpath / str(dwif + '_S0_mask.nii'))).get_data()
        zcut_data_maskb = zcut_data > 0
        S0_mask = np.zeros(np.squeeze(S0).shape)  # need to add a fourth dim here
        S0_mask[zcut_data_maskb] = 1
        S0_zcut = applymask(S0, S0_mask)
        savenii(S0_zcut, img.affine, str(infpath / str(dwif + '_S0_zcut.nii')))

        # get com for fsl bet
        com_data = nib.load(str(infpath / str(dwif + '_S0_match_bet_com_roi.nii'))).get_data()
        com_data_maskb = com_data > 4000
        com_data_mask = np.zeros(com_data.shape)
        com_data_mask[com_data_maskb] = 1
        match_com = np.round(com(com_data_mask)).astype(int)

        # extract brain and make brain mask before eddy current correction
        brain_outfname = str(S0_fname)[: -6] + 'S0_brain'
        bet.inputs.in_file = str(infpath / str(dwif + '_S0_zcut.nii'))
        bet.inputs.center = list(match_com)
        bet.inputs.frac = 0.3
        bet.inputs.mask = True
        bet.inputs.skull = True
        bet.inputs.out_file = brain_outfname + '.nii'
        result = bet.run()
        fslresult += (result,)
        provenance.log(brain_outfname + '.nii', 'brain extracted S0 dwi from ' + str(dwif), str(S0_fname), code=__file__)
        provenance.log(brain_outfname + '_mask.nii', 'dwi brain mask from ' + str(dwif), str(S0_fname), code=__file__)
        # make index and acquisition parameters files
        with open(str(infpath / 'index.txt'), 'w') as f:
            f.write('1 ' * len(gtab.bvals))

        with open(fdwell, 'r') as f:
            dwell = f.read().replace('\n', '')

        with open(join(infpath, 'acq_params.txt'), 'w') as f:
            f.write('0 1 0 ' + dwell)

        # execute eddy command in subprocess in local working directory using repol and lower stddev and linear 2nd level model
        # winner of DWI preproc deathmatch Oct-2016
        outpath = str(infpath / 'cuda_repol_std2_S0mf3_v4')
        if not isdir(outpath):
            os.makedirs(outpath)
        cmd = ''
        output = ()
        dt = datetime.datetime.now()
        output += (str(dt), 'eddy cuda start time for '+str(fdwi))
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + str(fbvals) + ' --bvecs=' + str(fbvecs)
        cmd += ' --imain=' + str(fdwi) + ' --index=index.txt --mask=' + brain_outfname + '_mask.nii '
        cmd += '--out=' + str(outpath / str(dwif + '_eddy_corrected_repol_std2')) + ' --repol --ol_sqr --slm=linear --ol_nstd=2 --niter=9 --fwhm=20,5,0,0,0,0,0,0,0'
        cmdt = (cmd,)
        output += cmdt
        output += run_subprocess(cmd)
        dt = datetime.datetime.now()
        output += (str(dt), 'eddy cuda end time for '+str(fdwi))
        params = {}
        params['eddy cmd'] = cmd
        params['eddy output'] = output
        cmd = ''
        output = ()
        dt = datetime.datetime.now()
        output += (str(dt),)
        cmd += 'fslmaths '+ join(outpath, dwif + '_eddy_corrected_repol_std2') + ' -thr 1 ' + join(outpath, dwif + '_eddy_corrected_repol_std2_thr1')
        cmdt = (cmd,)
        output += cmdt
        output += run_subprocess(cmd)
        params['fslmaths clamping cmd'] = cmd
        params['fslmaths output'] = output
        provenance.log(join(outpath, dwif + '_eddy_corrected_repol_std2_thr1.nii.gz'), 'eddy using --repol --ol_sqr --slm=linear --ol_nstd=2 --niter=9 --fwhm=20,5,0,0,0,0,0,0,0',
                 fdwi, code=__file__, provenance=params)