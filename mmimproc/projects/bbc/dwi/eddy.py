#this script takes converted bbc dti data, skull strips and performs eddy current correction with and without
#--repol replace outliers
import os, inspect, datetime
from pathlib import *
import numpy as np
import nibabel as nib
import mmimproc
from scipy.ndimage.measurements import center_of_mass as com
from scipy.ndimage.filters import median_filter as medianf
from nipype.interfaces import fsl
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.segment.mask import applymask
from mmimproc.io.images import savenii
from mmimproc.projects.bbc.dwi.passed_qc import dwi_passed_qc, dwi_passed_101
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.io.images import savenii
from mmimproc.conversion.nifti2nrrd import nii2nrrd
from mmimproc.utils import run_subprocess, WorkingContext
from mmimproc.utils.paths import getnetworkdataroot
#set up instances
provenance = ProvenanceWrapper()
fs = mmimproc.fs_local
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI')
bet = fsl.BET(output_type='NIFTI')
pylabs_basepath = Path(*Path(inspect.getabsfile(mmimproc)).parts[:-2])
#set paths for BET atlases
MNI_bet_zcut = pylabs_basepath / 'data' / 'atlases' / 'MNI152_T1_1mm_bet_zcut.nii.gz'
MNI_bet_zcut_mask = pylabs_basepath / 'data' / 'atlases' / 'MNI152_T1_1mm_bet_zcut_mask.nii.gz'
MNI_bet_com = pylabs_basepath / 'data' / 'atlases' / 'MNI152_T1_1mm-com-mask8k.nii.gz'
#set up project variables
project = 'bbc'
#directory where eddy current corrected data is stored
outdir = 'cuda_repol_std2_S0mf3_v5'
filterS0_string = ''
filterS0 = True
if filterS0:
    filterS0_string = '_withmf3S0'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in dwi_passed_qc]
override_mask = {'sub-bbc101_ses-2_dti_15dir_b1000_1': fs / project / 'sub-bbc101/ses-2/dwi/sub-bbc101_ses-2_dti_15dir_b1000_1_S0_brain_mask_jsedits.nii'}
#loop over pairs
for dwif in dwi_fnames:
    infpath = fs / project / dwif.split('_')[0] / dwif.split('_')[1] / 'dwi'
    fdwi = infpath / str(dwif + '.nii')
    fbvecs = infpath / str(dwif + '.bvecs')
    fbvals = infpath / str(dwif + '.bvals')
    fdwell = infpath / str(dwif + '.dwell_time')
    S0_fname = infpath / str(dwif + '_S0.nii')
    with WorkingContext(str(infpath)):
        bvals, bvecs = read_bvals_bvecs(str(fbvals), str(fbvecs))
        # make dipy gtab and load dwi data
        gtab = gradient_table(bvals, bvecs)
        img = nib.load(str(fdwi))
        data = img.get_data()
        # make S0 and bet to get mask
        S0 = data[:, :, :, gtab.b0s_mask]
        if filterS0:
            S0_fname = infpath / str(dwif + filterS0_string +'_S0.nii')
            S0 = medianf(S0, size=3)
            data[:, :, :, gtab.b0s_mask] = S0
            fdwi = infpath / str(dwif + filterS0_string + '.nii')
            savenii(data, img.affine, str(fdwi), header=img.header)
        savenii(S0, img.affine, str(S0_fname))
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

        with open(str(fdwell), 'r') as f:
            dwell = f.read().replace('\n', '')

        with open(str(infpath / 'acq_params.txt'), 'w') as f:
            f.write('0 1 0 ' + dwell)

        # execute eddy command in subprocess in local working directory using repol and lower stddev and linear 2nd level model
        # winner of DWI preproc deathmatch Oct-2016
        outpath = infpath / outdir
        if not outpath.is_dir():
            outpath.mkdir(parents=True)
        cmd = ''
        output = ()
        dt = datetime.datetime.now()
        output += (str(dt), 'eddy cuda start time for '+str(fdwi))
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + str(fbvals) + ' --bvecs=' + str(fbvecs)
        cmd += ' --imain=' + str(fdwi) + ' --index=index.txt --mask='
        if dwif in override_mask:
            cmd += str(override_mask[dwif])
        else:
            cmd += brain_outfname + '_mask.nii'
        cmd += ' --out=' + str(outpath / str(dwif + filterS0_string + '_ec'))
        cmd += ' --repol --ol_sqr --slm=linear --ol_nstd=2 --niter=9 --fwhm=20,5,0,0,0,0,0,0,0'
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
        cmd += 'fslmaths '+ str(outpath / str(dwif + filterS0_string + '_ec'))
        cmd += ' -thr 1 ' + str(outpath / str(dwif + filterS0_string + '_ec_thr1'))
        cmdt = (cmd,)
        output += cmdt
        output += run_subprocess(cmd)
        params['fslmaths clamping cmd'] = cmd
        params['fslmaths output'] = output
        provenance.log(str(outpath / str(dwif + filterS0_string + '_ec_thr1.nii.gz')),
                       'eddy using --repol --ol_sqr --slm=linear --ol_nstd=2 --niter=9 --fwhm=20,5,0,0,0,0,0,0,0',
                        str(fdwi), code=__file__, provenance=params)
