import pandas as pd
import os
from os.path import join
from pylabs.utils.paths import getnetworkdataroot
fs = getnetworkdataroot()
print (fs)


def make_sessions_fm_dict(niidict, project, subject):
    col_order = ['session_id', 'acq_time', 'basefilename', 'converted', 'tr', 'fa', 'ti',
                'QC', 'pre_proc', 'outdir', 'scan_name', 'outfilename', 'bvs', 'dwell_time',
                 'field_strength', 'bvals', 'bvecs' ]

    sessions = []
    scans = []

    for session, s in niidict.iteritems():
        #assert sessions.append(session[0]) == subject
        sessions.append(session)
        scans.append(pd.DataFrame.from_dict(s, orient='index'))

    sessionsDF = pd.concat(scans, keys=sessions)
    remain_cols = [x for x in sessionsDF.columns.values if x not in col_order]
    subsessionsDF = sessionsDF[col_order+remain_cols].reset_index(drop=True)

    if all(subsessionsDF['multisession'] > 0) == True and os.path.isfile(join(fs, project, subject, str(subject) +'_sessions.tsv')):
        orig_subsessionsDF = pd.DataFrame.from_csv(open(join(fs, project, subject, str(subject) +'_sessions.tsv')), sep='\t', header=1)
        subsessionsDF = subsessionsDF.append(orig_subsessionsDF)

    subsessionsDF.to_csv(join(fs, project, subject, str(subject) +'_sessions.tsv'), columns=col_order+remain_cols,
                             index=False, sep='\t', encoding='utf-8')
    return sessionsDF