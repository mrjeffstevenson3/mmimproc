import pylabs
pylabs.datadir.target = 'jaba'
pylabs.opts.nii_ftype = 'NIFTI_GZ'
pylabs.opts.nii_fext = '.nii.gz'
pylabs.opts.fslmultifilequit = 'FALSE'
pylabs.opts.overwrite = True
thresh = pylabs.opts.spm_seg_thr
from pathlib import *
from multiprocessing import Pool
import numpy as np
import nibabel as nib
import nipype, os
from dipy.segment.mask import applymask
from scipy.ndimage.morphology import binary_erosion as ero
from scipy.ndimage.filters import median_filter as medianf
from pylabs.utils import getnetworkdataroot, get_antsregsyn_cmd
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.io.images import savenii
from pylabs.utils.paths import RootDataDir
from pylabs.projects.genz.file_names import project, SubjIdPicks, get_5spgr_names
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())

if os.environ['FSLOUTPUTTYPE'] != 'NIFTI_GZ':
    os.environ['FSLOUTPUTTYPE'] = 'NIFTI_GZ'

antsRegistrationSyNQuick = get_antsregsyn_cmd(quick=True)
antsWarpMultitransform = get_antsregsyn_cmd(warps=True)
ext = pylabs.opts.nii_fext

async = False
pool = Pool(20)
# testing


# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of dicts with subject ids, session, scan info to operate on
picks = [
         {'subj': 'sub-genz996', 'session': 'ses-1', 'run': '1',},
         #{'subj': 'sub-genz996', 'session': 'ses-2', 'run': '1',},
         #{'subj': 'sub-genz997', 'session': 'ses-1', 'run': '1'},
         #{'subj': 'sub-genz997', 'session': 'ses-2', 'run': '1',}
         ]

setattr(subjids_picks, 'subjids', picks)

flip5 = True
overwrite = True
reg_dir_name = 'b1spgr2spgr30'

b1map_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames = get_5spgr_names(subjids_picks)
assert len(b1map_fnames) == len(spgr5_fa5_fnames) == len(spgr5_fa10_fnames) == len(spgr5_fa15_fnames) == len(spgr5_fa20_fnames) == len(spgr5_fa30_fnames)

TR = float(spgr5_fa5_fnames[0].split('_')[3].split('-')[-1].replace('p','.'))
results = ()

# # for testing purposes. comment out to run full loop.
# i = 3
# b1map, spgr05, spgr10, spgr15, spgr20, spgr30 = b1map_fnames[i], spgr5_fa5_fnames[i], spgr5_fa10_fnames[i], spgr5_fa15_fnames[i], spgr5_fa20_fnames[i], spgr5_fa30_fnames[i]

for spgr05, spgr10, spgr15, spgr20, spgr30 in zip(spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames):
    spgr_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'qt1'
    for spgr in [spgr05, spgr10, spgr15, spgr20, spgr30]:
        thrcmd = ['fslmaths '+ str(spgr_dir/str(spgr+'.nii'))+ ' -thr 2000 '+ str(appendposix(spgr_dir/spgr, '_thr2000'+ext))]
        results += run_subprocess(thrcmd)

for b1map, spgr05, spgr10, spgr15, spgr20, spgr30 in zip(b1map_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames):

    b1map_dir = fs/project/b1map.split('_')[0] / b1map.split('_')[1] / 'fmap'
    spgr_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'qt1'
    reg_dir = fs/project/spgr30.split('_')[0] / spgr30.split('_')[1] / 'reg' / reg_dir_name
    ref = spgr_dir/str(appendposix(spgr_dir/spgr30, '_thr2000'+ext))
    if not reg_dir.is_dir():
        reg_dir.mkdir(parents=True)
    if not (b1map_dir/str(b1map+'_mag'+ext)).is_file():
        b1magcmd = ['fslroi '+str(b1map_dir/str(b1map+'.nii'))+' '+str(replacesuffix(b1map_dir/b1map, '_mag'+ext))+' 0 1']
        results += run_subprocess(b1magcmd)
    b1regcmd = [str(antsRegistrationSyNQuick)+' -d 3 -m '+str(replacesuffix(b1map_dir/b1map, '_mag'+ext))+' -f '+
                str(ref)+' -o '+str(replacesuffix(reg_dir/b1map, '_mag_'+reg_dir_name+'_'))+' -n 30 -t s -p f -j 1 -s 10 -r 1']
    # reg b1mag to spgr30
    results += run_subprocess(b1regcmd)
    if not (b1map_dir/str(b1map+'_phase'+ext)).is_file():
        b1phasecmd = ['fslroi '+str(b1map_dir/str(b1map+'.nii'))+' '+str(replacesuffix(b1map_dir/b1map, '_phase'+ext))+' 2 1']
        results += run_subprocess(b1phasecmd)
    mov = replacesuffix(b1map_dir/b1map, '_phase'+ext)
    outf = replacesuffix(reg_dir/b1map, '_phase_' + reg_dir_name + ext)
    # need to point to reg dir
    warpf = [str(replacesuffix(reg_dir/b1map, '_mag_'+reg_dir_name+ '_1Warp.nii.gz'))]
    affine_xform = [str(replacesuffix(reg_dir/b1map, '_mag_'+reg_dir_name+ '_0GenericAffine.mat'))]
    # apply warps to b1 phase and mov to spgr30 space
    results += subj2templ_applywarp(str(mov), str(ref), str(outf), warpf, str(reg_dir), affine_xform=affine_xform)
    # filter and smooth phase
    phase_data = nib.load(str(outf)).get_data().astype('float32')
    phase_data_mf = medianf(phase_data, size=7)
    savenii(phase_data_mf, nib.load(str(outf)).affine,
            str(replacesuffix(reg_dir / b1map, '_phase_' + reg_dir_name + '_mf'+ext)))
    b1map_reg_ln = spgr_dir / str(b1map+ '_phase_' + reg_dir_name + '_mf'+ext)
    if not b1map_reg_ln.is_symlink():
        b1map_reg_ln.symlink_to(replacesuffix(reg_dir / b1map, '_phase_' + reg_dir_name + '_mf'+ext), target_is_directory=True)
    prov.log(str(spgr_dir / str(b1map+ '_phase_' + reg_dir_name + '_mf'+ext)),
             'median filtered b1 phase map ' + reg_dir_name, str(b1map_dir/str(b1map+'.nii')), #script=__file__,
             provenance={'filter': 'numpy median filter', 'filter size': '7', 'results': results})
    files = []
    for spgr in [spgr05, spgr10, spgr15, spgr20]:
        spgrregcmd = [str(antsRegistrationSyNQuick)+' -d 3 -m '+str(spgr_dir/spgr)+'_thr2000'+ext+' -f '+str(ref)+' -o '
                      +str(reg_dir / str(spgr+'_thr2000_' + reg_dir_name + '_'))+' -n 30 -t s -p f -j 1 -s 10 -r 1']
        results += run_subprocess(spgrregcmd)
        spgr_reg_ln = spgr_dir / str(spgr+'_thr2000_' + reg_dir_name + ext)
        if not spgr_reg_ln.is_symlink():
            spgr_reg_ln.symlink_to(reg_dir / str(spgr+'_thr2000_' + reg_dir_name + '_Warped'+ext), target_is_directory=True)
        files.append(str(spgr_reg_ln))
        prov.log(str(spgr_dir / str(spgr+'_thr2000_' + reg_dir_name + ext)),
             'spgr reg 2 flip 30 befor fits in ' + reg_dir_name, str(spgr_dir / str(spgr+'_thr2000'+ext)), #script=__file__,
             provenance={ 'results': results})
    files.append(str(ref))
    maskfile = appendposix(ref, '_mask')
    results += run_subprocess(['fslmaths '+str(ref)+' -bin -fillh '+str(maskfile)])
    b1file = b1map_reg_ln
    subject = spgr05.split('_')[0]
    ses = spgr05.split('_')[1]

    X = []
    if flip5:
        for a in [spgr05, spgr10, spgr15, spgr20, spgr30]:
            X.append(int(a.split('_')[3].split('-')[1]))
            outfile = str(spgr_dir / '{sub}_{ses}_qT1_b1corr_5flip.nii.gz'.format(sub=subject, ses=ses))

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
        prov.log(str(appendposix(kwargs['t1filename'], '_clamped')), 'clamping qT1 fit', kwargs['t1filename'], #script=__file__,
                 provenance=dict(**kwargs))
    except Exception as ex:
        print('\n--> Error during fitting: ', ex)

