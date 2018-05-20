import glob, os
from os.path import join, basename, dirname, isfile, isdir
import shell

#indir = '/home/jasper/data/bbc/meg/'
indir = '/diskArray/data/bbc/meg/'
kasgadir = '/data06/jasper/bbc/'
maxfilterbin = '/neuro/bin/util/maxfilter-2.2'
cmd = ['ssh','jasper@kasga.ilabs.uw.edu']
cmd += [maxfilterbin, '-f', None, '-headpos', '-o', None, '-hp', None]
fextensions = ['_raw.fif', '_quat.fif', '.pos']

subjectdirs = glob.glob(join(indir, 'bbc_*'))
for s, subjectdir in enumerate(subjectdirs):
    subject = basename(subjectdir)
    print('Subject {} of {}: {}'.format(s+1, len(subjectdirs), subject))
    remoterawdir = join(kasgadir, subject, 'raw_fif')

    raw, quat, pos = (join(remoterawdir, subject+ext) for ext in fextensions)
    for i, fpath in {4:raw, 7:quat, 9:pos}.items():
        cmd[i] = fpath
    log = join(subjectdir, 'headpos.log')
    shell.tryrun(cmd, logfpath = log)
