from __future__ import division
import numpy as np
import os
import nibabel
import nibabel.nifti1 as nifti1
from pylabs.utils.provenance import ProvenanceWrapper
from nipype.interfaces import fsl
from os.path import join
from scipy.ndimage.measurements import center_of_mass as com
from pylabs.conversion.parrec import par_to_nii
from pylabs.utils.paths import getpylabspath
from pylabs.utils import InDir
from pylabs.io.spar import load as readspar
from pylabs.utils.paths import getnetworkdataroot
fs = getnetworkdataroot()
prov = ProvenanceWrapper()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI')
bet = fsl.BET(output_type='NIFTI')
fast = fsl.FAST(output_type='NIFTI')


project = 'nbwr'
subject = 'sub-nbwr999b'
session = 'ses-1'

try:
    os.makedirs(join(fs, project, subject, session, 'mrs'))
except OSError:
    if not os.path.isdir(join(fs, project, subject, session, 'mrs')):
        raise
tempmrs = InDir(join(fs, project, subject, session, 'mrs'))

sparf = 'NWBR999B_WIP_LTPRESS_TE80_GLU_48MEAS_9_2_raw_act.SPAR'
sparfname = join(fs, project, subject, session, 'source_parrec', sparf)
matching_parfname = 'NWBR999B_LT_VBM_MATCHING_SPEC_3_7.PAR'
parfile = join(fs, project, subject, session, 'source_parrec', matching_parfname)
paroutfname = join(fs, project, subject, session, 'mrs', subject + '_mpr_match_sv')
maskfname = join(fs, project, subject, session, 'mrs', subject + '_glu_sv_voi_mask.nii.gz')
spar = readspar(sparfname)
# prov.add(parfile)

args = {'infile': parfile, 'outfilename': paroutfname, 'compressed': False,
        'overwrite': True, 'scaling': 'dv'}
par_to_nii(**args)
# prov.log(paroutfname + '.nii', 'converted fm parfile with par_to_nii', parfile)
match_img = nibabel.load(paroutfname + '.nii')
match_hdr = match_img.header
match_img_data = match_img.get_data()
affine = match_img.get_affine()
mask_img = np.zeros(match_img_data.shape)
lr_diff = round((spar['lr_size'] / 2.) / match_hdr.get_zooms()[0])
ap_diff = round((spar['ap_size'] / 2.) / match_hdr.get_zooms()[1])
cc_diff = round((spar['cc_size'] / 2.) / match_hdr.get_zooms()[2])
startx = int((match_img_data.shape[0] / 2.0) - lr_diff)
endx = int((match_img_data.shape[0] / 2.0) + lr_diff)
starty = int((match_img_data.shape[1] / 2.0) - ap_diff)
endy = int((match_img_data.shape[1] / 2.0) + ap_diff)
startz = int((match_img_data.shape[2] / 2.0) - cc_diff)
endz = int((match_img_data.shape[2] / 2.0) + cc_diff)
mask_img[startx:endx, starty:endy, startz:endz] = 1

nmask_img = nifti1.Nifti1Image(mask_img, affine, match_hdr)
nmask_hdr = nmask_img.header
nmask_hdr.set_qform(affine, code=2)
nibabel.save(nmask_img, maskfname)
# prov.log(maskfname, 'sv mrs voi mask file created for csf fraction', sparfname, script=__file__)

flt.inputs.in_file = join(getpylabspath(), 'data', 'atlases', 'MNI152_T1_1mm_bet_zcut.nii.gz')
flt.inputs.reference = paroutfname + '.nii'
flt.inputs.out_matrix_file = join(fs, project, subject, session, 'mrs', subject + 'mpr_match_sv.mat')
flt.inputs.out_file = join(fs, project, subject, session, 'mrs', subject + 'match_bet_zcut_MNIroi.nii')
res = flt.run()
applyxfm.inputs.in_matrix_file = join(fs, project, subject, session, 'mrs', subject + 'mpr_match_sv.mat')
applyxfm.inputs.in_file = join(getpylabspath(), 'data', 'atlases', 'MNI152_T1_1mm-com-mask8k.nii.gz')
applyxfm.inputs.out_file = join(fs, project, subject, session, 'mrs', subject + 'match_bet_com_roi.nii')
applyxfm.inputs.reference = paroutfname + '.nii'
applyxfm.inputs.apply_xfm = True
result = applyxfm.run()

#chop off neck with MNI zcut
zcut_data = nibabel.load(join(fs, project, subject, session, 'mrs', subject + 'match_bet_zcut_MNIroi.nii')).get_data()
zcut_data_maskb = zcut_data > 4000
zcut_data_mask = np.zeros(zcut_data.shape)
zcut_data_mask[zcut_data_maskb] = 1
zcut = int(np.round(com(zcut_data_mask))[2])
match_img_data[:,:,0:zcut] = 0
nzcut_img = nibabel.nifti1.Nifti1Image(match_img_data, affine, match_hdr)
nzcut_img.set_qform(affine, code=2)
nibabel.save(nzcut_img, join(fs, project, subject, session, 'mrs', subject + 'match_sv_zcut.nii'))

#get com for fsl bet
com_data = nibabel.load(join(fs, project, subject, session, 'mrs', subject + 'match_bet_com_roi.nii')).get_data()
com_data_maskb = com_data > 4000
com_data_mask = np.zeros(com_data.shape)
com_data_mask[com_data_maskb] = 1
match_com = np.round(com(com_data_mask)).astype(int)

#extract brain before segmenting
brain_outfname = join(fs, project, subject, session, 'mrs', subject + '_mpr_match_sv_brain.nii')
bet.inputs.in_file = join(fs, project, subject, session, 'mrs', subject + 'match_sv_zcut.nii')
bet.inputs.center = list(match_com)
bet.inputs.frac = 0.3
bet.inputs.mask = True
bet.inputs.skull = True
bet.inputs.out_file = brain_outfname
betres = bet.run()
# prov.log(brain_outfname, 'bet brain for segmentation', paroutfname + '.nii', script=__file__)

#segmentation using fsl fast
tempmrs.__enter__()
fast.inputs.in_files = join(fs, project, subject, session, 'mrs', subject + '_mpr_match_sv_brain.nii')
fast.inputs.img_type = 1
fast.inputs.number_classes = 3
fast.inputs.hyper = 0.1
fast.inputs.bias_iters = 4
fast.inputs.bias_lowpass = 20
fast.inputs.output_biascorrected = True
fast.inputs.output_biasfield = True
fast.inputs.segments = True
fast.inputs.probability_maps = True
fast.inputs.out_basename = join(fs, project, subject, session, 'mrs', subject + '_match_sv')
fastres = fast.run()

GM_seg_data = nibabel.load(join(fs, project, subject, session, 'mrs', subject + '_match_sv_seg_1.nii')).get_data()
GM_voi = GM_seg_data * mask_img
GM_num_vox = np.count_nonzero(GM_voi)
WM_seg_data = nibabel.load(join(fs, project, subject, session, 'mrs', subject + '_match_sv_seg_2.nii')).get_data()
WM_voi = WM_seg_data * mask_img
WM_num_vox = np.count_nonzero(WM_voi)
CSF_seg_data = nibabel.load(join(fs, project, subject, session, 'mrs', subject + '_match_sv_seg_0.nii')).get_data()
CSF_voi = CSF_seg_data * mask_img
CSF_num_vox = np.count_nonzero(CSF_voi)
mask_num_vox = np.count_nonzero(mask_img)

with open(join(fs, project, subject, session, 'mrs', subject + '_sv_voi_tissue_proportions.txt'), "w") as f:
    f.write('CSF: {0}\nGM: {1}\nWM: {2}\n'.format('{:.3%}'.format(CSF_num_vox / mask_num_vox),
                                                '{:.3%}'.format(GM_num_vox / mask_num_vox),
                                                '{:.3%}'.format(WM_num_vox / mask_num_vox)))

os.chdir(tempmrs._orig_dir)
# prov.log(join(fs, project, subject, session, 'mrs', subject + '_match_sv_seg_0.nii'), 'CSF segmentation', brain_outfname, script=__file__)
# prov.log(join(fs, project, subject, session, 'mrs', subject + '_match_sv_seg_1.nii'), 'GM segmentation', brain_outfname, script=__file__)
# prov.log(join(fs, project, subject, session, 'mrs', subject + '_match_sv_seg_2.nii'), 'WM segmentation', brain_outfname, script=__file__)
# prov.log(join(fs, project, subject, session, 'mrs', subject + '_sv_voi_tissue_proportions.txt'), 'results file containing %tissue values', brain_outfname, script=__file__)
