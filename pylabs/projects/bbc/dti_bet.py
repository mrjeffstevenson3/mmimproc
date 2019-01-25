import niprov
from dipy.segment.mask import median_otsu
import dipy.reconst.dti as dti
reload(dti)
import numpy as np
import nibabel as nib
from scipy.ndimage.measurements import center_of_mass as com
import dipy.data as dpd
from dipy.segment.mask import applymask
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
from pylabs.utils.paths import getnetworkdataroot
fs = getnetworkdataroot()
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc
from nipype.interfaces.fsl import Eddy
eddy = Eddy(num_threads=24, output_type='NIFTI')
from nipype.interfaces import fsl
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI')
bet = fsl.BET(output_type='NIFTI')
prov = niprov.ProvenanceContext()

import pylabs, os, inspect
from os.path import split
from os.path import join
pylabs_basepath = split(split(inspect.getabsfile(pylabs))[0])[0]
#set up files to process
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'

subjid = [105]
sespassqc = [1]
methodpassqc = ['dti_15dir_b1000']
runpassqc = [1]
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in zip(subjid, sespassqc, methodpassqc, runpassqc)]
#add for loop over dwi_fnames here:
dwi_fname = dwi_fnames[0]
fpath = join(fs, project, dwi_fname.split('_')[0] , dwi_fname.split('_')[1], 'dwi')
fdwi = join(fpath, dwi_fname + '.nii')
fbvecs = join(fpath, dwi_fname + '.bvecs')
fbvals = join(fpath, dwi_fname + '.bvals')
fdwell = join(fpath, dwi_fname + '.dwell_time')
S0_fname = join(fpath, dwi_fname + '_S0.nii')
#make dipy gtab and load dwi data
bvals, bvecs = read_bvals_bvecs(fbvals, fbvecs)
gtab = gradient_table(bvals, bvecs)
img = nib.load(fdwi)
data = img.get_data()
#make S0 and bet to get mask
S0 = data[:, :, :, gtab.b0s_mask]
nS0_img = nib.Nifti1Image(S0, img.affine)
nS0_img.set_qform(img.affine, code=1)
nib.save(nS0_img, S0_fname)

#make mat file to apply mask and com
flt.inputs.in_file = join(pylabs_basepath, 'data', 'atlases', 'MNI152_T1_1mm_bet_zcut.nii.gz')
flt.inputs.reference = S0_fname
flt.inputs.out_matrix_file = S0_fname[: -6] + 'bet2S0.mat'
flt.inputs.out_file = S0_fname[: -6] + 'S0_zcut.nii'
res = flt.run()
#apply mat file to center of mass ROI in MNI template
applyxfm.inputs.in_matrix_file = S0_fname[: -6] + 'bet2S0.mat'
applyxfm.inputs.in_file = join(pylabs_basepath, 'data', 'atlases', 'MNI152_T1_1mm-com-mask8k.nii.gz')
applyxfm.inputs.out_file = join(fpath, dwi_fname + '_S0_match_bet_com_roi.nii')
applyxfm.inputs.reference = S0_fname
applyxfm.inputs.apply_xfm = True
result = applyxfm.run()
#apply mat file to MNI mask file to cut off neck
applyxfm.inputs.in_matrix_file = S0_fname[: -6] + 'bet2S0.mat'
applyxfm.inputs.in_file = join(pylabs_basepath, 'data', 'atlases', 'MNI152_T1_1mm_bet_zcut_mask.nii.gz')
applyxfm.inputs.out_file = join(fpath, dwi_fname + '_S0_mask.nii')
applyxfm.inputs.reference = S0_fname
applyxfm.inputs.apply_xfm = True
result = applyxfm.run()
#chop off neck with MNI zcut
zcut_data = nib.load(join(fpath, dwi_fname + '_S0_mask.nii')).get_data()
zcut_data_maskb = zcut_data > 0
S0_mask = np.zeros(np.squeeze(S0).shape)  # need to add a fourth dim here
S0_mask[zcut_data_maskb] = 1
S0_zcut = applymask(S0, S0_mask)
nzcut_img = nib.nifti1.Nifti1Image(S0_zcut, img.affine)
nzcut_img.set_qform(img.affine, code=1)
nib.save(nzcut_img, join(fpath, dwi_fname + '_S0_zcut.nii'))

#get com for fsl bet
com_data = nib.load(join(fpath, dwi_fname + '_S0_match_bet_com_roi.nii')).get_data()
com_data_maskb = com_data > 4000
com_data_mask = np.zeros(com_data.shape)
com_data_mask[com_data_maskb] = 1
match_com = np.round(com(com_data_mask)).astype(int)

#extract brain and make brain mask before eddy current correction
brain_outfname = S0_fname[: -6] + 'S0_brain'
bet.inputs.in_file = join(fpath, dwi_fname + '_S0_zcut.nii')
bet.inputs.center = list(match_com)
bet.inputs.frac = 0.3
bet.inputs.mask = True
bet.inputs.skull = True
bet.inputs.out_file = brain_outfname + '.nii'
betres = bet.run()
prov.log(brain_outfname + '.nii', 'bet S0 brain for eddy', fdwi, script=__file__)
prov.log(brain_outfname + '_mask.nii', 'S0 brain mask for eddy mask', fdwi, script=__file__)
