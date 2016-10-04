import mne

fname = '/home/jasper/data/bbc/bbc_116/raw_fif/bbc_116_raw.fif'

raw = mne.io.read_raw_fif(fname, allow_maxshield=True)



# Set up pick list: MEG + STI 014 - bad channels
want_meg = True
want_eeg = True
want_stim = True
#raw.info['bads'] += ['MEG 2443', 'EEG 053']  # bad channels + 2 more

picks = mne.pick_types(raw.info, meg=False, misc=True, eog=True, emg=True, stim=want_stim)

some_picks = picks #[:5]  # take 5 first
#start, stop = raw.time_as_index([0, 15])  # read the first 15s of data
#data, times = raw[some_picks, start:(stop + 1)]

# save 150s of MEG data in FIF file
raw.save('sample__raw.fif', tmin=100, tmax=120, picks=picks,
         overwrite=True)

raw = mne.io.read_raw_fif('sample__raw.fif', allow_maxshield=True)
raw.plot(duration=6, n_channels=4, scalings='auto')




