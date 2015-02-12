# -*- coding: utf-8 -*-

import os
from os import path as op


import glob
import nibabel  # noqa
import niprov

from pylabs.utils import InTempDir

work_dir = ('/media/DiskArray/shared_data/js/self_control/'
            'hbm_group_data/qT1')
niprov.discover(work_dir)


# XXX This should be populated using an argument for subject names
subdirs = [op.join(work_dir, name) for name in os.listdir(work_dir)
           if os.path.isdir(os.path.join(work_dir, name))]
for subdir in subdirs:
    subj_name = op.split(subdir)[-1]
    # XXX these globs should be replaced by hard-coding the names
    # (with variable substitution), since we should settle on a convention
    t1_ref = glob.glob(op.join(subdir, '*T1_MAP_02B*.PAR'))
    t1_10 = glob.glob(op.join(subdir, '*T1_MAP_02B*.PAR'))
    t1_20 = glob.glob(op.join(subdir, '*T1_MAP_02B*.PAR'))
    b1_map = glob.glob(op.join(work_dir, subdir, '*B1MAP_SAG*.PAR'))
    out_names = [t1_ref, t1_10, t1_20, b1_map]
    for ni, name in enumerate(out_names):
        if len(name) != 1:
            raise IOError('should find exactly one name, found %s' % len(name))
        out_names[ni] = name[0][:-3] + '.nii'

    # convert from PAR/REC to NIfTI
    scalings = ['fp', 'fp', 'fp', 'dv']
    for out_name, scaling in zip(out_names, scalings):
        in_name = out_name[:-3] + '.PAR'
        cmd = 'nibabel.load(in_name, scaling=scaling).save(out_name)'
        exec(cmd)
        niprov.log(cmd, parent=in_name, new=out_name)

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

        niprov.record('fslhd -x %s > t1ref_temphdr.txt' % t1_ref)
        niprov.record('fslmerge -t t1flip_all_orig1 %s %s %s'
                      % (t1_ref, t1_10, t1_20))
        niprov.record('fslmaths t1flip_all_orig1 -mul 1 t1flip_all_orig '
                      '-odt float')
        niprov.record('bet %s %s_brain -m' % (t1_ref, t1_ref))
        niprov.record('fslroi %s b1map_mag 0 1' % b1_map)
        niprov.record('fslroi %s b1map_phase 2 1' % b1_map)
        niprov.record('mcflirt -in t1flip_all_orig -out t1all_reg -mats '
                      '-plots -refvol 0 -rmsrel -rmsabs')
        niprov.record('flirt -in b1map_mag -ref %s -init identity.mat '
                      '-o b1map_mag_upsample -omat b1mag2t1ref.mat'
                      % t1_ref)
        niprov.record('flirt -in b1map_phase -ref %s -applyxfm '
                      '-init b1mag2t1ref.mat -out b1map_phase_reg2t1map'
                      % t1_ref)
        niprov.record('fslmaths b1map_phase_reg2t1map -s 5 '
                      '-mas %s_brain_mask b1map_phase_reg2t1map_s5_masked '
                      '-odt float' % t1_ref)
        niprov.record('fslchfiletype ANALYZE t1all_reg t1flip_all.hdr')
        niprov.record('fslchfiletype ANALYZE '
                      'b1map_phase_reg2t1map_s5_masked out_image.hdr')
        # XXX hard-coded executable :(
        niprov.record('/home/toddr/Software/'
                      't1flip_with3_with3differentoutputs')
        niprov.record('fslchfiletype NIFTI t1image_b1corr %s' % qT1)
        niprov.record('fslchfiletype NIFTI t1flip_all_b1corr %s'
                      % all_t1flips_b1corr)
        niprov.record('fslchfiletype NIFTI t1image_uncorr %s' % qT1_nob1corr)
        niprov.record('fslchfiletype NIFTI t1image_intensitycorr %s'
                      % qT1_intensitycorr)
        for fname in (qT1, all_t1flips_b1corr, qT1_nob1corr,
                      qT1_intensitycorr):
            niprov.record('fslcreatehd t1ref_temphdr.txt %s' % fname)

    qT1_thr = op.join(subdir, subj_name + '_qT1_thr8000_ero')
    niprov.record('fslmaths %s -thr 1 -uthr 8000 -ero %s'
                  % (qT1, qT1_thr))
