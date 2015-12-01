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

import os, sys
from glob import glob
from os.path import join as pathjoin
import collections
import cPickle, cloud
from cloud.serialization.cloudpickle import dumps
from nipype.interfaces import fsl
from nipype.interfaces.fsl import ExtractROI
from nipype.interfaces.fsl import ImageMaths
from nipype.interfaces.fsl import SpatialFilter
from nipype.interfaces.fsl import BinaryMaths
from nipype.interfaces.fsl import SwapDimensions
from nipype.interfaces.fsl import FLIRT
from nipype.interfaces.fsl import ApplyXfm
import niprov
import nibabel
import numpy as np
import numpy.linalg as npl
import nibabel.parrec as pr
from nibabel.volumeutils import fname_ext_ul_case
from nibabel.filename_parser import splitext_addext
from pylabs.conversion.parrec import par_to_nii
from pylabs.correlation.behavior import csv2fslmat
from pylabs.correlation.regfilt import multiregfilt
from pylabs.correlation.randpar import multirandpar
from pylabs.correlation.atlas import report, atlaslabels
from pylabs.utils.paths import getlocaldataroot
from pylabs.utils.timing import waitForFiles
from pylabs.utils.selection import select, withVoxelsOverThresholdOf
from pylabs.utils.files import deconstructRandparFiles
from niprov.options import NiprovOptions
from pylabs.utils._options import PylabsOptions
opts = NiprovOptions()
_opts = PylabsOptions()
opts.dryrun = False
opts.verbose = True

def sort_par_glob (parglob):
    return sorted(parglob, key=lambda f: int(f.split('_')[-2]))

def printmessage(msg, indent=0):
    if verbose:
        print("%s%s" % (' ' * indent, msg))


fs = getlocaldataroot()
phantdirs = sorted(glob(pathjoin(fs, 'phantom_qT1_disc/phantom_qT1_*')), key=lambda f: int(f.split('_')[-1]))
scanner = phantdirs[0].split('/')[-2]
scanner = str(scanner.split('_')[-1])
scandateexception = ['20141108']
fslroi = ExtractROI()
fslfilter = SpatialFilter()
fslmaths = BinaryMaths()
fslswapdim = SwapDimensions()
fslflirt = FLIRT()
fslapplyxfm = ApplyXfm()
conv_scans = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
conv_scans_test = {}
for dir in phantdirs:
    #dir = phantdirs[8]
    spgrdir = pathjoin(dir, 'fitted_spgr_qT1')
    seirdir = pathjoin(dir, 'fitted_seir_qT1')
    seirhsdir = pathjoin(dir, 'fitted_seirhs_qT1')
    seirepidir = pathjoin(dir, 'fitted_seirepi_qT1')
    tseirdir = pathjoin(dir, 'fitted_tseir_qT1')
    sdate = dir.split('/')[-1].split('_')[-1]
    if scanner == 'disc':
        phantB1parfile = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR')))
        phantSPGRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*T1_MAP*.PAR')))
        phantSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*__IR*_128_*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_SEIREPI_*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    scaling = 'fp'
    seir_counter = collections.defaultdict(int)
    for parfile in phantSEIRparfiles:

        #this is where function begins
        parbasename = os.path.basename(parfile)
        infile = fname_ext_ul_case(parfile)
        pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
        pr_hdr = pr_img.header
        seir_ti = int(pr_hdr.__getattribute__('image_defs')[0][34])
        seir_tr = int(pr_hdr.__getattribute__('general_info').get('repetition_time'))
        scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".", "")
        if scandate != sdate:
            print "Error! found date discrepancy in "+parfile
        TR = int(seir_tr)
        if TR ==6999:
            TR = 7000
        seir_counter[seir_ti] += 1
        outseirfile = 'orig_seir_ti_'+str(seir_ti).zfill(4)+'_1slmni_'+str(seir_counter.get(seir_ti))
        if parfile and not os.path.exists(seirdir):
            os.makedirs(seirdir)

        print parfile, seir_ti, seir_tr, seir_counter.get(seir_ti), outseirfile
        file_ti_pair = (outseirfile, int(seir_ti), int(seir_counter.get(seir_ti)))
        conv_scans[scandate]['seir'][TR].append(file_ti_pair)


        scaling='fp'; minmax=('parse', 'parse'); origin='scanner';
        store_header=True; bvs=False; dwell_time=False; field_strength='3.0'; midslice_num=90
        outdir=seirdir; verbose=True
        compressed=False; overwrite=True; permit_truncated=False
        scaling='fp'; minmax=('parse', 'parse'); origin='scanner';


        outfilename = outseirfile

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

        scaling = 'fp' if scaling == 'off' else scaling
        infile = fname_ext_ul_case(infile)
        pr_img = pr.load(infile,
                         permit_truncated=permit_truncated,
                         scaling=scaling)
        pr_hdr = pr_img.header
        affine = pr_hdr.get_affine(origin=origin)
        slope, intercept = pr_hdr.get_data_scaling(scaling)

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

        mnizoomfactor = 218/float(pr_img.shape[1])
        slice_mag = pr_img.get_data()[:,:,0,0]
        slice218 = scipy.ndimage.zoom(slice_mag, mnizoomfactor, order=0)
        slice_T = slice218[18:200,:]

        #apply xform
        affine = np.asarray(affine)
        q, p = affine.shape[0]-1, affine.shape[1]-1
        RZS = affine[:q, :p]
        zooms = np.sqrt(np.sum(RZS * RZS, axis=0))
        zooms[zooms == 0] = 1; RS = RZS / zooms
        P, S, Qs = npl.svd(RS)

        tol=None
        if tol is None:
            tol = S.max() * max(RS.shape) * np.finfo(S.dtype).eps
        keep = (S > tol)
        R = np.dot(P[:, keep], Qs[keep])

        ornt = np.ones((p, 2), dtype=np.int8) * np.nan
        for in_ax in range(p):
            col = R[:, in_ax]
            if not np.allclose(col, 0):
                out_ax = np.argmax(np.abs(col))
                ornt[in_ax, 0] = out_ax
                assert col[out_ax] != 0
                if col[out_ax] < 0:
                    ornt[in_ax, 1] = -1
                else:
                    ornt[in_ax, 1] = 1
                # remove the identified axis from further consideration, by
                # zeroing out the corresponding row in R
                R[out_ax, :] = 0

        t_aff = inv_ornt_aff(ornt, pr_img.shape)
        affine = np.dot(affine, t_aff)

        slicemni = apply_orientation(slice_T, ornt[0:2])

        if scandate != '20141108':
            slicemni = np.flipud(slicemni)

        affine[0,0] = -1
        affine[0,3] = 90
        affine[0,3] = 90.0
        affine[1,1] = 1
        affine[1,3] = 126.0
        affine[2,2] = 1
        affine[2,3] = -72
        affine

        nimg = nifti1.Nifti1Image(slicemni, affine, pr_hdr)
        nhdr = nimg.header
        out_dtype = np.float32
        nhdr.set_data_dtype(out_dtype)
        nhdr.set_slope_inter(slope, intercept)
        with open(infile, 'r') as fobj:
            hdr_dump = fobj.read()
            dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
        nhdr.extensions.append(dump_ext)

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
        nibabel.save(nimg, outfilename)

print conv_scans
with open(pathjoin('/'.join(phantdirs[0].split('/')[0:-1]), 'conv_phant_1slmni_scans_dict.txt'), "wb") as f:
    f.write(dumps(conv_scans))
