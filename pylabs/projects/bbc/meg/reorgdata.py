## reorganize data into MNEFUN system
import glob, shutil, os
from os.path import join, basename, isfile, isdir

#indir = '/home/jasper/mirror/js/bbc'
#newdir = '/home/jasper/data/bbc'
indir = '/mnt/users/js/bbc'
newdir = '/diskArray/data/bbc/meg'

toCopy = []

for subjectdir in glob.glob(join(indir, 'sub-*')):
    subnum = int(basename(subjectdir)[-3:])
    fifs = glob.glob(join(subjectdir,'*','raw_meg','*.fif'))
    fifbasenames = [basename(f) for f in fifs]
    if not fifs:
        continue
    print('Subject {}'.format(subnum))
    for fif in fifs:
        print('    {}'.format(basename(fif)))
    targetdir = join(newdir, 'bbc_{}'.format(subnum), 'raw_fif')
    if not isdir(targetdir):
        os.makedirs(targetdir)
    prebadfile = join(targetdir, 'bbc_{}_prebad.txt'.format(subnum))
    with open('prebad.txt', 'w'):
        pass
    toCopy.append(('prebad.txt', prebadfile))
    for tp in ('raw','ave'):
        rawfname = 'bbc_{}_{}.fif'.format(subnum, tp)
        rawfiles = [f for f in fifs if rawfname in f]
        if not len(rawfiles) > 0:
            print('    Missing file: '+rawfname)
            continue
        movedrawfile = join(targetdir, rawfname)
        toCopy.append((rawfiles[0], movedrawfile))
    ermfiles = [f for f in fifs if 'empty' in f or 'erm' in f]
    if not len(ermfiles) > 0:
        print('    No empty room recording found.')
        continue
    movedermfile = join(targetdir, 'bbc_{}_erm_raw.fif'.format(subnum))
    toCopy.append((sorted(ermfiles)[-1], movedermfile))

for c, copy in enumerate(toCopy):
    print('Copying file {} of {}'.format(c+1, len(toCopy)))
    if isfile(copy[1]): 
        print('    target file exists, skipping.')
        continue
    shutil.copy(copy[0], copy[1])


