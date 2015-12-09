import pylabs.alignment.phantom
from os.path import join

datadir = join('data','phantom_align_samples')
targetfile = join(datadir,'T1_seir_mag_TR4000_2014-07-23_1.nii.gz')
# loop over phantoms
newAffine = nibabel.load(targetfile).get_affine()
subjectfile = join(datadir,'T1_seir_mag_TR4000_2014-07-03_1.nii.gz')
newFile = subjectfile.replace('.nii','_coreg723.nii')
xform = pylabs.alignment.phantom.align(subjectfile, targetfile)
pylabs.alignment.phantom.savetransformed(subjectfile, xform, newFile, newAffine)

#    ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(pr_img.affine))
#    t_aff = inv_ornt_aff(ornt, pr_img.shape)
#    affine = np.dot(pr_img.affine, t_aff)
#    in_data_ras = apply_orientation(in_data, affine)
#xaffine = pylabs.alignment.spaces.xform2affine(**xform)
#xform = {
#    'tx':x,
#    'ty':y,
#    'rxy':r,
#}
