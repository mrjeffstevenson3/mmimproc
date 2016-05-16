import pandas as pd
import os

def make_sessions_fm_dict(niidict, project, subject):
    col_order = ['session_id', 'acq_time', 'basefilename', 'converted', 'tr', 'fa', 'ti',
                'QC', 'pre_proc', 'outdir', 'scan_name', 'outfilename', 'bvs', 'dwell_time',
                 'field_strength', 'bvals', 'bvecs' ]
    sorterIndex = dict(zip(col_order,range(len(col_order))))
    sessions = []
    scans = []

    for session, s in niidict.iteritems():
        #assert sessions.append(session[0]) == subject
        sessions.append(session)
        scans.append(pd.DataFrame.from_dict(s, orient='index'))

    sessionsDF = pd.concat(scans, keys=sessions)
    #sessionsDF['sortby'] = sessionsDF['d1'].map(sorterIndex)

    #sessionsDF.set_index(sorterIndex.keys(), inplace=True)

    if opts.multisession[0] != 0 and os.path.isfile(join(subpath, str(opts.subj ) +'_sessions.tsv')):
        subsessionsDF = pd.DataFrame.from_csv(open(join(subpath, str(opts.subj ) +'_sessions.tsv')), sep='\t', header=1)
    else:
        subsessionsDF = pd.DataFrame (columns=['session_id', 'acq_time', 'scan', 'converted', 'tr', 'fa', 'ti', 'QC', 'pre_proc'])

    return sessionsDF