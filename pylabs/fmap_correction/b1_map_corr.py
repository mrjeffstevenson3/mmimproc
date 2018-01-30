# -*- coding: utf-8 -*-
# wip b1 map correction functions used in fs, qT1, vbm, mrs
from pathlib import *
import os
import nibabel as nib
import numpy as np
from scipy.ndimage.filters import median_filter as medianf
from pylabs.io.images import savenii
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix, getnetworkdataroot
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
    b1magcmd = ['fslroi '+str(b1map_file)+' '+str(replacesuffix(b1map_file, '_mag.nii.gz'))+' 0 1']
    b1phasecmd = ['fslroi '+str(b1map_file)+' '+str(replacesuffix(b1map_file, '_phase.nii.gz'))+' 2 1']
    b1totarget_antscmd = [str(antsRegistrationSyN)+' -d 3 -m '+str(replacesuffix(b1map_file, '_mag.nii.gz'))+' -f '+
                str(target)+' -o '+str(replacesuffix(reg_dir/b1map_file.name, '_mag_'+reg_dir_name+'_'))+' -n 30 -t s -p f -j 1 -s 10 -r 1']
    results = ()
    with WorkingContext(str(reg_dir)):
        results += run_subprocess(b1magcmd)
        results += run_subprocess(b1phasecmd)
        results += run_subprocess(b1totarget_antscmd)
        mov = replacesuffix(b1map_file, '_phase.nii.gz')
        ref = target
        outf = replacesuffix(b1map_file.name, '_phase_'+reg_dir_name+'.nii.gz')
        # need to point to reg dir
        warpf = [str(replacesuffix(b1map_file.name, '_mag_'+reg_dir_name+'_1Warp.nii.gz'))]
        affine_xform = [str(replacesuffix(b1map_file.name, '_mag_'+reg_dir_name+'_0GenericAffine.mat'))]
        results += subj2templ_applywarp(str(mov), str(ref), str(outf), warpf, str(reg_dir), affine_xform=affine_xform)
        phase_data = nib.load(str(outf)).get_data().astype('float32')
        phase_data_mf = medianf(phase_data, size=7)
        savenii(phase_data_mf, nib.load(str(outf)).affine,
                str(replacesuffix(reg_dir/b1map_file.name, '_phase_'+reg_dir_name+'_mf.nii.gz')))
        b1map_reg_ln = fs / project / subject / session / 'fmap' / str(replacesuffix(b1map_file.name, '_phase_'+reg_dir_name+'_mf.nii.gz'))
        if not b1map_reg_ln.is_symlink():
            b1map_reg_ln.symlink_to(replacesuffix(reg_dir/b1map_file.name, '_phase_'+reg_dir_name+'_mf.nii.gz'), target_is_directory=True)
        prov.log(str(replacesuffix(reg_dir/b1map_file.name, '_phase_'+reg_dir_name+'_mf.nii.gz')),
                 'median filtered b1 phase map '+reg_dir_name, str(b1map_file), script=__file__,
                 provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})

    with WorkingContext(str(target.parent)):
        results += run_subprocess(['fslmaths '+str(target)+' -div '+str(appendposix(reg_dir/b1map_file.name, '_phase_'+reg_dir_name+'_mf.nii.gz'))+' -mul 100 '+str(replacesuffix(target, '_b1corr.nii.gz'))])
        prov.log(str(replacesuffix(target, '_b1corr.nii.gz')),
                 'median filtered b1 phase map correction', str(target), script=__file__,
                 provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})
    return results

def calcb1map(S1, S2, TRs, T1mean=1000.0, FAnom=60.0, medfilt=True, mfsize=9):
    """
    based on vasily Yarnykh's 2007 B1map method. ref: Magnetic Resonance in Medicine 57:192–200 (2007)
    :param S1: b1map magnitude signal ndarray of 1st (shortest) TR1 . matches TRs[0]. can be scaled as fp or dv but must be same for both.
    :param S2: b1map magnitude signal ndarray of 2nd (offset) TR2. matches TRs[1]. same scaling as S1.
    :param TRs: list with values of 2 TRs in magnitude b1map. (TR2 = TR1 + offset). parrec TR list is correct
    :param T1mean: avg T1 of tissue. 1000ms for brain. should change for shorter T1 phantom vials.
    :param FAnom: the flip angle of the b1 map sequence. default=60ms
    :param medfilt: True/False filtering option
    :returns: the array of decimal offsets to flip angles in spgr eg 1.07234 is a 7.234% overflip error for any spgr flip angle scan

    """
    with np.errstate(divide='ignore'):
        # set 0s to nan's so no divide by 0
        S1[S1 == 0] = np.nan
        S2[S2 == 0] = np.nan
        r = S2 / S1
        # fix nan's
        nans_in_r = np.isnan(r)
        r[nans_in_r] = 0
        # calculate B1 correction
        E1 = np.exp(-TRs[0]/T1mean)
        E2 = np.exp(-TRs[1]/T1mean)
        C = (r - 1 - (E2 * r) + E1) / (E1 - (E2 * r) + (E1 * E2 * (r - 1)))
        FA = (np.arccos(C) * 180 / np.pi) / FAnom
        # clean up any nan's
        FA[FA == np.nan] = 0
    if medfilt:
        FA = medianf(FA, size=mfsize)
    return FA
