import os
import os.path as op

import numpy as np
import nibabel as nib
import mne

hemis = ['lh', 'rh']
step = 25  # in ms

subjects_dir = mne.get_config('SUBJECTS_DIR')
subjects_dir += '/bbc/reg/ants_vbm_pairedLH_in_template_space'
mne.set_config('SUBJECTS_DIR', subjects_dir)

subject = 'template_hires_br_freesurf_v6'
if not op.isdir('temp'):
    os.mkdir('temp')
for fname in ('Control-Foster_word1', 'tstat_group_contrast_word1'):
    print('Reading %s...' % fname)
    stc = mne.read_source_estimate(fname, subject=subject)

    print('  Morphing...')  # to fill all vertices
    surfs = dict((hemi, mne.read_surface(op.join(subjects_dir, subject, 'surf',
                                         hemi + '.white'))) for hemi in hemis)
    all_vertices = [np.arange(len(surfs[hemi][0])) for hemi in hemis]
    fill_mat = mne.compute_morph_matrix(subject, subject, stc.vertices,
                                        all_vertices, smooth=10)
    # Give in sparse format
    lh_mat = fill_mat.copy()
    lh_mat.data[fill_mat.indices >= len(stc.vertices[0])] = 0
    lh_mat.eliminate_zeros()
    lh_mat = lh_mat[:len(all_vertices[0])]
    rh_mat = fill_mat.copy()
    rh_mat.data[fill_mat.indices < len(stc.vertices[0])] = 0
    rh_mat.eliminate_zeros()
    rh_mat = rh_mat[len(all_vertices[0]):]
    mne.externals.h5io.write_hdf5('%s_hemi_data.h5' % fname,
                                  dict(lh_mat=lh_mat, rh_mat=rh_mat,
                                       data=stc.data, times=stc.times),
                                  overwrite=True)

    stc = stc.morph_precomputed(subject, all_vertices, fill_mat)

    print('  Converting to volume...')
    template_fname = op.join(subjects_dir, subject, 'mri', 'orig.mgz')
    work_dir = 'temp'
    data = list()
    times = np.arange(-100, 501, step) / 1000.
    for t in times:
        idx = np.abs(stc.times - t).argmin()
        print('    t=%s' % (stc.times[idx],))
        for hemi in hemis:
            vol_fname = op.join(work_dir, '%s_%s_%d.nii'
                                % (fname, hemi, round(1000 * stc.times[idx],)))
            if not op.isfile(vol_fname):
                # Write to disk
                this_data = getattr(stc, hemi + '_data')[:, idx]
                data_fname = op.join(work_dir, '%s.curv' % hemi)
                nib.freesurfer.write_morph_data(data_fname, this_data)
                # Run FreeSurfer algorithm
                mne.utils.run_subprocess([
                    'mri_surf2vol', '--surf', 'white', '--surfval', data_fname,
                    '--hemi', hemi, '--template', template_fname,
                    '--volregidentity', subject, '--outvol', vol_fname])
            if hemi == 'lh':
                vol = nib.load(vol_fname)
            else:
                data.append(vol.get_data())
                data[-1] += nib.load(vol_fname).get_data()

    print('  Writing to disk...')
    data = np.array(data).transpose([1, 2, 3, 0])
    vol = nib.nifti1.Nifti1Image(data, vol.affine, vol.header)
    nib.save(vol, '%s.nii' % fname)
print('Done.')