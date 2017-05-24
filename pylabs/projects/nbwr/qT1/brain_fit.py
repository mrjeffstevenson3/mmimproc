from pathlib import *
from multiprocessing import Pool
import numpy as np
import nibabel as nib
import nipype, os
import nipype.interfaces.fsl as fsl
from dipy.segment.mask import applymask
from scipy.ndimage.morphology import binary_erosion as ero
from scipy.ndimage.filters import median_filter as medianf
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext, appendposix
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.io.images import savenii
from pylabs.projects.nbwr.file_names import project, spgr_fa5_fname, spgr_fa15_fname, spgr_fa30_fname, b1map_fname
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
if os.environ['FSLOUTPUTTYPE'] == 'NIFTI':
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'

flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ >= '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')

if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
else:
    antsRegistrationSyN = Path(os.environ.get('ANTSPATH') , 'antsRegistrationSyN.sh')

async = False
TR = float(spgr_fa5_fname[0].split('_')[3].split('-')[-1].replace('p','.'))
pool = Pool(20)
# testing
b1map, spgr05, spgr15, spgr30 = b1map_fname[0], spgr_fa5_fname[0], spgr_fa15_fname[0], spgr_fa30_fname[0]


for b1map, spgr05, spgr15, spgr30 in zip(b1map_fname, spgr_fa5_fname, spgr_fa15_fname, spgr_fa30_fname):
    b1map_dir = fs/project/b1map.split('_')[0] / b1map.split('_')[1] / 'fmap'
    spgr_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'qt1'
    b1magcmd = ' '.join(['fslroi', str(b1map_dir/b1map), str(appendposix(b1map_dir/b1map, '_mag')), '0', '1'])
    b1phasecmd = ' '.join(['fslroi', str(b1map_dir/b1map), str(appendposix(b1map_dir/b1map, '_phase')), '2', '1'])
    b1tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(appendposix(b1map_dir/b1map, '_mag.nii.gz')), '-f',
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
        mov = appendposix(b1map_dir/b1map, '_phase.nii.gz')
        ref = spgr_dir/str(spgr30+'.nii')
        outf = appendposix(b1map_dir/b1map, '_phase_reg2spgr30.nii.gz')
        warpf = [str(appendposix(b1map_dir/b1map, '_mag_reg2spgr30_1Warp.nii.gz'))]
        affine_xform = [str(appendposix(b1map_dir/b1map, '_mag_reg2spgr30_0GenericAffine.mat'))]
        execwd = b1map_dir
        subj2templ_applywarp(str(mov), str(ref), str(outf), warpf, str(execwd), affine_xform=affine_xform)
        phase_data = nib.load(str(outf)).get_data().astype('float32')
        phase_data_mf = medianf(phase_data, size=7)
        affine = nib.load(str(outf)).affine
        phase_data_mf_img = nib.Nifti1Image(phase_data_mf, affine, nib.load(str(outf)).header)
        phase_data_mf_img.header.set_qform(affine, code=1)
        phase_data_mf_img.header.set_sform(affine, code=1)
        nib.save(phase_data_mf_img, str(appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf.nii.gz')))
        prov.log(str(appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf.nii.gz')), 'median filtered b1 phase map reg to spgr 30', str(b1map_dir/b1map)+'.nii', script=__file__,
                 provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})

    with WorkingContext(str(spgr_dir)):
        results += run_subprocess(spgr05tospgr30antscmd)
        results += run_subprocess(spgr15tospgr30antscmd)
        extract_brain(spgr_dir/str(spgr05 + '_reg2spgr30_Warped.nii.gz'))
        maskfile = spgr_dir/str(spgr05 + '_reg2spgr30_Warped_brain_mask.nii.gz')

        for f in [appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf.nii.gz'), spgr_dir/str(spgr15 + '_reg2spgr30_Warped.nii.gz'), spgr_dir/str(spgr30+'.nii')]:
            mask_cmd = ['fslmaths', str(f), '-mas', str(maskfile), str(appendposix(f, '_brain'))]
            results += run_subprocess(' '.join(mask_cmd))

        rootdir = str(fs/project)
        files = [str(spgr_dir/str(spgr05 + '_reg2spgr30_Warped_brain.nii.gz')),
                 str(spgr_dir/str(spgr15 + '_reg2spgr30_Warped_brain.nii.gz')),
                 str(spgr_dir/str(spgr30+'_brain.nii.gz'))]
        subject = spgr05.split('_')[0]
        ses = spgr05.split('_')[1]
        b1file = appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf_brain.nii.gz')
        X = []
        for a in [spgr05, spgr15, spgr30]:
            X.append(int(a.split('_')[3].split('-')[1]))
        outfile = str(spgr_dir/ '{sub}_{ses}_qT1_b1corr.nii.gz'.format(sub=subject, ses=ses))
        print(files)
        print(b1file)
        kwargs = {}
        kwargs['scantype'] = spgr05.split('_')[2].upper()
        kwargs['TR'] = TR
        kwargs['t1filename'] = outfile
        if b1file.is_file():
            kwargs['b1file'] = str(b1file)
        else:
            print('No B1 file for subject {0}'.format(subject))
        if maskfile.is_file():
            kwargs['maskfile'] = str(maskfile)
        if async:
            kwargs['mute'] = True
            pool.apply_async(t1fit, [files, X], kwargs)
        else:
            try:
                t1fit(files, X, **kwargs)
                qt1_data = nib.load(kwargs['t1filename']).get_data()
                mask_data = nib.load(kwargs['maskfile']).get_data().astype(int)
                qt1_data[qt1_data < 1] = 0
                qt1_data[qt1_data > 6000] = 6000
                mask_data = ero(mask_data, structure=np.ones((2,2,2))).astype(mask_data.dtype)
                qt1_clamped = applymask(qt1_data, mask_data)
                qt1_clamped_img = nib.Nifti1Image(qt1_clamped, nib.load(kwargs['t1filename']).affine)
                qt1_clamped_img.header.set_qform(nib.load(kwargs['t1filename']).affine, code=1)
                qt1_clamped_img.header.set_sform(nib.load(kwargs['t1filename']).affine, code=1)
                nib.save(qt1_clamped_img, str(appendposix(kwargs['t1filename'], '_clamped')))
                kwargs['clamp'] = '1 to 6000'
                kwargs['erosion'] = (2,2,2)
                kwargs['flips'] = X
                prov.log(str(appendposix(kwargs['t1filename'], '_clamped')), 'clamping qT1 fit', kwargs['t1filename'],
                         script=__file__, provenance=dict(**kwargs))
            except Exception as ex:
                print('\n--> Error during fitting: ', ex)

