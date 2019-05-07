# half baked untested bbc freesurf script
import os, copy
from pathlib import *
import datetime
import mne, json
from mmimproc.projects.bbc.pairing import vbm_fnames, project
from mmimproc.utils.paths import getnetworkdataroot
from mmimproc.utils import run_subprocess, WorkingContext, appendposix
#set up provenance
from mmimproc.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
#setup paths and file names to process
fs = mmimproc.fs
# number of cores to use
mp = 20

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
    fs_sid = vbmf+'_freesurf'
    results = ()
    with WorkingContext(str(subjects_dir)):
        results += run_subprocess(['recon-all', '-openmp', '%.0f' % mp, '-subjid', fs_sid, '-i', str(vbm_fname), '-all'], env=curr_env)
        with open(fs_sid+'/'+fs_sid+'_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now()), mode='a') as logr:
            json.dump(results, logr, indent=2)
    fs_subj_ln = fs/project/'freesurf_subjs'/fs_sid
    if not fs_subj_ln.is_symlink():
        fs_subj_ln.symlink_to(subjects_dir/fs_sid, target_is_directory=True)
