import os
from glob import glob
from os.path import join as pathjoin
import niprov
import nibabel
from pylabs.conversion.parrec import par_to_nii
from nibabel.volumeutils import fname_ext_ul_case
from nibabel.filename_parser import splitext_addext
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
#_opts.nb_radiolo
opts.dryrun = True
opts.verbose = True

fs = getlocaldataroot()
phantdirs = glob(pathjoin(fs, 'phantom_qT1_disc/phantom_qT1_*'))
for dir in phantdirs:
    phantB1parfile = glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR'))
    phantSPGRparfiles = glob(pathjoin(dir, 'source_parrec/*T1_MAP*.PAR'))
    phantSEIRparfiles = glob(pathjoin(dir, 'source_parrec/*__IR*_128_*.PAR'))
    phantSEIREPIparfiles = glob(pathjoin(dir, 'source_parrec/*_SEIREPI_*.PAR'))
    outdir = pathjoin(dir, 'fitted_spgr_qT1')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    par_to_nii(infile=phantB1parfile[0], outdir=outdir, outfilename='orig_b1map', scaling='dv')
    c02, c04, c10, c15, c20, c30 = 1, 1, 1, 1, 1, 1
    for parfile in phantSPGRparfiles:
        parbasename = os.path.basename(parfile)
        parname = os.path.basename(parfile).split('.')[0]
        parname = parname.replace('-', '_')
        iter_fields = iter(parname.split('_'))
        for fields in iter_fields:
            next(iter_fields, None)
            next(iter_fields, None)
            next(iter_fields, None)
            next(iter_fields, None)
            if fields[0:2] == '02':
                outspgrfile = str('orig_spgr_flip_02_'+str(c02))
                c02 +=1
            if fields[0:2] == '04':
                outspgrfile = str('orig_spgr_flip_04_'+str(c04))
                c04 +=1
            if fields[0:2] == '10':
                outspgrfile = str('orig_spgr_flip_10_'+str(c10))
                c10 +=1
            if fields[0:2] == '15':
                outspgrfile = str('orig_spgr_flip_15_'+str(c15))
                c15 +=1
            if fields[0:2] == '20':
                outspgrfile = str('orig_spgr_flip_20_'+str(c20))
                c20 +=1
            if fields[0:2] == '30':
                outspgrfile = str('orig_spgr_flip_30_'+str(c30))
                c30 +=1
        outdir = pathjoin(dir, 'fitted_spgr_qT1')
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        par_to_nii(infile=parfile, outdir=outdir, outfilename=outspgrfile, scaling='fp')
    outdir = pathjoin(dir, 'fitted_seir_qT1')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    ir500, ir1500, ir3000 = 1, 1, 1
    for parfile in phantSEIRparfiles:
        parbasename = os.path.basename(parfile)
        parname = os.path.basename(parfile).split('.')[0]
        for fields in parname.split('_'):
            if fields == '__IR500_128':
                outirfile = str('orig_seir_ti_0500_'+str(i50))
                ir500 +=1
            if fields == '__IR1500_128':
                outirfile = str('orig_seir_ti_1500_'+str(i50))
                ir1500 +=1
            if fields == '__IR3000_128':
                outirfile = str('orig_seir_ti_3000_'+str(i50))
                ir3000 +=1
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        par_to_nii(infile=parfile, outdir=outdir, outfilename=outspgrfile, scaling='dv')
    outdir = pathjoin(dir, 'fitted_seirepi_qT1')
    i50, i400, i1200, i2400, i4000 = 1, 1, 1, 1, 1
    for parfile in phantSEIREPIparfiles:
        parbasename = os.path.basename(parfile)
        parname = os.path.basename(parfile).split('.')[0]
        for fields in parname.split('_'):
            if fields == 'TI0050':
                outirfile = str('orig_seirepi_ti_0050_'+str(i50))
                i50 +=1
            if fields == 'TI0400':
                outirfile = str('orig_seirepi_ti_0400_'+str(i50))
                i400 +=1
            if fields == 'TI1200':
                outirfile = str('orig_seirepi_ti_1200_'+str(i50))
                i1200 +=1
            if fields == 'TI2400':
                outirfile = str('orig_seirepi_ti_2400_'+str(i50))
                i2400 +=1
            if fields == 'TI4000':
                outirfile = str('orig_seirepi_ti_4000_'+str(i50))
                i4000 +=1
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        par_to_nii(infile=parfile, outdir=outdir, outfilename=outspgrfile, scaling='dv')
