import os, sys
from glob import glob
from os.path import join as pathjoin
from collections import defaultdict
from mmimproc.utils.paths import getlocaldataroot
from mmimproc.conversion.phantom_conv import phantom_B1_midslice_par2mni
from mmimproc.conversion.phantom_conv import phantom_midslice_par2mni
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.utils._options import MmimprocOptions
opts = MmimprocOptions()
prov = ProvenanceWrapper()
prov.config.dryrun = False
prov.config.verbosity = True
opts.verbosity = True

def sort_par_glob (parglob):
    return sorted(parglob, key=lambda f: int(f.split('_')[-2]))

fs = getlocaldataroot()
scanner = 'slu'
phantdirs = sorted(glob(pathjoin(fs, 'phantom_qT1_'+scanner+'/phantom_qT1_*')), key=lambda f: int(f.split('_')[-1]))
phantom_ddata = defaultdict(list)
phantom_dict_fname = pathjoin('/'.join(phantdirs[0].split('/')[0:-1]), 'phantom_'+scanner+'_dict_mar22.txt')

#for testing purposes only
# for i, p in enumerate(phantdirs):
#     print(i, p)
#dir = phantdirs[1]

for dir in phantdirs:
    b1mapdir = pathjoin(dir, 'B1map_qT1')
    spgrdir = pathjoin(dir, 'fitted_spgr_qT1')
    seirdir = pathjoin(dir, 'fitted_seir_qT1')
    seirhsdir = pathjoin(dir, 'fitted_seirhs_qT1')
    seirepidir = pathjoin(dir, 'fitted_seirepi_qT1')
    tseirdir = pathjoin(dir, 'fitted_tseir_qT1')
    sdate = dir.split('/')[-1].split('_')[-1]
    # if dir == '/media/DiskArray/shared_data/js/phantom_test_disc_slu/phantom_qT1_20150309':
    #     scanner = 'disc'
    if scanner == 'disc':
        phantB1parfile = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR')))
        phantSPGRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*T1_MAP*.PAR')))
        phantSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*__IR*_128_*.PAR')))
        phantSEIRHSparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IR*_128_HS*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_SEIREPI_*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    # if dir == '/media/DiskArray/shared_data/js/phantom_test_disc_slu/phantom_qT1_20160113':
    #     scanner = 'slu'
    if scanner == 'slu':
        phantB1parfile = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*B1MAP*.PAR')))
        phantSPGRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*3D_SPGR_*.PAR')))
        phantSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IR*_128_CLEAR*.PAR')))
        phantSEIREPIparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_9shots_EPI11_*.PAR')))
        phantSEIRHSparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IR*_128_HS*.PAR')))
        phantTSEIRparfiles = sort_par_glob(glob(pathjoin(dir, 'source_parrec/*_IRTSE*.PAR')))

    for parfile in phantSPGRparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, datadict=phantom_ddata, method='orig_spgr', outdir=spgrdir,
                                               outfilename='orig_spgr', scaling=scaling, scanner=scanner)
        for k, v in zip(key, val):
            phantom_ddata[k].append(v)

    for parfile in phantSEIRparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, datadict=phantom_ddata, method='seir', outdir=seirdir,
                                               outfilename='orig_seir', scaling=scaling, scanner=scanner)
        for k, v in zip(key, val):
             phantom_ddata[k].append(v)

    for parfile in phantSEIRHSparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, datadict=phantom_ddata, method='seirhs', outdir=seirhsdir,
                                               outfilename='orig_seirhs', scaling=scaling, scanner=scanner)
        for k, v in zip(key, val):
            phantom_ddata[k].append(v)

    for parfile in phantSEIREPIparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, datadict=phantom_ddata, method='seirepi', outdir=seirepidir,
                                               outfilename='seirepi', scaling=scaling, scanner=scanner)
        for k, v in zip(key, val):
            phantom_ddata[k].append(v)

    for parfile in phantTSEIRparfiles:
        scaling = 'fp'
        key, val = phantom_midslice_par2mni(parfile=parfile, datadict=phantom_ddata, method='tseir', outdir=tseirdir,
                                               outfilename='tseir', scaling=scaling, scanner=scanner)
        for k, v in zip(key, val):
            phantom_ddata[k].append(v)

    for parfile in phantB1parfile:
        scaling = 'dv'
        key, val = phantom_B1_midslice_par2mni(parfile=parfile, datadict=phantom_ddata, outdir=b1mapdir,
                                               outfilename='b1map', scaling=scaling, scanner=scanner)
        for k, v in zip(key, val):
            phantom_ddata[k].append(v)

#todo: make h5 file write to save data
# with open(phantom_dict_fname, "wb") as f:
#     f.write(dumps(phantom_ddata))

