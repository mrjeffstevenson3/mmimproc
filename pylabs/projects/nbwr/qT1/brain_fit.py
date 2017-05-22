from pathlib import *
import numpy as np
import nibabel as nib
import nipype, os
import nipype.interfaces.fsl as fsl
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext, appendposix
from pylabs.projects.nbwr.file_names import project, spgr_fa5_fname, spgr_fa15_fname, spgr_fa30_fname, b1map_fname
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
if nipype.__version__ >= '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI')

if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
else:
    antsRegistrationSyN = Path(os.environ.get('ANTSPATH') , 'antsRegistrationSyN.sh')


# b1map, spgr05, spgr15, spgr30 = b1map_fname[0], spgr_fa5_fname[0], spgr_fa15_fname[0], spgr_fa30_fname[0]


for b1map, spgr05, spgr15, spgr30 in zip(b1map_fname, spgr_fa5_fname, spgr_fa15_fname, spgr_fa30_fname):
    b1map_dir = fs/project/b1map.split('_')[0] / b1map.split('_')[1] / 'fmap'
    spgr_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'qt1'
    b1magcmd = ' '.join(['fslroi', str(b1map_dir/b1map), str(appendposix(b1map_dir/b1map, '_mag')), '0', '1'])
    b1phasecmd = ' '.join(['fslroi', str(b1map_dir/b1map), str(appendposix(b1map_dir/b1map, '_phase')), '2', '1'])
    b1tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(appendposix(b1map_dir/str(b1map+'.nii'), '_mag')), '-f',
                str(spgr_dir/str(spgr30+'.nii')), '-o', str(appendposix(b1map_dir/b1map, '_mag_reg2spgr30_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    b1tospgr30antscmd = ' '.join(b1tospgr30antscmd)

    spgr05tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(spgr_dir/str(spgr05+'.nii')), '-f',
                str(spgr_dir/str(spgr30+'.nii')), '-o', str(spgr_dir/str(spgr05 + '_reg2spgr30_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    spgr05tospgr30antscmd = ' '.join(spgr05tospgr30antscmd)
    spgr15tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(spgr_dir/str(spgr15+'.nii')), '-f',
                str(spgr_dir/str(spgr30+'.nii')), '-o', str(spgr_dir/str(spgr15 + '_reg2spgr30_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    spgr15tospgr30antscmd = ' '.join(spgr15tospgr30antscmd)
    results = ()
    with WorkingContext(str(b1map_dir)):
        results += run_subprocess(b1magcmd)
        results += run_subprocess(b1phasecmd)
        results += run_subprocess(b1tospgr30antscmd)
    with WorkingContext(str(spgr_dir)):
        results += run_subprocess(spgr05tospgr30antscmd)
        results += run_subprocess(spgr15tospgr30antscmd)

