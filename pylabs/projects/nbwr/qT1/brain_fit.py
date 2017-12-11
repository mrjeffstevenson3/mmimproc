from pathlib import *
from multiprocessing import Pool
import numpy as np
import nibabel as nib
import nipype, os
import nipype.interfaces.fsl as fsl
from dipy.segment.mask import applymask
from scipy.ndimage.morphology import binary_erosion as ero
from scipy.ndimage.filters import median_filter as medianf
from pylabs.utils.paths import getnetworkdataroot, get_antsregsyn_cmd
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.io.images import savenii
from pylabs.utils.paths import RootDataDir
from pylabs.projects.nbwr.file_names import project, SubjIdPicks, get_5spgr_names
# from pylabs.projects.nbwr.file_names import spgr5_fa5_fnames,spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames, b1map5_fnames
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

from pylabs.utils.paths import RootDataDir
datadir = RootDataDir()
setattr(datadir, 'target', 'jaba')

fs = Path(getnetworkdataroot(datadir))

if os.environ['FSLOUTPUTTYPE'] != 'NIFTI_GZ':
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'

flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ >= '0.12.0':
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')

antsRegistrationSyN = get_antsregsyn_cmd()
async = False
pool = Pool(20)
# testing
# picks = [-1]
# for p in picks:
#
#     b1map_fnames, spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames = [b1map_fnames[picks]], [spgr_fa5_fnames[picks]], [spgr_fa15_fnames[picks]], [spgr_fa30_fnames[picks]]
# picks5 = -1
# b1map5_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr_fa15_fnames, \
#     spgr5_fa20_fnames, spgr_fa30_fnames = [b1map5_fnames[picks5]], [spgr5_fa5_fnames[picks5]], [spgr5_fa10_fnames[picks5]], \
#                                         [spgr_fa15_fnames[picks5]], [spgr5_fa20_fnames[picks5]], [spgr_fa30_fnames[picks5]]

subjids_picks = SubjIdPicks()
flip5 = True
overwrite = False
picks = ['136',]

setattr(subjids_picks, 'subjids', picks)

if flip5:
    b1map_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames = get_5spgr_names(subjids_picks)
    assert len(b1map_fnames) == len(spgr5_fa5_fnames) == len(spgr5_fa10_fnames) == len(spgr5_fa15_fnames) == len(spgr5_fa20_fnames) == len(spgr5_fa30_fnames)
    spgrs = [spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames]
else:
    b1map_fnames, spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames = get_3spgr_names(subjids_picks)
    assert len(b1map_fnames) == len(spgr_fa5_fnames) == len(spgr_fa15_fnames) == len(spgr_fa30_fnames)
    spgrs = [spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames]

TR = float(spgr_fa5_fnames[0].split('_')[3].split('-')[-1].replace('p','.'))

#for b1map, spgr05, spgr15, spgr30 in zip(b1map_fnames, spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames):
for b1map, spgr05, spgr10, spgr15, spgr20, spgr30 in zip(b1map5_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames):
    b1map_dir = fs/project/b1map.split('_')[0] / b1map.split('_')[1] / 'fmap'
    spgr_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'qt1'
    b1magcmd = ['fslroi', str(b1map_dir/b1map), str(appendposix(b1map_dir/b1map, '_mag')), '0', '1']
    b1phasecmd = ['fslroi', str(b1map_dir/b1map), str(appendposix(b1map_dir/b1map, '_phase')), '2', '1']
    b1tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(appendposix(b1map_dir/b1map, '_mag.nii.gz')), '-f',
                str(spgr_dir/str(spgr30+'.nii')), '-o', str(appendposix(b1map_dir/b1map, '_mag_reg2spgr30_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    spgr05tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(spgr_dir/str(spgr05+'.nii')), '-f',
                str(spgr_dir/str(spgr30+'.nii')), '-o', str(spgr_dir/str(spgr05 + '_reg2spgr30_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    spgr15tospgr30antscmd = [ str(antsRegistrationSyN), '-d 3 -m', str(spgr_dir/str(spgr15+'.nii')), '-f',
                str(spgr_dir/str(spgr30+'.nii')), '-o', str(spgr_dir/str(spgr15 + '_reg2spgr30_')),
                '-n 30 -t s -p f -j 1 -s 10 -r 1']
    if flip5:
        spgr10tospgr30antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(spgr_dir / str(spgr10 + '.nii')), '-f',
                                 str(spgr_dir / str(spgr30 + '.nii')), '-o',
                                 str(spgr_dir / str(spgr10 + '_reg2spgr30_')),
                                 '-n 30 -t s -p f -j 1 -s 10 -r 1']
        spgr20tospgr30antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(spgr_dir / str(spgr20 + '.nii')), '-f',
                                 str(spgr_dir / str(spgr30 + '.nii')), '-o',
                                 str(spgr_dir / str(spgr20 + '_reg2spgr30_')),
                                 '-n 30 -t s -p f -j 1 -s 10 -r 1']
        #spgr20tospgr30antscmd = ' '.join(spgr15tospgr30antscmd)
    results = ()
    # make b1 corr function
    if overwrite or not Path(appendposix(b1map_dir / b1map, '_phase_reg2spgr30_mf.nii.gz')).is_file():
        with WorkingContext(str(b1map_dir)):
            results += run_subprocess(b1magcmd)
            results += run_subprocess(b1phasecmd)
            results += run_subprocess(b1tospgr30antscmd)
            mov = appendposix(b1map_dir/b1map, '_phase.nii.gz')
            ref = spgr_dir/str(spgr30+'.nii')
            outf = appendposix(b1map_dir/b1map, '_phase_reg2spgr30.nii.gz')
            warpf = [str(appendposix(b1map_dir/b1map, '_mag_reg2spgr30_1Warp.nii.gz'))]
            affine_xform = [str(replacesuffix(b1map_dir/b1map, '_mag_reg2spgr30_0GenericAffine.mat'))]
            execwd = b1map_dir
            subj2templ_applywarp(str(mov), str(ref), str(outf), warpf, str(execwd), affine_xform=affine_xform)
            phase_data = nib.load(str(outf)).get_data().astype('float32')
            phase_data_mf = medianf(phase_data, size=7)
            savenii(phase_data_mf, nib.load(str(outf)).affine, str(appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf.nii.gz')))
            prov.log(str(appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf.nii.gz')), 'median filtered b1 phase map reg to spgr 30', str(b1map_dir/b1map)+'.nii', script=__file__,
                     provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})

    with WorkingContext(str(spgr_dir)):
        if overwrite or not (spgr_dir/str(spgr05 + '_reg2spgr30_Warped.nii.gz')).is_file():
            results += run_subprocess(spgr05tospgr30antscmd)
            extract_brain(spgr_dir / str(spgr05 + '_reg2spgr30_Warped.nii.gz'))
        if overwrite or not (spgr_dir / str(spgr15 + '_reg2spgr30_Warped.nii.gz')).is_file():
            results += run_subprocess(spgr15tospgr30antscmd)
        if flip5:
            if overwrite or not (spgr_dir / str(spgr10 + '_reg2spgr30_Warped.nii.gz')).is_file():
                results += run_subprocess(spgr10tospgr30antscmd)
            if overwrite or not (spgr_dir / str(spgr20 + '_reg2spgr30_Warped.nii.gz')).is_file():
                results += run_subprocess(spgr20tospgr30antscmd)

        maskfile = spgr_dir/str(spgr05 + '_reg2spgr30_Warped_brain_mask.nii.gz')

        if flip5:
            for f in [appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf.nii.gz'), spgr_dir/str(spgr15 + '_reg2spgr30_Warped.nii.gz'), spgr_dir/str(spgr30+'.nii')]:
                results += run_subprocess(['fslmaths', str(f), '-mas', str(maskfile), str(appendposix(f, '_brain'))])


        rootdir = str(fs/project)
        if flip5:
            files = [str(spgr_dir/str(spgr05 + '_reg2spgr30_Warped_brain.nii.gz')),
                     str(spgr_dir / str(spgr10 + '_reg2spgr30_Warped_brain.nii.gz')),
                 str(spgr_dir/str(spgr15 + '_reg2spgr30_Warped_brain.nii.gz')),
                     str(spgr_dir / str(spgr20 + '_reg2spgr30_Warped_brain.nii.gz')),
                 str(spgr_dir/str(spgr30+'_brain.nii.gz'))]
        else:
            files = [str(spgr_dir/str(spgr05 + '_reg2spgr30_Warped_brain.nii.gz')),
                 str(spgr_dir/str(spgr15 + '_reg2spgr30_Warped_brain.nii.gz')),
                 str(spgr_dir/str(spgr30+'_brain.nii.gz'))]

        subject = spgr05.split('_')[0]
        ses = spgr05.split('_')[1]
        b1file = appendposix(b1map_dir/b1map, '_phase_reg2spgr30_mf_brain.nii.gz')
        X = []
        if flip5:
            for a in [spgr05, spgr10, spgr15, spgr20, spgr30]:
                X.append(int(a.split('_')[3].split('-')[1]))
                outfile = str(spgr_dir / '{sub}_{ses}_qT1_b1corr_5flip.nii.gz'.format(sub=subject, ses=ses))
        else:
            for a in [spgr05, spgr15, spgr30]:
                X.append(int(a.split('_')[3].split('-')[1]))
                outfile = str(spgr_dir/ '{sub}_{ses}_qT1_b1corr_3flip.nii.gz'.format(sub=subject, ses=ses))
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
                kwargs['clamp'] = '1 to 6000'
                kwargs['erosion structure'] = (2,2,2)
                kwargs['flips'] = X
                kwargs['files'] = files
                qt1_data = nib.load(kwargs['t1filename']).get_data()
                mask_data = nib.load(kwargs['maskfile']).get_data().astype(int)
                qt1_data[qt1_data < 1] = 0
                qt1_data[qt1_data > 6000] = 6000
                mask_data = ero(mask_data, structure=np.ones((2,2,2))).astype(mask_data.dtype)
                qt1_clamped = applymask(qt1_data, mask_data)
                savenii(qt1_clamped, nib.load(kwargs['t1filename']).affine, str(appendposix(kwargs['t1filename'], '_clamped')))
                prov.log(str(appendposix(kwargs['t1filename'], '_clamped')), 'clamping qT1 fit', kwargs['t1filename'],
                         script=__file__, provenance=dict(**kwargs))
            except Exception as ex:
                print('\n--> Error during fitting: ', ex)

