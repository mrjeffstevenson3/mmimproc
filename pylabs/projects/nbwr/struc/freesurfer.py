# half baked untested nbwr freesurf script
import pylabs
import os, copy
from pathlib import *
import datetime
import mne, json
from pylabs.projects.nbwr.file_names import project, SubjIdPicks, get_freesurf_names
from pylabs.utils.paths import getnetworkdataroot, get_antsregsyn_cmd
from pylabs.fmap_correction.b1_map_corr import correct4b1
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix
from mne.utils import run_subprocess as mne_subprocess
#set up provenance
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()
#setup paths and file names to process

pylabs.datadir.target = 'scotty'
fs = Path(getnetworkdataroot())

antsRegistrationSyN = get_antsregsyn_cmd()

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = ['007'] #, '088', '107', '110', '135', '226', '307', '309',]

setattr(subjids_picks, 'subjids', picks)


# string defining reg directory and appended to file name
reg_dir_name = 'b1map2fsrms'
overwrite = True
hires = True
b1corr = True
noise_filter = True
noise_thresh = -1
noise_kernel = 1
meg_source_spacing = 5
bem_from = 'T1' # or 'brain' if probs with overlapping boundaries

b1map_fnames, freesurf_fnames = get_freesurf_names(subjids_picks)

if 'FREESURFER_HOME' not in os.environ:
    raise RuntimeError('FreeSurfer environment not set up. Pls fix.')

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
    rms_fname = subjects_dir / 'anat' /str(fsf+'.nii')
    fs_fname = fsf

    if not rms_fname.is_file():
        raise ValueError('Cannot find rms file '+str(fsf))
    if overwrite and b1corr:
        results += ('starting b1 correction at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()),)
        results += correct4b1(project, subject, session, b1map_file, rms_fname, reg_dir_name)
        results += ('finished b1 correction at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()),)
        fs_fname += '_b1corr'
    elif not overwrite and b1corr:
        fs_fname += '_b1corr'
    if overwrite and noise_filter:
        with WorkingContext(str(subjects_dir / 'anat')):
            results += ('starting susan noise filtering at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()),)
            results += run_subprocess(['susan '+str(replacesuffix(fs_fname, '.nii.gz'))+' '+str(noise_thresh)+' '+str(noise_kernel)+' 3 1 0 '+str(replacesuffix(fs_fname, '_susanf.nii.gz'))])
            fs_fname += '_susanf'
            results += ('finished susan noise filtering at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()),)
            prov.log(str(replacesuffix(fs_fname, '.nii.gz')), 'fs mempr rms with susan noise filtering', str(rms_fname), script=__file__,
                     provenance={'filter': 'susan noise filter', 'filter size': '1mm', 'noise level': 'auto', 'results': results})
    elif not overwrite and noise_filter:
        fs_fname += '_susanf'
    fs_sid = fsf+'_freesurf'

    with WorkingContext(str(subjects_dir)):
        if overwrite:
            if hires:
                fs_sid += '_hires'
                with open('freesurf_expert_opts.txt', mode='w') as optsf:
                    optsf.write('mris_inflate -n 15\n')
                print('starting hi resolution freesurfer run for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()))
                results += ('starting hi resolution freesurfer run for '+fs_sid+' at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()),)
                results += run_subprocess(['recon-all -hires -all -subjid '+fs_sid+' -i '+str(subjects_dir / 'anat'/ appendposix(fs_fname, '.nii.gz'))+' -expert freesurf_expert_opts.txt -parallel -openmp 8'])
                print('hi resolution freesurfer run finished for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()))
                results += ('hi resolution freesurfer run finished for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(
                    datetime.datetime.now()),)
            else:
                print('starting 1mm3 freesurfer run for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()))
                results += ('starting 1mm3 freesurfer run for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()),)
                results += run_subprocess(['recon-all -all -subjid '+fs_sid+' -i '+str(subjects_dir / 'anat'/ appendposix(fs_fname, '.nii.gz'))+' -parallel -openmp 8'])
                results += ('finished 1mm3 freesurfer run for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(
                    datetime.datetime.now()),)
                print('finished 1mm3 freesurfer run for ' + fs_sid + ' at {:%H:%M on %M %d %Y}.'.format(datetime.datetime.now()))
        if not overwrite and hires:
            fs_sid += '_hires'
        results += mne_subprocess(['mne_setup_mri', '--mri', bem_from, '--subject', fs_sid, '--overwrite'], env=curr_env)
        results += mne_subprocess(['mne', 'watershed_bem', '--subject', fs_sid, '--overwrite'], env=curr_env)
        results += mne_subprocess(['mne_setup_source_space', '--subject', fs_sid, '--spacing', '%.0f' % meg_source_spacing, '--cps'], env=curr_env)
        with open(fs_sid+'/'+fs_sid+'_log{:%Y%m%d%H%M}.json'.format(datetime.datetime.now()), mode='a') as logr:
            json.dump(results, logr, indent=2)
    fs_subj_ln = fs/project/'freesurf_subjs'/fs_sid
    if not fs_subj_ln.is_symlink():
        fs_subj_ln.symlink_to(subjects_dir/fs_sid, target_is_directory=True)

