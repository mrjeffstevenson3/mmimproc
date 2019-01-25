# -*- coding: utf-8 -*-
# Copyright (c) 2014, LABS^N
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import mnefun
import numpy as np
import score
from picks import fullChpiValidEpochs as pickedSubjects
nsubjects = len(pickedSubjects)


try:
    # Use niprov as handler for events if it's installed
    from niprov.mnefunsupport import handler
except ImportError:
    handler = None

params = mnefun.Params(tmin=-0.2, tmax=0.5, t_adjust=-4e-3,
                       n_jobs=6, n_jobs_mkl=1,
                       n_jobs_fir=4, n_jobs_resample=4,
                       decim=5, proj_sfreq=200, filter_length='5s')

#params.work_dir = '/home/jasper/data/bbc' 
params.work_dir = '/diskArray/data/bbc/meg' 
params.subjects = ['bbc_'+str(s) for s in pickedSubjects] 
params.structurals = [None]*nsubjects  # None means use sphere
params.dates = None  # Use "None" to more fully anonymize
params.score = score.score_words_tones  # Scoring function used to slice data into trials
params.subject_indices = np.arange(nsubjects)  # Define which subjects to run
params.plot_drop_logs = False  # Turn off so plots do not halt processing

# Set parameters for remotely connecting to acquisition computer
params.acq_ssh = 'jasper@minea.ilabs.uw.edu'
params.acq_dir = '/home/jasper/bbc'

# Set parameters for remotely connecting to SSS workstation ('sws')
params.sws_ssh = 'jasper@kasga.ilabs.uw.edu'
params.sws_dir = '/data06/jasper'

# Set the niprov handler to deal with events:
params.on_process = handler

params.run_names = ['%s']
params.get_projs_from = np.arange(1)
params.inv_names = ['%s']
params.inv_runs = [np.arange(1)]
params.runs_empty = [] #['%s_erm']  # Define empty room runs

# Define number of SSP projectors. Columns correspond to Grad/Mag/EEG chans
#params.ecg_channel='MEG1531'
params.proj_nums = [[0, 0, 0],  # ECG
                    [1, 1, 0],  # EOG
                    [0, 0, 0]]  # Continuous (from ERM)
params.cov_method = 'shrunk'  # Cleaner noise covariance regularization

# python | maxfilter for choosing SSS applied using either Maxfilter or MNE
params.sss_type = 'python'
params.sss_regularize = 'svd'
params.tsss_dur = 8.
params.int_order = 6
params.st_correlation = .9
params.trans_to = (0, 0, 0.03)
# The scoring function needs to produce an event file with these values
params.in_numbers = [60, 10, 11, 12, 30, 31, 32]
# Those values correspond to real categories as:
params.in_names = ['response', 'tone1', 'tone2cont', 'tone2match',
                                'word1', 'word2cont', 'word2match']

# Define how to translate the above event types into evoked files
params.analyses = [
    'All',
    'Resp_vs_Aud',
    'Each'
]
params.out_names = [
    ['All'],
    ['Resp','Aud'],
    params.in_names,
]
params.out_numbers = [
    [1, 1, 1, 1, 1, 1, 1], # Combine all trials
    [1, 2, 2, 2, 2, 2, 2], # responses vs. auditory stimuli
    [1, 2, 3, 4, 5, 6, 7],     # Leave events split the same way they were scored
]
params.must_match = [
    [],
    [],
    [],
]


# Set what processing steps will execute
mnefun.do_processing(
    params,
    fetch_raw=False,     # Fetch raw recording files from acquisition machine
    do_score=True,      # Do scoring to slice data into trials

    # Before running SSS, make SUBJ/raw_fif/SUBJ_prebad.txt file with
    # space-separated list of bad MEG channel numbers
    push_raw=False,      # Push raw files and SSS script to SSS workstation
    do_sss=False,        # Run SSS remotely (on sws) or locally with mne-python
    fetch_sss=False,     # Fetch SSSed files from SSS workstation
    do_ch_fix=False,     # Fix channel ordering

    # Before running SSP, examine SSS'ed files and make
    # SUBJ/bads/bad_ch_SUBJ_post-sss.txt; usually, this should only contain EEG
    # channels.
    gen_ssp=False,       # Generate SSP vectors
    apply_ssp=False,     # Apply SSP vectors and filtering
    plot_psd=False,      # Plot raw data power spectra
    write_epochs=True,  # Write epochs to disk
    gen_covs=True,      # Generate covariances

    # Make SUBJ/trans/SUBJ-trans.fif using mne_analyze; needed for fwd calc.
    gen_fwd=True,       # Generate forward solutions (and src space if needed)
    gen_inv=True,       # Generate inverses
    gen_report=True,    # Write mne report html of results to disk
    print_status=True,  # Print completeness status update
)
