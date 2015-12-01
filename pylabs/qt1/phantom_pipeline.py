import os, sys
from glob import glob
from os.path import join as pathjoin
import collections
from collections import defaultdict
import cPickle, cloud
from cloud.serialization.cloudpickle import dumps
import nibabel.parrec as pr
from nibabel.volumeutils import fname_ext_ul_case
from pylabs.utils.paths import getlocaldataroot
from pylabs.conversion.phantom_conv import phantom_B1_midslice_par2mni
from pylabs.conversion.phantom_conv import phantom_midslice_par2mni
from niprov import Context
from pylabs.utils._options import PylabsOptions
_opts = PylabsOptions()
prov = Context()
#opts.dryrun = False
#opts.verbose = True
verbose = True

def sort_par_glob (parglob):
    return sorted(parglob, key=lambda f: int(f.split('_')[-2]))

fs = getlocaldataroot()
phantdirs = sorted(glob(pathjoin(fs, 'phantom_qT1_disc/phantom_qT1_*')), key=lambda f: int(f.split('_')[-1]))
scanner = phantdirs[0].split('/')[-2]
scanner = str(scanner.split('_')[-1])
scandateexception = ['20141108']
phantom_disc_ddata = defaultdict(list)
phantom_slu_ddata = defaultdict(list)

# for i, p in enumerate(phantdirs):
#     print i, p

phantdirs = [phantdirs[40]]

for dir in phantdirs:
    b1mapdir = pathjoin(dir, 'B1map_qT1')
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
        phantSEIRHSparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IR*_128_HS*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_SEIREPI_*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    if scanner == 'slu':
        phantSPGRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*3D_SPGR_*.PAR')))
        phantSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IR*_128_CLEAR*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_9shots_EPI11_*.PAR')))
        phantSEIRHSparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IR*_128_HS*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    b1map_counter = collections.defaultdict(int)
    for parfile in phantB1parfile:
        scaling = 'dv'
        b1map_counter[sdate] += 1
        key, val = phantom_B1_midslice_par2mni(parfile=parfile, outdir=b1mapdir, exceptions=scandateexception,
                                               outfilename='b1map',run=b1map_counter[sdate], scaling=scaling)
        for k, v in zip(key, val):
            if scanner == 'disc':
                phantom_disc_ddata[k].append(v)
            elif scanner == 'slu':
                phantom_slu_ddata[k].append(v)

    seir_counter = collections.defaultdict(int)
    seir_counter[sdate] += 1
    for parfile in phantSEIRparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, method='seir', outdir=seirdir, exceptions=scandateexception,
                                               outfilename='orig_seir',run=seir_counter[sdate], scaling=scaling)
        for k, v in zip(key, val):
            if scanner == 'disc':
                phantom_disc_ddata[k].append(v)
            elif scanner == 'slu':
                phantom_slu_ddata[k].append(v)

    seirhs_counter = collections.defaultdict(int)
    seirhs_counter[sdate] += 1
    for parfile in phantSEIRHSparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, method='seirhs', outdir=seirhsdir, exceptions=scandateexception,
                                               outfilename='orig_seir',run=seirhs_counter[sdate], scaling=scaling)
        for k, v in zip(key, val):
            if scanner == 'disc':
                phantom_disc_ddata[k].append(v)
            elif scanner == 'slu':
                phantom_slu_ddata[k].append(v)

    spgr_counter = collections.defaultdict(int)
    spgr_counter[sdate] += 1
    for parfile in phantSPGRparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, method='orig_spgr', outdir=spgrdir, exceptions=scandateexception,
                                               outfilename='orig_spgr',run=spgr_counter[sdate], scaling=scaling)
        for k, v in zip(key, val):
            if scanner == 'disc':
                phantom_disc_ddata[k].append(v)
            elif scanner == 'slu':
                phantom_slu_ddata[k].append(v)

    seirepi_counter = collections.defaultdict(int)
    seirepi_counter[sdate] += 1
    for parfile in phantSEIREPIparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, method='seirepi', outdir=seirepidir, exceptions=scandateexception,
                                               outfilename='seirepi',run=seirepi_counter[sdate], scaling=scaling)
        for k, v in zip(key, val):
            if scanner == 'disc':
                phantom_disc_ddata[k].append(v)
            elif scanner == 'slu':
                phantom_slu_ddata[k].append(v)

    tseir_counter = collections.defaultdict(int)
    tseir_counter[sdate] += 1
    for parfile in phantTSEIRparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, method='tseir', outdir=seirepidir, exceptions=scandateexception,
                                               outfilename='tseir',run=tseir_counter[sdate], scaling=scaling)
        for k, v in zip(key, val):
            if scanner == 'disc':
                phantom_disc_ddata[k].append(v)
            elif scanner == 'slu':
                phantom_slu_ddata[k].append(v)

if scanner == 'disc':
    with open(pathjoin('/'.join(phantdirs[0].split('/')[0:-1]), 'phantom_disc_dict.txt'), "wb") as f:
        f.write(dumps(phantom_disc_ddata))
elif scanner == 'slu':
    with open(pathjoin('/'.join(phantdirs[0].split('/')[0:-1]), 'phantom_slu_dict.txt'), "wb") as f:
        f.write(dumps(phantom_slu_ddata))