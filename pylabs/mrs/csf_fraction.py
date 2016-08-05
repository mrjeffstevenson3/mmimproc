import numpy as np
import os
import nibabel.parrec as pr
import nibabel.nifti1 as nifti1
import niprov
from nipype.interfaces import fsl
from os.path import join
import pandas as pd
from pylabs.conversion.parrec2nii_convert import BrainOpts
from pylabs.conversion.brain_convert import set_opts
from pylabs.conversion.parrec2nii_convert import brain_proc_file
from pylabs.utils.paths import getpylabspath
from pylabs.io.spar import load as readspar
from pylabs.utils.paths import getnetworkdataroot
fs = getnetworkdataroot()
opts = BrainOpts()
prov = niprov.ProvenanceContext()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')

project = 'tadpole'
subject = 'JONAH_DAY2'
setattr(opts, 'proj', project)
setattr(opts, 'subj', subject)
try:
    os.makedirs(join(fs, project, subject, 'mrs'))
except OSError:
    if not os.path.isdir(join(fs, project, subject, 'mrs')):
        raise

sparf = 'TADPOLE_PR20160804_WIP_PRESS_TE80_GLU_48MEAS_4_2_raw_act.SPAR'
sparfname = join(fs, project, subject, 'source_parrec', sparf)
matching_parfname = 'TADPOLE_PR20160804_MATCHING_SV_6_5.PAR'
parfile = join(fs, project, subject, 'source_parrec', matching_parfname)
paroutfname = join(fs, project, subject, 'mrs', subject + 'mpr_match_sv.nii.gz')
maskfname = join(fs, project, subject, 'mrs', subject + '_glu_sv_voi_mask.nii.gz')
spar = readspar(sparfname)



match_img = pr.load(parfile, scaling='dv')
match_img_data = match_img.get_data()
match_hdr = match_img.header
affine = match_img.get_affine()
nmatch_img = nifti1.Nifti1Image(match_img, affine, match_hdr)
nmatch_hdr = nmatch_img.header
nmatch_hdr.set_qform(affine, code=2)
np.testing.assert_almost_equal(affine, nmatch_hdr.get_qform(), 4,
                                       err_msg='output qform in header does not match input qform')
nibabel.save(nmatch_img, paroutfname)
prov.log(paroutfname, 'nifti file created for csf fraction and segmentation', parfile, script=__file__)
sizex = match_hdr['pixdim'][1]
sizey = match_hdr['pixdim'][2]
sizez = match_hdr['pixdim'][3]

lr_diff = round((spar['lr_off_center'] / 2.) / sizex)
ap_diff = round((spar['ap_off_center'] / 2.) / sizey)
cc_diff = round((spar['cc_off_center'] / 2.) / sizez)

mask_img = np.zeros(match_img_data.shape)
startx = (match_img_data.shape[0] / 2.0) - lr_diff
endx = (match_img_data.shape[0] / 2.0) + lr_diff
starty = (match_img_data.shape[1] / 2.0) - ap_diff
endy =(match_img_data.shape[1] / 2.0) + ap_diff
startz = (match_img_data.shape[2] / 2.0) - cc_diff
endz = (match_img_data.shape[2] / 2.0) + cc_diff
mask_img[startx:endx, starty:endy, startz:endz] = 1

nmask_img = nifti1.Nifti1Image(mask_img, affine, match_hdr)
nmask_hdr = nmask_img.header
nmask_hdr.set_qform(affine, code=2)
nibabel.save(nmask_img, maskfname)
prov.log(outfilename, 'sv mrs voi mask file created for csf fraction', infile, script=__file__)

flt.inputs.in_file = join(getpylabspath(), 'data', 'atlases', 'MNI152_T1_1mm_bet_zcut.nii.gz')
flt.inputs.reference = paroutfname
flt.inputs.out_matrix_file = join(fs, project, subject, 'mrs', subject + 'mpr_match_sv.mat')
res = flt.run()
applyxfm.inputs.in_matrix_file = join(fs, project, subject, 'mrs', subject + 'mpr_match_sv.mat')
applyxfm.inputs.in_file = join(getpylabspath(), 'data', 'atlases', 'MNI152_T1_1mm-com-mask8k.nii.gz')
applyxfm.inputs.out_file =
applyxfm.inputs.reference = paroutfname
applyxfm.inputs.apply_xfm = True
result = applyxfm.run()



