# wip b1 map correction functions used in fs, qT1, vbm, mrs
from pathlib import *
import os
import nibabel as nib
from scipy.ndimage.filters import median_filter as medianf
from pylabs.utils.paths import getnetworkdataroot
from pylabs.io.images import savenii
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
# set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
# setup paths and file names to process
fs = Path(getnetworkdataroot())

if not os.environ['FSLOUTPUTTYPE'] == 'NIFTI_GZ':
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'

if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
else:
    antsRegistrationSyN = Path(os.environ.get('ANTSPATH'), 'antsRegistrationSyN.sh')

def correct4b1(project, subject, session, b1map_file, target, reg_dir_name):
    reg_dir = fs/project/subject/session/'reg'/reg_dir_name
    if not reg_dir.is_dir():
        reg_dir.mkdir(parents=True)
    b1magcmd = ['fslroi', str(b1map_file), str(appendposix(b1map_file, '_mag')), '0', '1']
    b1phasecmd = ['fslroi', str(b1map_file), str(appendposix(b1map_file, '_phase')), '2', '1']
    b1totarget_antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(replacesuffix(b1map_file, '_mag.nii.gz')), '-f',
                str(target), '-o', str(appendposix(reg_dir/b1map_file.name, '_mag_'+reg_dir_name+'_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    results = ()
    with WorkingContext(str(reg_dir)):
        results += run_subprocess(b1magcmd)
        results += run_subprocess(b1phasecmd)
        results += run_subprocess(b1totarget_antscmd)
        mov = replacesuffix(b1map_file, '_phase.nii.gz')
        ref = target
        outf = replacesuffix(b1map_file, '_phase_'+reg_dir_name+'.nii.gz')
        warpf = [str(replacesuffix(b1map_file, '_mag_'+reg_dir_name+'_1Warp.nii.gz'))]
        affine_xform = [str(replacesuffix(b1map_file, '_mag_'+reg_dir_name+'_0GenericAffine.mat'))]
        results += subj2templ_applywarp(str(mov), str(ref), str(outf), warpf, str(reg_dir), affine_xform=affine_xform)
        phase_data = nib.load(str(outf)).get_data().astype('float32')
        phase_data_mf = medianf(phase_data, size=7)
        savenii(phase_data_mf, nib.load(str(outf)).affine,
                str(replacesuffix(b1map_file, '_phase_'+reg_dir_name+'_mf.nii.gz')))
        prov.log(str(replacesuffix(b1map_file, '_phase_'+reg_dir_name+'_mf.nii.gz')),
                 'median filtered b1 phase map '+reg_dir_name, str(b1map_file), script=__file__,
                 provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})

    with WorkingContext(str(target.parent)):
        results += run_subprocess(['fslmaths', target, '-div', str(appendposix(b1map_file, '_phase_'+reg_dir_name+'_mf.nii.gz')),
                                   '-mul 100', str(replacesuffix(target, '_b1corr.nii.gz'))])
        prov.log(str(replacesuffix(target, '_b1corr.nii.gz')),
                 'median filtered b1 phase map correction', str(target), script=__file__,
                 provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})
    return results
