# half baked untested nbwr freesurf script
import os, copy
from pathlib import *
import datetime
import mne, json
from pylabs.projects.nbwr.file_names import project, freesurf_fnames, b1map_fnames
from pylabs.utils.paths import getnetworkdataroot
from pylabs.fmap_correction.b1_map_corr import correct4B1
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())
# number of cores to use
mp = 20
hires = True
b1corr = True
noise_filter = True
picks = -1

freesurf_fnames = [freesurf_fnames[picks]]
b1map_fnames = [b1map_fnames[picks]]

if len(freesurf_fnames) != len(b1map_fnames):
    raise ValueError('must have same number of b1maps as mempr rms')

if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
else:
    antsRegistrationSyN = Path(os.environ.get('ANTSPATH') , 'antsRegistrationSyN.sh')


if not (fs/project/'freesurf_subjs').is_dir():
    (fs / project / 'freesurf_subjs').mkdir(parents=True)

for fsf, b1map in zip(freesurf_fnames, b1map_fnames):
    results = ()
    subject = fsf.split('_')[0]
    session = fsf.split('_')[1]
    subjects_dir = fs/project/subject/session
    b1map_file = subjects_dir/'fmap'/str(b1map+'.nii')
    mne.set_config('SUBJECTS_DIR', str(subjects_dir))
    curr_env = copy.copy(os.environ)
    target = subjects_dir / 'anat' /str(fsf+'.nii')
    reg_dir_name = 'reg_b1map2fsrms'
    fs_fname = fsf

    if b1corr:
        results += correct4b1(project, subject, session, b1map_file, target, reg_dir_name)
        fs_fname += '_b1corr'
    if noise_filter:
        with WorkingContext(str(subjects_dir / 'anat')):
            results += run_subprocess(['susan', str(replacesuffix(target, '_b1corr.nii.gz')), '-1 1 3 1 0', str(replacesuffix(target, '_susan.nii.gz'))])
            fs_fname += '_susan'
    fs_sid = fsf+'_freesurf'

    with WorkingContext(str(subjects_dir)):
        if hires:
            fs_sid += '_hires'
            with open('freesurf_expert_opts.txt', mode='w') as optsf:
                optsf.write('mris_inflate -n 15\n')
            results += run_subprocess(['recon-all', '-openmp', '%.0f' % mp, '-hires', '-subjid', fs_sid, '-i', fs_fname+'.nii.gz', '-all', '-expert', 'freesurf_expert_opts.txt'], env=curr_env)
        else:
            results += run_subprocess(['recon-all', '-openmp', '%.0f' % mp, '-subjid', fs_sid, '-i', fs_fname+'.nii.gz', '-all'], env=curr_env)
        with open(fs_sid+'/'+fs_sid+'_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now()), mode='a') as logr:
            json.dump(results, logr, indent=2)
    fs_subj_ln = fs/project/'freesurf_subjs'/fs_sid
    if not fs_subj_ln.is_symlink():
        fs_subj_ln.symlink_to(subjects_dir/fs_sid, target_is_directory=True)
