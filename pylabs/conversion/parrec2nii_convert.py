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
import collections
from collections import defaultdict
import pandas as pd
from nibabel.mriutils import calculate_dwell_time
from os.path import join, isfile
from glob import glob
from pylabs.utils.files import sortedParGlob
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
from pylabs.utils import pr_examdate2pydatetime, pr_examdate2BIDSdatetime
import niprov
prov = niprov.ProvenanceContext()
fs = getnetworkdataroot()
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

def mergeddicts(origdict, appenddict):
    if not isinstance(origdict, collections.Mapping) or not isinstance(appenddict, collections.Mapping):
        raise TypeError('One dictionary not a nested 3 level collections.defaultdict(list), please fix.')
    for k, v in appenddict.iteritems():
        if isinstance(origdict, collections.Mapping):
            if isinstance(v, collections.Mapping):
                r = mergeddicts(origdict.get(k, {}), v)
                origdict[k] = r
            else:
                origdict[k] = appenddict[k]
        else:
            origdict = {k: appenddict[k]}
    return origdict

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
        setattr(opts, 'run', '')
        setattr(opts, 'outpath', '')
        scaling = 'dv' if opts.scaling == 'off' else opts.scaling
        infile = fname_ext_ul_case(infile)
        pr_img = pr.load(infile,
                         permit_truncated=opts.permit_truncated,
                         scaling=scaling,
                         strict_sort=opts.strict_sort)
        pr_hdr = pr_img.header
        affine = pr_hdr.get_affine(origin=opts.origin)
        slope, intercept = pr_hdr.get_data_scaling(scaling)
        setattr(opts, 'fa', np.unique(pr_hdr.image_defs['image_flip_angle']))
        setattr(opts, 'ti', np.unique(np.round(pr_hdr.image_defs['Inversion delay'])))
        setattr(opts, 'tr', np.round(np.unique(pr_hdr.general_info['repetition_time']), 1))
        setattr(opts, 'exam_date', pr_examdate2pydatetime(pr_hdr.general_info['exam_date']))
        setattr(opts, 'acq_time', pr_examdate2BIDSdatetime(pr_hdr.general_info['exam_date']))
        setattr(opts, 'resolution', np.int(np.max(pr_hdr.image_defs['recon resolution'])))
        setattr(opts, 'fov', pr_hdr.general_info['fov'])
        setattr(opts, 'vols', np.int(np.max(pr_hdr.image_defs['dynamic scan number'])))
        setattr(opts, 'slices', np.int(np.max(pr_hdr.image_defs['slice number'])))
        setattr(opts, 'slice_thickness', np.unique(pr_hdr.image_defs['slice thickness']))
        setattr(opts, 'slice_gap', np.unique(pr_hdr.image_defs['slice gap']))
        setattr(opts, 'angulation', pr_hdr.general_info['angulation'])
        setattr(opts, 'off_center', pr_hdr.general_info['off_center'])
        setattr(opts, 'slope', slope)
        setattr(opts, 'intercept', intercept)
        setattr(opts, 'patient_name', pr_hdr.general_info['patient_name'])
        setattr(opts, 'exam_name', pr_hdr.general_info['exam_name'])
        setattr(opts, 'protocol_name', pr_hdr.general_info['protocol_name'])
        setattr(opts, 'acq_nr', pr_hdr.general_info['acq_nr'])
        setattr(opts, 'recon_nr', pr_hdr.general_info['recon_nr'])
        setattr(opts, 'max_echoes', pr_hdr.general_info['max_echoes'])
        setattr(opts, 'max_slices', pr_hdr.general_info['max_slices'])
        setattr(opts, 'tech', pr_hdr.general_info['tech'])
        setattr(opts, 'epi_factor', pr_hdr.general_info['epi_factor'])
        setattr(opts, 'max_diffusion_values', pr_hdr.general_info['max_diffusion_values'])
        setattr(opts, 'max_gradient_orient', pr_hdr.general_info['max_gradient_orient'])
        setattr(opts, 'diffusion_b_factor', pr_hdr.image_defs['diffusion_b_factor'])
        setattr(opts, 'diffusion_b_value_number', pr_hdr.image_defs['diffusion b value number'])
        setattr(opts, 'gradient_orientation_number', pr_hdr.image_defs['gradient orientation number'])
        setattr(opts, 'num_echos', np.unique(pr_hdr.image_defs['echo number']))
        setattr(opts, 'echo_time', np.unique(pr_hdr.image_defs['echo_time']))
        setattr(opts, 'image_type_mr', np.unique(pr_hdr.image_defs['image_type_mr']))
        setattr(opts, 'scanning_sequence', np.unique(pr_hdr.image_defs['scanning sequence']))
        setattr(opts, 'image_pixel_size', pr_hdr.image_defs['image pixel size'])
        setattr(opts, 'pixel_spacing', pr_hdr.image_defs['pixel spacing'])
        setattr(opts, 'recon_resolution', np.unique(pr_hdr.image_defs['recon resolution']))
        setattr(opts, 'TURBO_factor', np.unique(pr_hdr.image_defs['TURBO factor']))

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
            out_dtype = np.float32
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
        setattr(opts, 'orig_affine', affine)
        setattr(opts, 'orig_data_shape', in_data.shape)
        #make rms if asked
        if opts.rms and len(in_data.shape) == 4:
            in_data_rms = np.sqrt(np.sum(np.square(in_data), axis=3)/in_data.shape[3])
            rmsimg = nifti1.Nifti1Image(in_data_rms, affine, pr_hdr)
            rmshdr = rmsimg.header
            rmshdr.set_data_dtype(out_dtype)
            rmshdr.set_slope_inter(slope, intercept)
            rmshdr.set_qform(affine, code=2)

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
        basefilename = str(opts.fname_template).format(subj=opts.subj, fa=str(int(opts.fa[0])).zfill(2),
                            tr=str(opts.tr[0]).replace('.', 'p'), ti=str(opts.ti[0]).zfill(4), run=str(run),
                            session=opts.session_id, scan_name=opts.scan_name, scan_info=opts.scan_info)
        outerkey = (opts.subj, opts.session_id, opts.outdir)
        middlekey = basefilename.split('.')[0]
        if not scandict[outerkey].has_key(middlekey):
            #case 1: no dict key found, not in dict - eg 1st instance of exam and/or scan
            run = 1
        elif scandict.has_key(outerkey):
            #exam known
            if scandict[outerkey].has_key(middlekey):
                #exam and scan known. need to ascertain run number
                while scandict[outerkey].has_key(middlekey[:-1]+str(run)) and \
                        scandict[outerkey][middlekey[:-1]+str(run)]['exam_date'] == opts.exam_date:
                    run += 1

        basefilename = str(opts.fname_template).format(subj=opts.subj, fa=str(int(opts.fa[0])).zfill(2),
                            tr=str(opts.tr[0]).replace('.', 'p'), ti=str(opts.ti[0]).zfill(4), run=str(run),
                            session=opts.session_id, scan_name=opts.scan_name, scan_info=opts.scan_info)
        middlekey = basefilename.split('.')[0]
        if opts.rms:
            rms_basefilename = basefilename.split('.')[0][:-1] + 'rms_' + str(run) + '.nii'

        if opts.compressed:
            verbose('Using gzip compression')
            basefilename = basefilename + '.gz'
            if opts.rms:
                rms_basefilename = rms_basefilename + '.gz'
        #set path for output
        if any(opts.multisession) != 0:
            outpath = join(fs, opts.proj, opts.subj, opts.session_id, opts.outdir)
        else:
            outpath = join(fs, opts.proj, opts.subj, opts.outdir)
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        outfilename = os.path.join(outpath, basefilename)
        if opts.rms:
            rms_outfilename = os.path.join(outpath, rms_basefilename)
        if not opts.compressed and outfilename.count('.') > 1:
            raise ValueError('more than one . was found in '+outfilename+ '! stopping now.!')
        elif opts.compressed and outfilename.count('.') > 2:
            raise ValueError('more than two . were found in ' + outfilename + '! stopping now.!')
        # prep a file

        if os.path.isfile(outfilename) and not opts.overwrite:
            raise IOError('Output file "%s" exists, use \'overwrite\': True to '
                          'overwrite it' % outfilename)
        setattr(opts, 'run', run)
        setattr(opts, 'outpath', outpath)
        setattr(opts, 'outfilename', outfilename)
        setattr(opts, 'basefilename', basefilename)
        # Make corresponding NIfTI image
        nimg = nifti1.Nifti1Image(in_data, affine, pr_hdr)
        nhdr = nimg.header
        nhdr.set_data_dtype(out_dtype)
        nhdr.set_slope_inter(slope, intercept)
        nhdr.set_qform(affine, code=2)

        if 'parse' in opts.minmax:
            # need to get the scaled data
            verbose('Loading (and scaling) the data to determine value range')
        if opts.minmax[0] == 'parse':
            nhdr['cal_min'] = in_data.min() * slope + intercept
            if opts.rms:
                rmshdr['cal_min'] = in_data_rms.min() * slope + intercept
        else:
            nhdr['cal_min'] = float(opts.minmax[0])
            if opts.rms:
                rmshdr['cal_min'] = float(opts.minmax[0])
        if opts.minmax[1] == 'parse':
            nhdr['cal_max'] = in_data.max() * slope + intercept
            if opts.rms:
                rmshdr['cal_max'] = in_data_rms.max() * slope + intercept
        else:
            nhdr['cal_max'] = float(opts.minmax[1])
            if opts.rms:
                rmshdr['cal_max'] = float(opts.minmax[1])

        # container for potential NIfTI1 header extensions
        if opts.store_header:
            # dump the full PAR header content into an extension
            with open(infile, 'rb') as fobj:  # contents must be bytes
                hdr_dump = fobj.read()
                dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
            nhdr.extensions.append(dump_ext)
            if opts.rms:
                rmshdr.extensions.append(dump_ext)
        np.testing.assert_almost_equal(affine, nhdr.get_qform(), 4,
                                       err_msg='output qform in header does not match input qform')
        setattr(opts, 'qform', nhdr.get_qform())
        verbose('Writing %s' % outfilename)
        nibabel.save(nimg, outfilename)
        prov.log(outfilename, 'nifti file created by parrec2nii_convert', infile, script=__file__)

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
                prov.log(outfilename.split('.')[0] + '.bvals', 'bvalue file created by parrec2nii_convert', infile, script=__file__)
                with open(outfilename.split('.')[0] + '.bvecs', 'w') as fid:
                    for row in bvecs.T:
                        for val in row:
                            fid.write('%s ' % val)
                        fid.write('\n')
                prov.log(outfilename.split('.')[0] + '.bvecs', 'bvectors file created by parrec2nii_convert', infile, script=__file__)
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
                prov.log(outfilename.split('.')[0] + '.dwell_time', 'dwell time file created by parrec2nii_convert', infile, script=__file__)

        setattr(opts, 'converted', True)
        setattr(opts, 'QC', False)
        setattr(opts, 'pre_proc', False)
        scandict[outerkey][middlekey] = opts2dict(opts)

        #save rms and add new niftiDict data
        if opts.rms:
            rms_middlekey = rms_basefilename.split('.')[0]
            scandict[outerkey][rms_middlekey] = opts2dict(opts)
            rms_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            rms_dict[outerkey][rms_middlekey]['outfilename'] = rms_outfilename
            rms_dict[outerkey][rms_middlekey]['basefilename'] = rms_basefilename
            rms_dict[outerkey][rms_middlekey]['qform'] = rmshdr.get_qform()
            rms_dict[outerkey][rms_middlekey]['b1corr'] = True
            rms_dict[outerkey][rms_middlekey]['orig_data_shape'] = rmsimg.shape
            mergeddicts(scandict, rms_dict)
            np.testing.assert_almost_equal(affine, rmshdr.get_qform(), 4,
                                           err_msg='output qform in rms header does not match input qform')
            nibabel.save(rmsimg, rms_outfilename)
            prov.log(rms_outfilename, 'rms file created by parrec2nii_convert', infile, script=__file__)
    return scandict
