# half baked untested bbc freesurf script
import os, copy
from pathlib import *
import datetime
import mne, json
from pylabs.projects.nbwr.file_names import project, vbm_fnames
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext, appendposix
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = Path(getnetworkdataroot())
# number of cores to use
mp = 20
hires = True
b1corr = True
noise_filter = True

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

for vbmf in vbm_fnames:
    subject = vbmf.split('_')[0]
    session = vbmf.split('_')[1]
    subjects_dir = fs/project/subject/session
    mne.set_config('SUBJECTS_DIR', str(subjects_dir))
    curr_env = copy.copy(os.environ)
    vbmdir = subjects_dir / 'anat'
    vbm_fname = vbmdir/appendposix(vbmf, '.nii')  # no rms on this protocol
    if b1corr:
        ## b1corr function here

    if noise_filter:
        ## add susan filter function here

    fs_sid = vbmf+'_freesurf'
    results = ()
    with WorkingContext(str(subjects_dir)):
        if hires:
            fs_sid += '_hires'
            with open('freesurf_expert_opts.txt', mode='w') as optsf:
                optsf.write('mris_inflate -n 15\n')
            results += run_subprocess(['recon-all', '-openmp', '%.0f' % mp, '-hires', '-subjid', fs_sid, '-i', str(vbm_fname), '-all', '-expert', 'freesurf_expert_opts.txt'], env=curr_env)
        else:
            results += run_subprocess(['recon-all', '-openmp', '%.0f' % mp, '-subjid', fs_sid, '-i', str(vbm_fname), '-all'], env=curr_env)
        with open(fs_sid+'/'+fs_sid+'_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now()), mode='a') as logr:
            json.dump(results, logr, indent=2)
    fs_subj_ln = fs/project/'freesurf_subjs'/fs_sid
    if not fs_subj_ln.is_symlink():
        fs_subj_ln.symlink_to(subjects_dir/fs_sid, target_is_directory=True)
