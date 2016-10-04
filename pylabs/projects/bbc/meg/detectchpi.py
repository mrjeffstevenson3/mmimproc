import mne, glob
from os.path import join, basename

#datadir = '/home/jasper/data/bbc'
datadir = '/diskArray/data/bbc/meg'

files = []
fifs = glob.glob(join(datadir,'*','raw_fif','*.fif'))
rawfifs = [f for f in fifs if 'raw.fif' in f]
for fpath in rawfifs:
    if '252' in fpath:
        print('skipping 252')
        continue
    raw = mne.io.read_raw_fif(fpath, allow_maxshield=True)
    nresults = len(raw.info['hpi_results'])
    if nresults > 0:
        accepted = raw.info['hpi_results'][0]['accept']
    else:
        accepted = None
    files.append((fpath, nresults, accepted))
for info in files:
    print('{}\n\tnresults: {}\n\taccept: {}'.format(*info))
