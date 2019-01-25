#todo: add opts dict option to excliude converting par files with scans matching various strings
from __future__ import division, print_function, absolute_import
from pathlib import *
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
import collections
#js addl imports
from collections import defaultdict
import pandas as pd
from nibabel.mriutils import calculate_dwell_time
from os.path import join
from pylabs.structural.brain_extraction import extract_brain
from pylabs.io.images import savenii
from pylabs.utils import *
prov = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
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
    from pylabs.conversion.brain_convert import is_empty
    verbose.switch = opts.verbose
    if '__missing__' not in dir(scandict):
        raise TypeError('Dictionary not a collections.defaultdict, please fix.')
    subpath = fs / str(opts.proj) / str(opts.subj)
    if 0 in opts.multisession:
        setattr(opts, 'session', '')
        fpath = subpath / 'source_parrec'
        infiles = sortedParGlob(str(fpath / ('*' + opts.scan + '*.PAR')))
    if any(opts.multisession) > 0:
        infiles = []
        for s in opts.multisession:
            ses = 'ses-'+str(s)
            fpath = subpath / ses / 'source_parrec'
            files = ScanReconSort(fpath, '*'+opts.scan+'*.PAR')
            files = filter(lambda x: not ('_dADC_' in x or '_faADC_' in x), [str(y) for y in files])
            files = [Path(x) for x in files]
            if opts.take_lowest_recon:
                # need to account for repeat scans with multiple recons.
                if not is_empty(files):
                    infiles += [files[0]]
            else:
                infiles += files
    for infile in infiles:
        prov.add(str(infile))
        print('working on '+str(infile))
        # load the PAR header and data
        setattr(opts, 'bvals', '')
        setattr(opts, 'bvecs', '')
        setattr(opts, 'run', '')
        setattr(opts, 'outpath', '')
        scaling = 'dv' if opts.scaling == 'off' else opts.scaling
        infile = fname_ext_ul_case(str(infile))
        pr_img = pr.load(infile,
                         permit_truncated=opts.permit_truncated,
                         scaling=scaling,
                         strict_sort=opts.strict_sort)
        pr_hdr = pr_img.header
        affine = pr_hdr.get_affine(origin=opts.origin)
        slope, intercept = pr_hdr.get_data_scaling(scaling)
        setattr(opts, 'parrec_affine', affine)
        setattr(opts, 'fa', int(np.round(np.unique(pr_hdr.image_defs['image_flip_angle']), 0)))
        setattr(opts, 'ti', int(np.round(np.unique(np.round(pr_hdr.image_defs['Inversion delay'])), 0)))
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
            setattr(opts, 'session_id', str(str(infile).split('/')[-3]))
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
        setattr(opts, 'pr_shape', in_data.shape)

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
            in_dataui64 = in_data.astype(np.uint64)
            in_data_rms = np.sqrt(np.mean(np.square(in_dataui64), axis=3))
            rmsimg = nifti1.Nifti1Image(in_data_rms.astype(np.float64), affine)
            rmshdr = rmsimg.header
            rmshdr.set_data_dtype(out_dtype)
            rmshdr.set_slope_inter(slope, intercept)
            rmshdr.set_qform(affine, code=1)
            rmshdr.set_sform(affine, code=1)

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
        basefilename = str(opts.fname_template).format(subj=opts.subj, fa=str(opts.fa).zfill(2),
                            tr=str(opts.tr[0]).replace('.', 'p'), ti=str(opts.ti).zfill(4), run=str(run),
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
        # what is this repeated for from line 199?
        basefilename = str(opts.fname_template).format(subj=opts.subj, fa=str(opts.fa).zfill(2),
                            tr=str(opts.tr[0]).replace('.', 'p'), ti=str(opts.ti).zfill(4), run=str(run),
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
            outpath = fs / opts.proj / opts.subj / opts.session_id / opts.outdir
        else:
            outpath = fs / opts.proj / opts.subj / opts.outdir
        if not outpath.is_dir():
            outpath.mkdir(parents=True)
        outfilename = outpath / basefilename
        if opts.rms:
            rms_outfilename = outpath / rms_basefilename
        if not opts.compressed and str(outfilename).count('.') > 1:
            raise ValueError('more than one . was found in '+str(outfilename)+ '! stopping now.!')
        elif opts.compressed and outfilename.count('.') > 2:
            raise ValueError('more than two . were found in ' + str(outfilename) + '! stopping now.!')
        # prep a file

        if outfilename.is_file() and not opts.overwrite:
            raise IOError('Output file "%s" exists, use \'overwrite\': True to '
                          'overwrite it' % str(outfilename))
        setattr(opts, 'run', run)
        setattr(opts, 'outpath', str(outpath))
        setattr(opts, 'outfilename', str(outfilename))
        setattr(opts, 'basefilename', str(basefilename))
        setattr(opts, 'zooms', pr_hdr.get_zooms())
        # Make corresponding NIfTI image
        nimg = nifti1.Nifti1Image(in_data, affine, pr_hdr)
        nhdr = nimg.header
        nhdr.set_data_dtype(out_dtype)
        nhdr.set_slope_inter(slope, intercept)
        nhdr.set_qform(affine, code=1)
        nhdr.set_sform(affine, code=1)
        nhdr.set_xyzt_units(2, 8)

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
            with open(str(infile), 'rb') as fobj:  # contents must be bytes
                hdr_dump = fobj.read()
                dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
            nhdr.extensions.append(dump_ext)
            if opts.rms:
                rmshdr.extensions.append(dump_ext)
        np.testing.assert_almost_equal(affine, nhdr.get_qform(), 2,
                                       err_msg='output qform in header does not match input qform')
        setattr(opts, 'qform', nhdr.get_qform())
        verbose('Writing %s' % str(outfilename))
        nibabel.save(nimg, str(outfilename))
        prov.log(str(outfilename), 'nifti file created by parrec2nii_convert', str(infile), script=__file__)
        with WorkingContext(str(fs / opts.proj)):
            try:
                if not Path(fs / opts.proj / 'tesla_backups').is_dir():
                    Path(fs / opts.proj / 'tesla_backups').mkdir(parents=True)
                if Path(fs / opts.proj / 'tesla_backups', Path(outfilename).name).is_symlink():
                    Path(fs / opts.proj / 'tesla_backups', Path(outfilename).name).unlink()
                if any(opts.multisession) > 0:
                    Path('tesla_backups', Path(outfilename).name).symlink_to(Path('../' + '/'.join(list(Path(outfilename).parts[-4:]))))
                else:
                    Path('tesla_backups', Path(outfilename).name).symlink_to(Path('../' + '/'.join(list(Path(outfilename).parts[-3:]))))
            except OSError as e:
                if 'File exists' in e:
                    raise ValueError('unable to set backup relative symbolic link for '+infile+' in '+opts.proj+'/tesla_backups/.')

        # write out bvals/bvecs if requested
        if opts.bvs:
            if bvals is None and bvecs is None:
                verbose('No DTI volumes detected, bvals and bvecs not written')
            elif bvecs is None:
                verbose('DTI volumes detected, but no diffusion direction info was'
                        'found.  Writing .bvals file only.')
                with open(str(outfilename).split('.')[0] + '.bvals', 'w') as fid:
                    # np.savetxt could do this, but it's just a loop anyway
                    for val in bvals:
                        fid.write('%s ' % val)
                    fid.write('\n')
            else:
                verbose('Writing .bvals and .bvecs files for '+str(infile))
                # Transform bvecs with reorientation affine
                orig2new = npl.inv(t_aff)
                bv_reorient = from_matvec(to_matvec(orig2new)[0], [0, 0, 0])
                bvecs = apply_affine(bv_reorient, bvecs)
                with open(str(outfilename).split('.')[0] + '.bvals', 'w') as fid:
                    # np.savetxt could do this, but it's just a loop anyway
                    for val in bvals:
                        fid.write('%s ' % val)
                    fid.write('\n')
                prov.log(str(outfilename).split('.')[0] + '.bvals', 'bvalue file created by parrec2nii_convert', str(infile), script=__file__)
                with open(str(outfilename).split('.')[0] + '.bvecs', 'w') as fid:
                    for row in bvecs.T:
                        for val in row:
                            fid.write('%s ' % val)
                        fid.write('\n')
                prov.log(str(outfilename).split('.')[0] + '.bvecs', 'bvectors file created by parrec2nii_convert', str(infile), script=__file__)
                setattr(opts, 'bvals', bvals)
                setattr(opts, 'bvecs', bvecs)
                with WorkingContext(str(fs / opts.proj)):
                    try:
                        if Path(fs / opts.proj / 'tesla_backups', (replacesuffix(outfilename, '.bvecs').name)).is_symlink():
                            Path(fs / opts.proj / 'tesla_backups', (replacesuffix(outfilename, '.bvecs').name)).unlink()
                        if Path(fs / opts.proj / 'tesla_backups', (replacesuffix(outfilename, '.bvals').name)).is_symlink():
                            Path(fs / opts.proj / 'tesla_backups', (replacesuffix(outfilename, '.bvals').name)).unlink()
                        if any(opts.multisession) > 0:
                            Path('tesla_backups', (replacesuffix(outfilename, '.bvecs')).name).symlink_to(Path('../' + '/'.join(list((replacesuffix(outfilename, '.bvecs').parts[-4:])))))
                            Path('tesla_backups', (replacesuffix(outfilename, '.bvals')).name).symlink_to(Path('../' + '/'.join(list((replacesuffix(outfilename, '.bvals').parts[-4:])))))
                        else:
                            Path('tesla_backups', (replacesuffix(outfilename, '.bvecs')).name).symlink_to(Path('../' + '/'.join(list((replacesuffix(outfilename, '.bvecs').parts[-3:])))))
                            Path('tesla_backups', (replacesuffix(outfilename, '.bvals')).name).symlink_to(Path('../' + '/'.join(list((replacesuffix(outfilename, '.bvals').parts[-3:])))))
                    except OSError as e:
                        if 'File exists' in e:
                            raise ValueError('unable to set backup relative symbolic link for '+infile+' in '+opts.proj+'/tesla_backups/')
                    else:
                        print('bvecs backup link created for '+str(outfilename)+' = ' +str(Path('tesla_backups', (replacesuffix(outfilename, '.bvecs')).name).is_symlink()))
                        print('bvals backup link created for '+str(outfilename)+' = ' +str(Path('tesla_backups', (replacesuffix(outfilename, '.bvals')).name).is_symlink()))


        # export data labels varying along the 4th dimensions if requested
        if opts.vol_info:
            labels = pr_img.header.get_volume_labels()
            if len(labels) > 0:
                vol_keys = list(labels.keys())
                with open(str(outfilename).split('.')[0] + '.ordering.csv', 'w') as csvfile:
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
                with open(str(outfilename).split('.')[0] + '.dwell_time', 'w') as fid:
                    fid.write('%r\n' % dwell_time)
                setattr(opts, 'dwell_time', dwell_time)
                prov.log(str(outfilename).split('.')[0] + '.dwell_time', 'dwell time file created by parrec2nii_convert', str(infile), script=__file__)
                with WorkingContext(str(fs / opts.proj)):
                    try:
                        if Path(fs / opts.proj / 'tesla_backups', (replacesuffix(outfilename, '.dwell_time').name)).is_symlink():
                            Path(fs / opts.proj / 'tesla_backups', (replacesuffix(outfilename, '.dwell_time').name)).unlink()
                        if any(opts.multisession) > 0:
                            Path('tesla_backups', (replacesuffix(outfilename, '.dwell_time')).name).symlink_to(Path('../' + '/'.join(list((replacesuffix(outfilename, '.dwell_time').parts[-4:])))))
                        else:
                            Path('tesla_backups', (replacesuffix(outfilename, '.dwell_time')).name).symlink_to(Path('../' + '/'.join(list((replacesuffix(outfilename, '.dwell_time').parts[-3:])))))
                    except OSError as e:
                        if 'File exists' in e:
                            raise ValueError('unable to set dwell time backup relative symbolic link for '+infile+' in '+opts.proj+'/tesla_backups/')
                    else:
                        print('dwell time backup link created for '+str(outfilename)+' = ' +str(Path('tesla_backups', (replacesuffix(outfilename, '.dwell_time')).name).is_symlink()))



        setattr(opts, 'converted', True)
        setattr(opts, 'QC', False)
        setattr(opts, 'pre_proc', False)
        scandict[outerkey][middlekey] = opts2dict(opts)

        #save rms and add new niftiDict data and extract brain
        if opts.rms:
            rms_middlekey = rms_basefilename.split('.')[0]
            scandict[outerkey][rms_middlekey] = opts2dict(opts)
            rms_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            rms_dict[outerkey][rms_middlekey]['outfilename'] = str(rms_outfilename)
            rms_dict[outerkey][rms_middlekey]['basefilename'] = str(rms_basefilename)
            rms_dict[outerkey][rms_middlekey]['qform'] = rmshdr.get_qform()
            rms_dict[outerkey][rms_middlekey]['zooms'] = rmshdr.get_zooms()
            rms_dict[outerkey][rms_middlekey]['b1corr'] = True
            rms_dict[outerkey][rms_middlekey]['orig_data_shape'] = rmsimg.shape
            np.testing.assert_almost_equal(affine, rmshdr.get_qform(), 3,
                                           err_msg='output qform in rms header does not match input qform')
            nibabel.save(rmsimg, str(rms_outfilename))
            rms_brain, rms_mask, rms_cropped = extract_brain(rms_outfilename)
            rms_dict[outerkey][rms_middlekey]['rms_brain'] = rms_brain
            rms_dict[outerkey][rms_middlekey]['rms_mask'] = rms_mask
            rms_dict[outerkey][rms_middlekey]['rms_cropped'] = rms_cropped
            mergeddicts(scandict, rms_dict)
            # prov.log(str(rms_outfilename), 'rms file created by parrec2nii_convert', str(infile), script=__file__, provenance=scandict)
            # prov.log(str(rms_brain), 'brain extracted rms file created by parrec2nii_convert', str(infile), script=__file__, provenance=scandict)
            # prov.log(str(rms_mask), 'mask of extracted rms brain file created by parrec2nii_convert', str(infile), script=__file__, provenance=scandict)

            with WorkingContext(str(fs / opts.proj)):
                try:
                    if Path(fs / opts.proj / 'tesla_backups', Path(rms_outfilename).name).is_symlink():
                        Path(fs / opts.proj / 'tesla_backups', Path(rms_outfilename).name).unlink()
                    if any(opts.multisession) > 0:
                        Path('tesla_backups', Path(rms_outfilename).name).symlink_to(Path('../' + '/'.join(list(Path(rms_outfilename).parts[-4:]))))
                    else:
                        Path('tesla_backups', Path(rms_outfilename).name).symlink_to(Path('../' + '/'.join(list(Path(rms_outfilename).parts[-3:]))))
                except OSError as e:
                    if 'File exists' in e:
                        raise ValueError('unable to set backup relative symbolic link for '+rms_outfilename+' in '+opts.proj+'/tesla_backups/.')
    return scandict
