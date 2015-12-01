import os, sys
from glob import glob
from os.path import join as pathjoin
import collections
from collections import defaultdict
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
from niprov import Context
from pylabs.utils._options import PylabsOptions
from pylabs.conversion.phantom_conv import phantom_B1_midslice_par2mni
opts = NiprovOptions()
_opts = PylabsOptions()
opts.dryrun = False
opts.verbose = True
prov = Context()

def sort_par_glob (parglob):
    return sorted(parglob, key=lambda f: int(f.split('_')[-2]))




#
# def sort_par_glob (parglob):
#     return sorted(parglob, key=lambda f: int(f.split('_')[-2]))
# fs = getlocaldataroot()
# phantdirs = sorted(glob.glob(pathjoin(fs, 'phantom_qT1_disc/phantom_qT1_*')), key=lambda f: int(f.split('_')[-1]))
# scanner = phantdirs[0].split('/')[-2]
# scanner = str(scanner.split('_')[-1])
# scandateexception = ['20141108']
# conv_scans = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
# phantdirs = sorted(glob.glob(pathjoin(fs, 'phantom_qT1_disc/phantom_qT1_*')), key=lambda f: int(f.split('_')[-1]))
# dir = phantdirs[14]
# phantB1parfile = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR')))
# parfile = phantB1parfile[0]
# b1mapdir = pathjoin(dir, 'B1map_qT1')
# outdir = b1mapdir
# scan_info_dict=None
# scandateexception = ['20141108']
# exceptions = scandateexception
# outfilename = 'b1map'
# verbose=True
# scaling='dv'
# minmax=('parse', 'parse')
# origin='scanner'
# overwrite=True
# run = 1
#









fs = getlocaldataroot()
phantdirs = sorted(glob.glob(pathjoin(fs, 'phantom_qT1_disc/phantom_qT1_*')), key=lambda f: int(f.split('_')[-1]))
scanner = phantdirs[0].split('/')[-2]
scanner = str(scanner.split('_')[-1])
scandateexception = ['20141108']
fslroi = ExtractROI()
fslfilter = SpatialFilter()
fslmaths = BinaryMaths()
fslswapdim = SwapDimensions()
fslflirt = FLIRT()
fslapplyxfm = ApplyXfm()
phantom_disc_ddata = defaultdict(list)
for dir in phantdirs:
    b1mapdir = pathjoin(dir, 'B1map_qT1')
    spgrdir = pathjoin(dir, 'fitted_spgr_qT1')
    seirdir = pathjoin(dir, 'fitted_seir_qT1')
    seirhsdir = pathjoin(dir, 'fitted_seirhs_qT1')
    seirepidir = pathjoin(dir, 'fitted_seirepi_qT1')
    tseirdir = pathjoin(dir, 'fitted_tseir_qT1')
    sdate = dir.split('/')[-1].split('_')[-1]
    if scanner == 'disc':
        phantB1parfile = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR')))
        phantSPGRparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*T1_MAP*.PAR')))
        phantSEIRparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*__IR*_128_*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*_SEIREPI_*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    if scanner == 'slu':
        phantSPGRparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*3D_SPGR_*.PAR')))
        phantSEIRparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*_IR*_128_CLEAR*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*_9shots_EPI11_*.PAR')))
        phantSEIRHSparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*_IR*_128_HS*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob.glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    if dir and not os.path.exists(spgrdir):
        os.makedirs(spgrdir)

    scaling = 'fp'
    spgr_counter = collections.defaultdict(int)
    for parfile in phantSPGRparfiles:
        parbasename = os.path.basename(parfile)
        infile = fname_ext_ul_case(parfile)
        pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
        pr_hdr = pr_img.header
        flipangle = int(pr_hdr.__getattribute__('image_defs')[0][29])
        spgr_tr = int(pr_hdr.__getattribute__('general_info').get('repetition_time'))
        spgr_max_slices = int(pr_hdr.__getattribute__('general_info').get('max_slices'))
        spgr_mid_slice_num = int(spgr_max_slices) / 2
        scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".","")
        if scandate != sdate:
            print "Error! found date discrepancy in "+parfile
        TR = int(spgr_tr)
        spgr_counter[flipangle] += 1
        print parfile, flipangle, spgr_tr, spgr_counter.get(flipangle)
        outspgrfile = 'orig_spgr_fa_'+str(flipangle).zfill(2)+'_'+str(spgr_counter.get(flipangle))
        if parfile and not os.path.exists(spgrdir):
            os.makedirs(spgrdir)
        par_to_nii(infile=parfile, outdir=spgrdir, outfilename=outspgrfile, scaling=scaling, midslice_num=spgr_mid_slice_num)
        if scandate == '20141108':
            if flipangle < 10:
                swap_spgr = fslswapdim.run(in_file=pathjoin(spgrdir, 'orig_spgr_fa_0'+str(flipangle)+'_'+str(spgr_counter.get(flipangle))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(spgrdir, 'swap_spgr_fa_0'+str(flipangle)+'_'+str(spgr_counter.get(flipangle))+'.nii'), output_type='NIFTI' )
                outspgrfile = 'swap_spgr_fa_0'+str(flipangle)+'_'+str(spgr_counter.get(flipangle))
            if flipangle >= 10:
                swap_spgr = fslswapdim.run(in_file=pathjoin(spgrdir, 'orig_spgr_fa_'+str(flipangle)+'_'+str(spgr_counter.get(flipangle))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(spgrdir, 'swap_spgr_fa_'+str(flipangle)+'_'+str(spgr_counter.get(flipangle))+'.nii'), output_type='NIFTI' )
                outspgrfile = 'swap_spgr_fa_'+str(flipangle)+'_'+str(spgr_counter.get(flipangle))
        file_fa_pair = (outspgrfile, flipangle, int(spgr_counter.get(flipangle)))
        conv_scans[scandate]['spgr'][TR].append(file_fa_pair)


        #b1corrected_spgr = fslmaths.run(in_file=pathjoin(spgrdir, outspgrfile+'.nii.gz'), operand_file=pathjoin(spgrdir, b1mapfile+'.nii.gz',  output_datatype='float'))

    scaling = 'fp'
    seir_counter = collections.defaultdict(int)
    for parfile in phantSEIRparfiles:
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
        print parfile, seir_ti, seir_tr, seir_counter.get(seir_ti)
        if seir_ti < 100:
            outseirfile = 'orig_seir_ti_00'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))
        if seir_ti >= 100 and seir_ti < 1000:
            outseirfile = 'orig_seir_ti_0'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))
        if seir_ti >= 1000:
            outseirfile = 'orig_seir_ti_'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))
        if parfile and not os.path.exists(seirdir):
            os.makedirs(seirdir)
        par_to_nii(infile=parfile, outdir=seirdir, outfilename=outseirfile, scaling=scaling)
        if scandate == '20141108':
            if seir_ti < 100:
                swap_seir = fslswapdim.run(in_file=pathjoin(seirdir, 'orig_seir_ti_00'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirdir, 'orig_seir_ti_00'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))+'.nii'), output_type='NIFTI' )
                outseirfile = 'swap_seir_ti_00'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))
            if seir_ti >= 100 and seir_ti < 1000:
                swap_seir = fslswapdim.run(in_file=pathjoin(seirdir, 'orig_seir_ti_0'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirdir, 'orig_seir_ti_0'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))+'.nii'), output_type='NIFTI' )
                outseirfile = 'swap_seir_ti_0'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))
            if seir_ti >= 1000:
                swap_seir = fslswapdim.run(in_file=pathjoin(seirdir, 'orig_seir_ti_'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirdir, 'orig_seir_ti_00'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))+'.nii'), output_type='NIFTI' )
                outseirfile = 'swap_seir_ti_'+str(seir_ti)+'_'+str(seir_counter.get(seir_ti))
        file_ti_pair = (outseirfile, int(seir_ti), int(seir_counter.get(seir_ti)))
        conv_scans[scandate]['seir'][TR].append(file_ti_pair)

    if scanner == 'slu':
        scaling = 'fp'
        if not os.path.exists(seirhsdir):
            os.makedirs(seirhsdir)
        seirhs_counter = collections.defaultdict(int)
        for parfile in phantSEIRHSparfiles:
            parbasename = os.path.basename(parfile)
            infile = fname_ext_ul_case(parfile)
            pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
            pr_hdr = pr_img.header
            seirhs_ti = int(pr_hdr.__getattribute__('image_defs')[0][34])
            seirhs_tr = int(pr_hdr.__getattribute__('general_info').get('repetition_time'))
            scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".","")
            TR = int(seirhs_tr)
            if scandate != sdate:
                print "Error! found date discrepancy in "+parfile
            seirhs_counter[seirhs_ti] += 1
            if seirhs_ti < 100:
                outseirhsfile = 'orig_seirhs_ti_00'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))
            if seirhs_ti >= 100 and invtime < 1000:
                outseirhsfile = 'orig_seirhs_ti_0'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))
            if seirhs_ti >= 1000:
                outseirhsfile = 'orig_seirhs_ti_'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))
            if parfile and not os.path.exists(seirhsdir):
                os.makedirs(seirhsdir)
            par_to_nii(infile=parfile, outdir=seirhsdir, outfilename=outseirhsfile, scaling=scaling)
            if scandate == '20141108':
                if seirhs_ti < 100:
                    swap_seirhs = fslswapdim.run(in_file=pathjoin(seirhsdir, 'orig_seirhs_ti_00'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirhsdir, 'swap_seirhs_ti_00'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))+'.nii'), output_type='NIFTI' )
                    outseirhsfile = 'swap_seirhs_ti_'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))
                if seirhs_ti >= 100 and seirhs_ti < 1000:
                    swap_seirhs = fslswapdim.run(in_file=pathjoin(seirhsdir, 'orig_seirhs_ti_0'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirhsdir, 'swap_seirhs_ti_0'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))+'.nii'), output_type='NIFTI' )
                    outseirhsfile = 'swap_seirhs_ti_'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))
                if seirhs_ti >= 1000:
                    swap_seirhs = fslswapdim.run(in_file=pathjoin(seirhsdir, 'orig_seirhs_ti_'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirhsdir, 'swap_seirhs_ti_'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))+'.nii'), output_type='NIFTI' )
                    outseirhsfile = 'swap_seirhs_ti_'+str(seirhs_ti)+'_'+str(seirhs_counter.get(seirhs_ti))
            file_seirhs_pair = (outseirhsfile, seirhs_ti, int(seirhs_counter.get(seirhs_ti)))
            conv_scans[scandate]['seirhs'][TR].append(file_seirhs_pair)

    scaling = 'fp'
    if not os.path.exists(seirepidir):
        os.makedirs(seirepidir)
    seirepi_counter = collections.defaultdict(int)
    for parfile in phantSEIREPIparfiles:
        parbasename = os.path.basename(parfile)
        infile = fname_ext_ul_case(parfile)
        pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
        pr_hdr = pr_img.header
        seirepi_ti = int(pr_hdr.__getattribute__('image_defs')[0][34])
        seirepi_tr = int(pr_hdr.__getattribute__('general_info').get('repetition_time'))
        scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".","")
        if scandate != sdate:
            print "Error! found date discrepancy in "+parfile
        TR = int(seirepi_tr)
        seirepi_counter[seirepi_ti] += 1
        print parfile, seirepi_ti, seirepi_tr, seirepi_counter.get(seirepi_ti)
        if seirepi_ti < 100:
            outseirepifile = 'orig_seirepi_ti_00'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))
        if seirepi_ti >= 100 and seirepi_ti < 1000:
            outseirepifile = 'orig_seirepi_ti_0'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))
        if seirepi_ti >= 1000:
            outseirepifile = 'orig_seirepi_ti_'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))
        if parfile and not os.path.exists(seirepidir):
            os.makedirs(seirepidir)
        par_to_nii(infile=parfile, outdir=seirepidir, outfilename=outseirepifile, scaling=scaling)
        if scandate == '20141108':
            if seirepi_ti < 100:
                swap_seirepi = fslswapdim.run(in_file=pathjoin(seirepidir, 'orig_seirepi_ti_00'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirepidir, 'swap_seirepi_ti_00'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))+'.nii'), output_type='NIFTI' )
                outseirepifile = 'swap_seirepi_ti_00'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))
            if seirepi_ti >= 100 and seirepi_ti < 1000:
                swap_seirepi = fslswapdim.run(in_file=pathjoin(seirepidir, 'orig_seirepi_ti_0'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirepidir, 'swap_seirepi_ti_0'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))+'.nii'), output_type='NIFTI' )
                outseirepifile = 'swap_seirepi_ti_0'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))
            if seirepi_ti >= 1000:
                swap_seirepi = fslswapdim.run(in_file=pathjoin(seirepidir, 'orig_seirepi_ti_'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(seirepidir, 'swap_seirepi_ti_'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))+'.nii'), output_type='NIFTI' )
                outseirepifile = 'swap_seirepi_ti_'+str(seirepi_ti)+'_'+str(seirepi_counter.get(seirepi_ti))
        file_seirepi_pair = (outseirepifile, seirepi_ti, int(seirepi_counter.get(seirepi_ti)))
        conv_scans[scandate]['seirepi'][TR].append(file_seirepi_pair)


    scaling = 'fp'
    tseir_counter = collections.defaultdict(int)
    for parfile in phantTSEIRparfiles:
        parbasename = os.path.basename(parfile)
        infile = fname_ext_ul_case(parfile)
        pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
        pr_hdr = pr_img.header
        tseir_ti = int(pr_hdr.__getattribute__('image_defs')[0][34])
        tseir_tr = int(pr_hdr.__getattribute__('general_info').get('repetition_time'))
        scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".","")
        TR = int(tseir_tr)
        if scandate != sdate:
            print "Error! found date discrepancy in "+parfile
        tseir_counter[tseir_ti] += 1
        print parfile, tseir_ti, tseir_tr, tseir_counter.get(tseir_ti)
        if tseir_ti < 100:
            outtseirfile = 'orig_tseir_ti_00'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))
        if tseir_ti >= 100 and tseir_ti < 1000:
            outtseirfile = 'orig_tseir_ti_0'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))
        if tseir_ti >= 1000:
            outtseirfile = 'orig_tseir_ti_'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))
        if parfile and not os.path.exists(tseirdir):
            os.makedirs(tseirdir)
        par_to_nii(infile=parfile, outdir=tseirdir, outfilename=outtseirfile, scaling=scaling)
        if scandate == '20141108':
            if tseir_ti < 100:
                swap_tseir = fslswapdim.run(in_file=pathjoin(tseirdir, 'orig_tseir_ti_00'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(tseirdir, 'swap_tseir_ti_00'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))+'.nii'), output_type='NIFTI' )
                outtseirfile = 'swap_tseir_ti_00'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))
            if tseir_ti >= 100 and tseir_ti < 1000:
                swap_tseir = fslswapdim.run(in_file=pathjoin(tseirdir, 'orig_tseir_ti_0'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(tseirdir, 'swap_tseir_ti_0'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))+'.nii'), output_type='NIFTI' )
                outtseirfile = 'swap_tseir_ti_0'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))
            if tseir_ti >= 1000:
                swap_tseir = fslswapdim.run(in_file=pathjoin(tseirdir, 'orig_tseir_ti_'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(tseirdir, 'swap_tseir_ti_'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))+'.nii'), output_type='NIFTI' )
                outtseirfile = 'swap_tseir_ti_'+str(tseir_ti)+'_'+str(tseir_counter.get(tseir_ti))
        file_tseir_pair = (outtseirfile, tseir_ti, int(tseir_counter.get(tseir_ti)))
        conv_scans[scandate]['tseir'][TR].append(file_tseir_pair)


#prepare b1 map for correction
    if scanner == 'disc':
        b1map_counter = collections.defaultdict(int)
        for parfile in phantB1parfile:
            scaling = 'dv'
            parbasename = os.path.basename(parfile)
            infile = fname_ext_ul_case(parfile)
            pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
            pr_hdr = pr_img.header
            scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".", "")
            b1map_tr = int(pr_hdr.__getattribute__('general_info').get('repetition_time'))
            if scandate != sdate:
                print "Error! found date discrepancy in "+parfile
            b1map_counter[scandate] += 1
            outb1mapfile = str('orig_b1map_'+str(b1map_counter.get(scandate)))
            par_to_nii(infile=parfile, outdir=spgrdir, outfilename=outb1mapfile, scaling='dv')
            if scandate == '20141108':
                swap_b1map = fslswapdim.run(in_file=pathjoin(spgrdir, outb1mapfile+'.nii'), new_dims=('-x', 'y', 'z'), out_file=pathjoin(spgrdir, 'swap_b1map_phase_'+str(b1map_counter.get(scandate))+'.nii'), output_type='NIFTI' )
                outb1mapfile = 'swap_b1map_phase_'+str(b1map_counter.get(scandate))
            orig_b1map_phase = fslroi.run(in_file=pathjoin(spgrdir, outb1mapfile+'.nii'), roi_file=pathjoin(spgrdir, 'orig_b1map_phase_'+str(b1map_counter.get(scandate))+'.nii.gz'), t_min=2, t_size=1)
            orig_b1map_mag = fslroi.run(in_file=pathjoin(spgrdir, outb1mapfile+'.nii'),
                                        roi_file=pathjoin(spgrdir, 'orig_b1map_mag_'+str(b1map_counter.get(scandate))+'.nii.gz'),
                                        t_min=0, t_size=1)
            fslfilter.inputs.in_file = pathjoin(spgrdir, 'orig_b1map_phase_'+str(b1map_counter.get(scandate))+'.nii.gz')
            fslfilter.inputs.out_file = pathjoin(spgrdir, 'b1map_phase_medfilt6_'+str(b1map_counter.get(scandate))+'.nii.gz')
            fslfilter.inputs.kernel_shape = 'box'
            fslfilter.inputs.kernel_size = 6
            fslfilter.inputs.operation = 'median'
            fslfilter.run()
            mfilt_b1map_phase_sl16 = fslroi.run(in_file=pathjoin(spgrdir, 'b1map_phase_medfilt6_'+str(b1map_counter.get(scandate))+'.nii.gz'),
                                                roi_file=pathjoin(spgrdir, 'b1map_phase_medfilt6_sl16_'+str(b1map_counter.get(scandate))+'.nii.gz'),
                                                x_min=0, x_size=-1, y_min=0, y_size=-1, z_min=15, z_size=1)
            b1mapfile_1sl = 'b1map_phase_medfilt6_sl16_'+str(b1map_counter.get(scandate))
            b1mapfile = 'b1map_phase_medfilt6_'+str(b1map_counter.get(scandate))
            fslapplyxfm.inputs.in_file = pathjoin(spgrdir, b1mapfile+'.nii.gz')
            fslapplyxfm.inputs.reference = pathjoin(spgrdir, outspgrfile+'.nii')
            fslapplyxfm.inputs.out_file = pathjoin(spgrdir, b1mapfile+'_reg2spgr.nii.gz')
            fslapplyxfm.inputs.in_matrix_file = str(os.environ.get('FSLDIR'))+'/etc/flirtsch/ident.mat'
            fslapplyxfm.inputs.interp = 'nearestneighbour'
            fslapplyxfm.inputs.apply_xfm = True
            b1mapfile_reg2spgr = fslapplyxfm.run()
            if b1map_counter.get(scandate) > 1:
                print 'Danger more than one b1 map file detected! '+parfile
            file_pair = (b1mapfile, int(b1map_tr), int(b1map_counter.get(scandate)), b1mapfile_1sl, 'orig_b1map_mag_'+str(b1map_counter.get(scandate)))
            conv_scans[scandate]['b1map'][0].append(file_pair)

print conv_scans
with open(pathjoin('/'.join(phantdirs[0].split('/')[0:-1]), 'conv_scans_dict.txt'), "wb") as f:
    f.write(dumps(conv_scans))
