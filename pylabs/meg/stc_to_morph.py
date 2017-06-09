# this half baked script makes 1 morph file for a given stc time point.
# to do: make it flexible selecting project, subject, hemisphere, stc file(s) and time point(s)
import os.path as op
from pathlib import *
import numpy as np
import nibabel as nib
import mne


subject = 'sub-nbwr999b_ses-1_vbm_ti1200_rms_freesurf'
mne.set_config('SUBJECTS_DIR', '/Users/mrjeffs/Documents/Research/data/nbwr/sub-nbwr999b/ses-1')
subjects_dir = mne.get_config('SUBJECTS_DIR')
stc_files = ['Word-NonWord']
hemis = ['lh', 'rh']

############################

data_dir = mne.datasets.sample.data_path()
subjects_dir = data_dir + '/subjects'
stc = mne.read_source_estimate(data_dir + '/MEG/sample/sample_audvis-meg', subject=subject)
surfs = dict((hemi, mne.read_surface(op.join(subjects_dir, subject, 'surf', hemi + '.pial'))) for hemi in hemis)
all_vertices = [np.arange(len(surfs[hemi][0])) for hemi in hemis]
fill_mat = mne.compute_morph_matrix(subject, subject, stc.vertices, all_vertices, smooth=10, subjects_dir=subjects_dir)
stc = stc.morph_precomputed(subject, all_vertices, fill_mat)
template_fname = op.join(subjects_dir, subject, 'mri', 'orig.mgz')
idx = np.abs(stc.times - 0.2).argmin()
for hemi in hemis:
    this_data = getattr(stc, hemi + '_data')[:, idx]
    data_fname = '%s.curv' % hemi
    nib.freesurfer.write_morph_data(data_fname, this_data, fnum=surfs[hemi][1].shape[0])

############################# Eric's code



stc = mne.read_source_estimate(str(fs/'nbwr'/'sub-nbwr999b'/'ses-1'/subject/stc_files[0]), subject=subject)
surfs = dict((hemi, mne.read_surface(op.join(subjects_dir, subject, 'surf', hemi + '.pial'))) for hemi in hemis)
all_vertices = [np.arange(len(surfs[hemi][0])) for hemi in hemis]
fill_mat = mne.compute_morph_matrix(subject, subject, stc.vertices, all_vertices, smooth=10)

# # Give in sparse format
# lh_mat = fill_mat.copy()
# lh_mat.data[fill_mat.indices >= len(stc.vertices[0])] = 0
# lh_mat.eliminate_zeros()
# lh_mat = lh_mat[:len(all_vertices[0])]
# rh_mat = fill_mat.copy()
# rh_mat.data[fill_mat.indices < len(stc.vertices[0])] = 0
# rh_mat.eliminate_zeros()
# rh_mat = rh_mat[len(all_vertices[0]):]
# fname = stc_files[0]
# mne.externals.h5io.write_hdf5('%s_hemi_data.h5' % fname, dict(lh_mat=lh_mat, rh_mat=rh_mat, data=stc.data, times=stc.times), overwrite=True)

stc = stc.morph_precomputed(subject, all_vertices, fill_mat)
template_fname = op.join(subjects_dir, subject, 'mri', 'orig.mgz')
data = list()
times = np.arange(296,297) / 1000.
t = times[0]

t = 0.296
idx = np.abs(stc.times - t).argmin()
for hemi in hemis:
    vol_fname = op.join(subjects_dir, subject, '%s_%s_%d.nii' % (fname, hemi, round(1000 * stc.times[idx], )))
    this_data = getattr(stc, hemi + '_data')[:, idx]
    data_fname = op.join(subjects_dir, subject, '%s.curv' % hemi)
    nib.freesurfer.write_morph_data(data_fname, this_data)
