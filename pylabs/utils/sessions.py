



if opts.multisession[0] != 0 and os.path.isfile(join(subpath, str(opts.subj ) +'_sessions.tsv')):
    subsessionsDF = pd.DataFrame.from_csv(open(join(subpath, str(opts.subj ) +'_sessions.tsv')), sep='\t', header=1)
else:
    subsessionsDF = pd.DataFrame (columns=['session_id', 'acq_time', 'scan', 'converted', 'tr', 'fa', 'ti', 'QC', 'pre_proc'])
