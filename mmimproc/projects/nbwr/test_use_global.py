import socket
import mmimproc as ip

class SubjIdPicks(object):
    subjids = None
    pass

def testgetnetworkdataroot(datadir=ip.fs_local):
    hostname = socket.gethostname()
    if datadir.target == 'scotty':
        if hostname == 'scotty.ilabs.uw.edu':
            return '/media/DiskArray/shared_data/js/'
        elif hostname in ['redshirt.ilabs.uw.edu', 'redshirt', 'uhora.ilabs.uw.edu', 'uhora', 'sulu.ilabs.uw.edu', 'sulu', 'JVDB']:
            return '/mnt/users/js/'
        elif any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
            return '/Users/mrjeffs/Documents/Research/data'
        else:
            raise ValueError('Dont know where scotty network data root is on this computer.')
    if datadir.target == 'jaba':
        if hostname in ['scotty.ilabs.uw.edu', 'scotty', 'redshirt.ilabs.uw.edu', 'redshirt', 'uhora.ilabs.uw.edu', 'uhora', 'sulu.ilabs.uw.edu', 'sulu', 'JVDB']:
            return '/mnt/brainstudio/data'
        elif any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
            return '/Users/mrjeffs/Documents/Research/data'
        else:
            raise ValueError('Dont know where jaba network data root is on this computer.')


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

