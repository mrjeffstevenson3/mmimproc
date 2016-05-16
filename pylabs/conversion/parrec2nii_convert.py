#from nibabel parrec2nii
from __future__ import division, print_function, absolute_import

from optparse import OptionParser, Option
import numpy as np
import numpy.linalg as npl
import sys
import os
import csv
import nibabel
import nibabel.parrec as pr
from nibabel.parrec import one_line
from nibabel.mriutils import calculate_dwell_time, MRIError
import nibabel.nifti1 as nifti1
from nibabel.filename_parser import splitext_addext
from nibabel.volumeutils import fname_ext_ul_case
from nibabel.orientations import (io_orientation, inv_ornt_aff,
                                  apply_orientation)
from nibabel.affines import apply_affine, from_matvec, to_matvec

#js addl imports
from collections import defaultdict
import pandas as pd
from nibabel.mriutils import calculate_dwell_time
from os.path import join, isfile
from glob import glob
from pylabs.utils.files import sortedParGlob
from pylabs.utils.paths import getlocaldataroot
import niprov
prov = niprov.Context()
fs = getlocaldataroot()
import dill #to use as pickle replacement of lambda dict

class BrainOpts(object):
    pass

def opts2dict(opts):
    d = {}
    for key in dir(opts):
        value = getattr(opts, key)
        if not key.startswith('__'):
            d[key] = value
    return d

#nib functions to do heavy lifting using opts object to drive processing
def verbose(msg, indent=0):
    if verbose.switch:
        print("%s%s" % (' ' * indent, msg))

def error(msg, exit_code):
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)

def brain_proc_file(opts, scandict):
    verbose.switch = opts.verbose
    if '__missing__' not in dir(scandict):
        raise TypeError('Dictionary not a collections.defaultdict, please fix.')
    subpath = join(fs, opts.proj, opts.subj)
    if opts.multisession[0] == 0:
        setattr(opts, 'session', '')
        fpath = join(subpath, 'source_parrec')
        infiles = sortedParGlob(join(fpath, '*' + opts.scan + '*.PAR'))
    if any(opts.multisession) > 0:
        infiles = []
        for s in opts.multisession:
            ses = 'ses-'+str(s)
            fpath = join(subpath, ses, 'source_parrec')
            infiles += sortedParGlob(join(fpath, '*'+opts.scan+'*.PAR'))
    for infile in infiles:
        prov.add(infile)
        # load the PAR header and data
        setattr(opts, 'bvals', '')
        setattr(opts, 'bvecs', '')
        scaling = 'dv' if opts.scaling == 'off' else opts.scaling
        infile = fname_ext_ul_case(infile)
        pr_img = pr.load(infile,
                         permit_truncated=opts.permit_truncated,
                         scaling=scaling,
                         strict_sort=opts.strict_sort)
        pr_hdr = pr_img.header
        affine = pr_hdr.get_affine(origin=opts.origin)
        slope, intercept = pr_hdr.get_data_scaling(scaling)
        setattr(opts, 'fa', int(pr_hdr.image_defs['image_flip_angle'][0]))
        setattr(opts, 'ti', int(round(pr_hdr.image_defs['Inversion delay'][0])))
        setattr(opts, 'tr', round(pr_hdr.general_info['repetition_time'][0], 1))
        setattr(opts, 'acq_time', pr_hdr.general_info['exam_date'].replace(".","-").replace('/','T').replace(' ', ''))
        if any(opts.multisession) > 0:
            setattr(opts, 'session_id', str(infile.split('/')[-3]))
        else:
            setattr(opts, 'session_id', '')

        if opts.scaling != 'off':
            verbose('Using data scaling "%s"' % opts.scaling)
        # get original scaling, and decide if we scale in-place or not
        if opts.scaling == 'off':
            slope = np.array([1.])
            intercept = np.array([0.])
            in_data = pr_img.dataobj.get_unscaled()
            out_dtype = pr_hdr.get_data_dtype()
        elif not np.any(np.diff(slope)) and not np.any(np.diff(intercept)):
            # Single scalefactor case
            slope = slope.ravel()[0]
            intercept = intercept.ravel()[0]
            in_data = pr_img.dataobj.get_unscaled()
            out_dtype = pr_hdr.get_data_dtype()
        else:
            # Multi scalefactor case
            slope = np.array([1.])
            intercept = np.array([0.])
            in_data = np.array(pr_img.dataobj)
            out_dtype = np.float64
        # Reorient data block to LAS+ if necessary
        ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(affine))
        if np.all(ornt == [[0, 1],
                           [1, 1],
                           [2, 1]]):  # already in LAS+
            t_aff = np.eye(4)
        else:  # Not in LAS+
            t_aff = inv_ornt_aff(ornt, pr_img.shape)
            affine = np.dot(affine, t_aff)
            in_data = apply_orientation(in_data, ornt)

        bvals, bvecs = pr_hdr.get_bvals_bvecs()
        if not opts.keep_trace:  # discard Philips DTI trace if present
            if bvecs is not None:
                bad_mask = np.logical_and(bvals != 0, (bvecs == 0).all(axis=1))
                if bad_mask.sum() > 0:
                    pl = 's' if bad_mask.sum() != 1 else ''
                    verbose('Removing %s DTI trace volume%s'
                            % (bad_mask.sum(), pl))
                    good_mask = ~bad_mask
                    in_data = in_data[..., good_mask]
                    bvals = bvals[good_mask]
                    bvecs = bvecs[good_mask]

        # figure out the output filename, and see if it exists
        run = 1
        basefilename = str(opts.fname_template).format(subj=opts.subj, fa=str(opts.fa),
                            tr=str(opts.tr).replace('.', 'p'), ti=str(opts.ti), run=str(run),
                            session=opts.session_id, scan_name=opts.scan_name, scan_info=opts.scan_info)

        while opts.acq_time in scandict[(opts.subj, opts.session_id, opts.outdir)][basefilename.split('.')[0]]:
            run = run + 1
            basefilename = str(opts.fname_template).format(subj=opts.subj, fa=str(opts.fa),
                                tr=str(opts.tr).replace('.', 'p'), ti=str(opts.ti), run=str(run),
                                session=opts.session_id, scan_name=opts.scan_name, scan_info=opts.scan_info)

        if any(opts.multisession) != 0:
            if not os.path.isdir(os.path.join(fs, opts.proj, opts.subj, opts.session_id, opts.outdir)):
                os.mkdir(os.path.join(fs, opts.proj, opts.subj, opts.session_id, opts.outdir))
            outfilename = os.path.join(fs, opts.proj, opts.subj, opts.session_id, opts.outdir, basefilename)
        else:
            if not os.path.isdir(os.path.join(fs, opts.proj, opts.subj, opts.outdir)):
                os.mkdir(os.path.join(fs, opts.proj, opts.subj, opts.outdir))
            outfilename = os.path.join(fs, opts.proj, opts.subj, opts.outdir, basefilename)
        if outfilename.count('.') > 1:
            raise ValueError('more than one . was found in '+outfilename+ '! stopping now.!')
        # prep a file
        if opts.compressed:
            verbose('Using gzip compression')
            outfilename = outfilename + '.gz'

        if os.path.isfile(outfilename) and not opts.overwrite:
            raise IOError('Output file "%s" exists, use \'overwrite\': True to '
                          'overwrite it' % outfilename)

        setattr(opts, 'outfilename', outfilename)
        setattr(opts, 'basefilename', basefilename.split('.')[0])
        # Make corresponding NIfTI image
        nimg = nifti1.Nifti1Image(in_data, affine, pr_hdr)
        nhdr = nimg.header
        nhdr.set_data_dtype(out_dtype)
        nhdr.set_slope_inter(slope, intercept)

        if 'parse' in opts.minmax:
            # need to get the scaled data
            verbose('Loading (and scaling) the data to determine value range')
        if opts.minmax[0] == 'parse':
            nhdr['cal_min'] = in_data.min() * slope + intercept
        else:
            nhdr['cal_min'] = float(opts.minmax[0])
        if opts.minmax[1] == 'parse':
            nhdr['cal_max'] = in_data.max() * slope + intercept
        else:
            nhdr['cal_max'] = float(opts.minmax[1])

        # container for potential NIfTI1 header extensions
        if opts.store_header:
            # dump the full PAR header content into an extension
            with open(infile, 'rb') as fobj:  # contents must be bytes
                hdr_dump = fobj.read()
                dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
            nhdr.extensions.append(dump_ext)

        verbose('Writing %s' % outfilename)
        #verbose('session id=%s' % opts.session_id)
        nibabel.save(nimg, outfilename)

        # write out bvals/bvecs if requested
        if opts.bvs:
            if bvals is None and bvecs is None:
                verbose('No DTI volumes detected, bvals and bvecs not written')
            elif bvecs is None:
                verbose('DTI volumes detected, but no diffusion direction info was'
                        'found.  Writing .bvals file only.')
                with open(outfilename.split('.')[0] + '.bvals', 'w') as fid:
                    # np.savetxt could do this, but it's just a loop anyway
                    for val in bvals:
                        fid.write('%s ' % val)
                    fid.write('\n')
            else:
                verbose('Writing .bvals and .bvecs files')
                # Transform bvecs with reorientation affine
                orig2new = npl.inv(t_aff)
                bv_reorient = from_matvec(to_matvec(orig2new)[0], [0, 0, 0])
                bvecs = apply_affine(bv_reorient, bvecs)
                with open(outfilename.split('.')[0] + '.bvals', 'w') as fid:
                    # np.savetxt could do this, but it's just a loop anyway
                    for val in bvals:
                        fid.write('%s ' % val)
                    fid.write('\n')
                with open(outfilename.split('.')[0] + '.bvecs', 'w') as fid:
                    for row in bvecs.T:
                        for val in row:
                            fid.write('%s ' % val)
                        fid.write('\n')
                setattr(opts, 'bvals', bvals)
                setattr(opts, 'bvecs', bvecs)

        # export data labels varying along the 4th dimensions if requested
        if opts.vol_info:
            labels = pr_img.header.get_volume_labels()
            if len(labels) > 0:
                vol_keys = list(labels.keys())
                with open(outfilename.split('.')[0] + '.ordering.csv', 'w') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=',')
                    csvwriter.writerow(vol_keys)
                    for vals in zip(*[labels[k] for k in vol_keys]):
                        csvwriter.writerow(vals)

        # write out dwell time if requested
        if opts.dwell_time:
            try:
                dwell_time = calculate_dwell_time(
                    pr_hdr.get_water_fat_shift(),
                    pr_hdr.get_echo_train_length(),
                    opts.field_strength)
            except MRIError:
                verbose('No EPI factors, dwell time not written')
            else:
                verbose('Writing dwell time (%r sec) calculated assuming %sT '
                        'magnet' % (dwell_time, opts.field_strength))
                with open(outfilename.split('.')[0] + '.dwell_time', 'w') as fid:
                    fid.write('%r\n' % dwell_time)
                setattr(opts, 'dwell_time', dwell_time)

        setattr(opts, 'converted', True)
        setattr(opts, 'QC', False)
        setattr(opts, 'pre_proc', False)
        scandict[(opts.subj, opts.session_id, opts.outdir)][basefilename.split('.')[0]] = opts2dict(opts)

    #need to make dataframe from opts and save as tsv
    #need to make k v pairs for scandict to pass back

    return scandict
        # done

