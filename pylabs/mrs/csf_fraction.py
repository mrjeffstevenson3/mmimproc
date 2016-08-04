import numpy as np
import nibabel
import nibabel.nifti1 as nifti1



f = '/media/DiskArray/shared_data/js/tadpole/JONA_DAY1/csf_segmentation/TADPOLE_PR20160803_MATCHING_SPEC_6_5.nii'
match_img = nibabel.load(f)
match_img_data = match_img.get_data()
match_hdr = match_img.header
sizex = match_hdr['pixdim'][1]
sizey = match_hdr['pixdim'][2]
sizez = match_hdr['pixdim'][3]

center = tuple([s/2 for s in match_img_data.shape])

cc_diff = round((cc_size / 2.) / sizez)
ap_diff = round((ap_size / 2.) / sizey)
lr_diff = round((lr_size / 2.) / sizex)
sizez = 0.9
sizey = 0.728
sizex = 0.729
affine = match_img.get_affine()
mask_img = np.zeros(match_img_data.shape)

maskfname = '/media/DiskArray/shared_data/js/tadpole/JONA_DAY1/csf_segmentation/TADPOLE_PR20160803_MATCHING_SPEC_6_5_sv_spec_mask2.nii.gz'
