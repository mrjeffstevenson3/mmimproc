
class SubjIdPicks(object):
    pass


global subjids
project = 'nbwr'
ftempl = 'sub-nbwr{}_ses-{}_{}_{}'
vbm_rms = [
    ('998', 1, 'vbmmempr_ti850_rms', 1),
    ]
freesurf_rms = [
    ('999b', 1, 'vbmmempr_rms', 1),
    ('998', 1, 'vbmmempr_ti1100_rms', 1),
    ('144', 1, 'fsmempr_ti1100_rms', 1),
    ]
vbm_fnames = []
freesurf_fnames = []

topup_fnames = []
topdn_fnames= []
dwi_fnames = []


def get_vbm_names(subjids_picks):
    for vbm in vbm_rms:
        if vbm[0] in subjids_picks.subjids:
            vbm_fnames.append(ftempl.format(*vbm))
    return vbm_fnames #, # dwi_fnames

def get_freesurf_names(subjids_picks):
    for freesurf in freesurf_rms:
        if freesurf[0] in subjids_picks.subjids:
            freesurf_fnames.append(ftempl.format(*freesurf))
    return freesurf_fnames, # dwi_fnames

