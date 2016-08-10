# -*- coding: utf-8 -*-


import numpy as np
import numpy.linalg as npl
import sys
import os
import nibabel
import nibabel.parrec as pr
from nibabel.mriutils import calculate_dwell_time, MRIError
import nibabel.nifti1 as nifti1
from nibabel.filename_parser import splitext_addext
from nibabel.volumeutils import fname_ext_ul_case
from nibabel.orientations import (io_orientation, inv_ornt_aff,
                                  apply_orientation)
from nibabel.affines import apply_affine, from_matvec, to_matvec
import scipy.ndimage

# from six import string_types


# def par_to_nii(in_file, out_file, scaling='fp'):
#     """Load a PAR/REC file, scale it, and save the data (usually as NIfTI)
#
#     Parameters
#     ----------
#     in_file : str
#         Input filename.
#     out_file : str.
#         Output filename. Should have a ``.nii`` or ``.nii.gz`` to save
#         in NIfTI format.
#     scaling : str
#         Scaling to use. See nibabel's parrec2nii for options.
#     """
#     if not isinstance(in_file, string_types):
#         raise TypeError('in_file must be a str')
#     if op.splitext(in_file)[1].lower() != '.par':
#         raise RuntimeError('Input must be a .par file')
#     nibabel.save(nibabel.load(in_file, scaling=scaling), out_file)

def error(msg, exit_code):
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)
#defaults
verbose = False

def printmessage(msg, indent=0):
    if verbose:
        print("%s%s" % (' ' * indent, msg))

def par_to_nii(infile, verbose=True, outdir=None, compressed=False, overwrite=True, permit_truncated=True,
               store_header=True, bvs=False, dwell_time=False, field_strength='3.0',
               scaling='dv', minmax=('parse', 'parse'), origin='scanner', outfilename=None):
    # figure out the output filename, and see if it exists
    basefilename = splitext_addext(os.path.basename(infile))[0]
    if outdir is not None and outfilename is not None:
        # prep a file
        if compressed:
            printmessage('Using gzip compression')
            outfilename = os.path.join(outdir, outfilename + '.nii.gz' )
        else:
             outfilename = os.path.join(outdir, outfilename + '.nii' )
        if os.path.isfile(outfilename) and not overwrite:
            raise IOError('Output file "%s" exists, use --overwrite to '
                          'overwrite it' % outfilename)

    if outdir is not None and outfilename is None:
        # set output path
        basefilename = os.path.join(outdir, basefilename)
        # prep a file
        if compressed:
            printmessage('Using gzip compression')
            outfilename =  basefilename + '.nii.gz'
        else:
             outfilename = basefilename + '.nii'
        if os.path.isfile(outfilename) and not overwrite:
            raise IOError('Output file "%s" exists, use --overwrite to '
                          'overwrite it' % outfilename)
    if outdir is None and outfilename is not None:
        # prep a file
        if compressed:
            printmessage('Using gzip compression')
            outfilename = os.path.join(outdir, outfilename + '.nii.gz' )
        else:
             outfilename = os.path.join(outdir, outfilename + '.nii' )
        if os.path.isfile(outfilename) and not overwrite:
            raise IOError('Output file "%s" exists, use --overwrite to '
                          'overwrite it' % outfilename)


    # load the PAR header and data
    scaling = 'dv' if scaling == 'off' else scaling
    infile = fname_ext_ul_case(infile)
    pr_img = pr.load(infile,
                     permit_truncated=permit_truncated,
                     scaling=scaling)
    pr_hdr = pr_img.header
    affine = pr_hdr.get_affine(origin=origin)
    slope, intercept = pr_hdr.get_data_scaling(scaling)
    if scaling != 'off':
        printmessage('Using data scaling "%s"' % scaling)
    # get original scaling, and decide if we scale in-place or not
    if scaling == 'off':
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
                       [2, 1]]): # already in LAS+
        t_aff = np.eye(4)
    else: # Not in LAS+
        t_aff = inv_ornt_aff(ornt, pr_img.shape)
        affine = np.dot(affine, t_aff)
        in_data = apply_orientation(in_data, ornt)
    # Make corresponding NIfTI image
    nimg = nifti1.Nifti1Image(in_data, affine, pr_hdr)
    nhdr = nimg.header
    nhdr.set_data_dtype(out_dtype)
    nhdr.set_slope_inter(slope, intercept)
    nhdr.set_qform(affine, code=2)
    np.testing.assert_almost_equal(affine, nhdr.get_qform(), 4,
                                   err_msg='output qform in header does not match input qform')

    if 'parse' in minmax:
        # need to get the scaled data
        printmessage('Loading (and scaling) the data to determine value range')
    if minmax[0] == 'parse':
        nhdr['cal_min'] = in_data.min() * slope + intercept
    else:
        nhdr['cal_min'] = float(minmax[0])
    if minmax[1] == 'parse':
        nhdr['cal_max'] = in_data.max() * slope + intercept
    else:
        nhdr['cal_max'] = float(minmax[1])

    # container for potential NIfTI1 header extensions
    if store_header:
        # dump the full PAR header content into an extension
        with open(infile, 'r') as fobj:
            hdr_dump = fobj.read()
            dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
        nhdr.extensions.append(dump_ext)

    printmessage('Writing %s' % outfilename)
    nibabel.save(nimg, outfilename)

    # write out bvals/bvecs if requested
    if bvs:
        bvals, bvecs = pr_hdr.get_bvals_bvecs()
        if bvals is None and bvecs is None:
            printmessage('No DTI volumes detected, bvals and bvecs not written')
        else:
            printmessage('Writing .bvals and .bvecs files')
            # Transform bvecs with reorientation affine
            orig2new = npl.inv(t_aff)
            bv_reorient = from_matvec(to_matvec(orig2new)[0], [0, 0, 0])
            bvecs = apply_affine(bv_reorient, bvecs)
            with open(basefilename + '.bvals', 'w') as fid:
                # np.savetxt could do this, but it's just a loop anyway
                for val in bvals:
                    fid.write('%s ' % val)
                fid.write('\n')
            with open(basefilename + '.bvecs', 'w') as fid:
                for row in bvecs.T:
                    for val in row:
                        fid.write('%s ' % val)
                    fid.write('\n')

    # write out dwell time if requested
    if dwell_time:
        try:
            dwell_time = calculate_dwell_time(
                pr_hdr.get_water_fat_shift(),
                pr_hdr.get_echo_train_length(),
                field_strength)
        except MRIError:
            printmessage('No EPI factors, dwell time not written')
        else:
            printmessage('Writing dwell time (%r sec) calculated assuming %sT '
                    'magnet' % (dwell_time, field_strength))
            with open(basefilename + '.dwell_time', 'w') as fid:
                fid.write('%r\n' % dwell_time)


    if origin not in ['scanner', 'fov']:
        error("Unrecognized value for --origin: '%s'." % origin, 1)
    if dwell_time and field_strength is None:
        error('Need --field-strength for dwell time calculation', 1)

    # store any exceptions
    errs = []

    printmessage('Processing %s' % infile)

    if len(errs):
        error('Caught %i exceptions. Dump follows:\n\n %s'
              % (len(errs), '\n'.join(errs)), 1)
    else:
        printmessage('Done')

def par_to_mni1slice(infile, verbose=True, outdir=None, compressed=False, overwrite=True, permit_truncated=False,
               store_header=True, bvs=False, dwell_time=False, field_strength='3.0', midslice_num=90,
               scaling='fp', minmax=('parse', 'parse'), origin='scanner', outfilename=None):
    # figure out the output filename, and see if it exists
    basefilename = splitext_addext(os.path.basename(infile))[0]
    if outdir is not None and outfilename is not None:
        # prep a file
        if compressed:
            printmessage('Using gzip compression')
            outfilename = os.path.join(outdir, outfilename + '.nii.gz' )
        else:
             outfilename = os.path.join(outdir, outfilename + '.nii' )
        if os.path.isfile(outfilename) and not overwrite:
            raise IOError('Output file "%s" exists, use --overwrite to '
                          'overwrite it' % outfilename)

    if outdir is not None and outfilename is None:
        # set output path
        basefilename = os.path.join(outdir, basefilename)
        # prep a file
        if compressed:
            printmessage('Using gzip compression')
            outfilename =  basefilename + '.nii.gz'
        else:
             outfilename = basefilename + '.nii'
        if os.path.isfile(outfilename) and not overwrite:
            raise IOError('Output file "%s" exists, use --overwrite to '
                          'overwrite it' % outfilename)
    if outdir is None and outfilename is not None:
        # prep a file
        if compressed:
            printmessage('Using gzip compression')
            outfilename = os.path.join(outdir, outfilename + '.nii.gz' )
        else:
             outfilename = os.path.join(outdir, outfilename + '.nii' )
        if os.path.isfile(outfilename) and not overwrite:
            raise IOError('Output file "%s" exists, use --overwrite to '
                          'overwrite it' % outfilename)


    # load the PAR header and data
    scaling = 'fp' if scaling == 'off' else scaling
    infile = fname_ext_ul_case(infile)
    pr_img = pr.load(infile,
                     permit_truncated=permit_truncated,
                     scaling=scaling)
    pr_hdr = pr_img.header
    affine = pr_hdr.get_affine(origin=origin)
    slope, intercept = pr_hdr.get_data_scaling(scaling)
    if scaling != 'off':
        printmessage('Using data scaling "%s"' % scaling)
    # get original scaling, and decide if we scale in-place or not
    if scaling == 'off':
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
                       [2, 1]]): # already in LAS+
        t_aff = np.eye(4)
    else: # Not in LAS+
        t_aff = inv_ornt_aff(ornt, pr_img.shape)
        affine = np.dot(affine, t_aff)
        in_data = apply_orientation(in_data, ornt)
    # Make corresponding NIfTI image
    nimg = nifti1.Nifti1Image(in_data, affine, pr_hdr)
    nhdr = nimg.header
    nhdr.set_data_dtype(out_dtype)
    nhdr.set_slope_inter(slope, intercept)

    if 'parse' in minmax:
        # need to get the scaled data
        printmessage('Loading (and scaling) the data to determine value range')
    if minmax[0] == 'parse':
        nhdr['cal_min'] = in_data.min() * slope + intercept
    else:
        nhdr['cal_min'] = float(minmax[0])
    if minmax[1] == 'parse':
        nhdr['cal_max'] = in_data.max() * slope + intercept
    else:
        nhdr['cal_max'] = float(minmax[1])

    # container for potential NIfTI1 header extensions
    if store_header:
        # dump the full PAR header content into an extension
        with open(infile, 'r') as fobj:
            hdr_dump = fobj.read()
            dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
        nhdr.extensions.append(dump_ext)

    printmessage('Writing %s' % outfilename)
    nibabel.save(nimg, outfilename)

    # write out bvals/bvecs if requested
    if bvs:
        bvals, bvecs = pr_hdr.get_bvals_bvecs()
        if bvals is None and bvecs is None:
            printmessage('No DTI volumes detected, bvals and bvecs not written')
        else:
            printmessage('Writing .bvals and .bvecs files')
            # Transform bvecs with reorientation affine
            orig2new = npl.inv(t_aff)
            bv_reorient = from_matvec(to_matvec(orig2new)[0], [0, 0, 0])
            bvecs = apply_affine(bv_reorient, bvecs)
            with open(basefilename + '.bvals', 'w') as fid:
                # np.savetxt could do this, but it's just a loop anyway
                for val in bvals:
                    fid.write('%s ' % val)
                fid.write('\n')
            with open(basefilename + '.bvecs', 'w') as fid:
                for row in bvecs.T:
                    for val in row:
                        fid.write('%s ' % val)
                    fid.write('\n')

    # write out dwell time if requested
    if dwell_time:
        try:
            dwell_time = calculate_dwell_time(
                pr_hdr.get_water_fat_shift(),
                pr_hdr.get_echo_train_length(),
                field_strength)
        except MRIError:
            printmessage('No EPI factors, dwell time not written')
        else:
            printmessage('Writing dwell time (%r sec) calculated assuming %sT '
                    'magnet' % (dwell_time, field_strength))
            with open(basefilename + '.dwell_time', 'w') as fid:
                fid.write('%r\n' % dwell_time)


    if origin not in ['scanner', 'fov']:
        error("Unrecognized value for --origin: '%s'." % origin, 1)
    if dwell_time and field_strength is None:
        error('Need --field-strength for dwell time calculation', 1)

    # store any exceptions
    errs = []

    printmessage('Processing %s' % infile)

    if len(errs):
        error('Caught %i exceptions. Dump follows:\n\n %s'
              % (len(errs), '\n'.join(errs)), 1)
    else:
        printmessage('Done')
