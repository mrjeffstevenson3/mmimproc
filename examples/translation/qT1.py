# -*- coding: utf-8 -*-

import os
from os import path as op


import glob
import niprov

from mmimproc.utils import InTempDir
from mmimproc.conversion import par_to_nii, dump_header

work_dir = os.getcwd()  # must have e.g. scs385 subdirectory here
niprov.discover(work_dir)


# XXX This should be populated using an argument for subject names
subdirs = [op.join(work_dir, name) for name in os.listdir(work_dir)
           if os.path.isdir(os.path.join(work_dir, name))]
for subdir in subdirs:
    subj_name = op.split(subdir)[-1]
    # XXX these globs should be replaced by hard-coding the names
    # (with variable substitution), since we should settle on a convention
    t1_ref = glob.glob(op.join(subdir, '*T1_MAP_02B*.PAR'))
    assert len(t1_ref) == 1
    t1_ref = t1_ref[0][:-3] + 'nii'
    t1_10 = glob.glob(op.join(subdir, '*T1_MAP_02B*.PAR'))
    assert len(t1_10) == 1
    t1_10 = t1_10[0][:-3] + 'nii'
    t1_20 = glob.glob(op.join(subdir, '*T1_MAP_02B*.PAR'))
    assert len(t1_20) == 1
    t1_20 = t1_20[0][:-3] + 'nii'
    b1_map = glob.glob(op.join(work_dir, subdir, '*B1MAP_SAG*.PAR'))
    assert len(b1_map) == 1
    b1_map = b1_map[0][:-3] + 'nii'

    # convert from PAR/REC to NIfTI
    scalings = ['fp', 'fp', 'fp', 'dv']
    for out_name, scaling in zip([t1_ref, t1_10, t1_20, b1_map], scalings):
        in_name = out_name[:-3] + 'PAR'
        niprov.record(par_to_nii, args=[in_name, out_name, scaling],
                      parents=[in_name], new=out_name)

    print('B1 map file name is %s and T1 reference file name is %s'
          % (b1_map, t1_ref))

    # These are what the final output files will be named
    qT1 = op.join(subdir, subj_name + '_qT1.nii')
    all_t1flips_b1corr = op.join(subdir,
                                 subj_name + '_all_t1flips_b1corr.nii')
    qT1_nob1corr = op.join(subdir, subj_name + '_qT1_nob1corr.nii')
    qT1_intensitycorr = op.join(subdir,
                                subj_name + '_qT1_intensitycorr.nii')

    # Work in a temporary directory so that all temporary files will get
    # automatically removed
    with InTempDir():
        with open('identity.mat', 'w') as fid:
            fid.write('1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n')
        niprov.add('identity.mat', transient=True)

        niprov.record(dump_header, args=(t1_ref, 't1ref_temphdr.txt'),
                      parents=t1_ref, new='t1ref_temphdr.txt', transient=True)
        parents = (t1_ref, t1_10, t1_20)
        niprov.record('fslmerge -t t1flip_all_orig1 %s %s %s'
                      % parents, new='t1flip_all_orig1', parents=parents,
                      transient=True)
        niprov.record('fslmaths t1flip_all_orig1 -mul 1 t1flip_all_orig '
                      '-odt float', new='t1flip_all_orig',
                      parents='t1flip_all_orig1', transient=True)
        niprov.record('bet %s %s_brain -m' % (t1_ref, t1_ref),
                      parents=t1_ref, transient=True,
                      new=[t1_ref + '_brain', t1_ref + '_brain_mask'])
        niprov.record('fslroi %s b1map_mag 0 1' % b1_map, new='b1map_mag',
                      parents=b1_map, transient=True)
        niprov.record('fslroi %s b1map_phase 2 1' % b1_map, new='b1map_phase',
                      parents=b1_map, transient=True)
        niprov.record('mcflirt -in t1flip_all_orig -out t1all_reg -mats '
                      '-plots -refvol 0 -rmsrel -rmsabs', new='t1all_reg',
                      parents='t1flip_all_orig', transient=True)
        niprov.record('flirt -in b1map_mag -ref %s -init identity.mat '
                      '-o b1map_mag_upsample -omat b1mag2t1ref.mat'
                      % t1_ref, new=['b1map_mag_upsample', 'b1mag2t1ref.mat'],
                      parents=['b1map_mag', t1_ref, 'identity.mat'],
                      transient=True)
        niprov.record('flirt -in b1map_phase -ref %s -applyxfm '
                      '-init b1mag2t1ref.mat -out b1map_phase_reg2t1map'
                      % t1_ref, new='b1map_phase_reg2t1map',
                      parents=['b1map_phase', t1_ref, 'b1mag2t1ref.mat'],
                      transient=True)
        niprov.record('fslmaths b1map_phase_reg2t1map -s 5 '
                      '-mas %s_brain_mask b1map_phase_reg2t1map_s5_masked '
                      '-odt float' % t1_ref,
                      new='b1map_phase_reg2t1map_s5_masked',
                      parents=[t1_ref + '_brain_mask',
                               'b1map_phase_reg2t1map'], transient=True)
        niprov.record('fslchfiletype ANALYZE t1all_reg t1flip_all.hdr',
                      new='t1flip_all', parents='t1all_reg', transient=True)
        niprov.record('fslchfiletype ANALYZE '
                      'b1map_phase_reg2t1map_s5_masked out_image.hdr',
                      new='out_image.hdr',
                      parents='b1map_phase_reg2t1map_s5_masked',
                      transient=True)
        niprov.record(op.join(work_dir, 't1flip_with3_with3differentoutputs'),
                      new=['t1image_b1corr', 't1image_intensitycorr',
                           't1image_uncorr',
                           's0image_b1corr', 's0image_intensitycorr',
                           's0image_uncorr',
                           't1flip_all_b1corr'],
                      parents=['t1flip_all', 'out_image'],
                      transient=True)
        niprov.record('fslchfiletype NIFTI t1image_b1corr %s' % qT1,
                      new=qT1, parents='t1image_b1corr')
        niprov.record('fslchfiletype NIFTI t1flip_all_b1corr %s'
                      % all_t1flips_b1corr, new=all_t1flips_b1corr,
                      parents='t1flip_all_b1corr')
        niprov.record('fslchfiletype NIFTI t1image_intensitycorr %s'
                      % qT1_intensitycorr, new=qT1_intensitycorr,
                      parents='t1image_intensitycorr')
        niprov.record('fslchfiletype NIFTI t1image_uncorr %s' % qT1_nob1corr,
                      new=qT1_nob1corr, parents='t1image_uncorr')
        for fname in (qT1, all_t1flips_b1corr, qT1_nob1corr,
                      qT1_intensitycorr):
            niprov.record('fslcreatehd t1ref_temphdr.txt %s' % fname,
                          parents=[fname, 't1ref_temphdr.txt'], new=fname)

    qT1_thr = op.join(subdir, subj_name + '_qT1_thr8000_ero.nii.gz')
    niprov.record('fslmaths %s -thr 1 -uthr 8000 -ero %s'
                  % (qT1, qT1_thr), parents=qT1, new=qT1_thr)
