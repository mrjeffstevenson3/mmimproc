import glob, shutil, os
from os.path import join, basename, dirname, isfile, isdir, splitext

#rootdir = '/home/jasper/data/bbc/meg/'
rootdir = '/diskArray/data/bbc/meg/'
headposdir = join(rootdir, 'eval', 'headpos')
if not isdir(headposdir):
    os.makedirs(headposdir)

subjectdirs = glob.glob(join(rootdir, 'bbc_*'))
for s, subjectdir in enumerate(subjectdirs):
    subject = basename(subjectdir)
    print('Subject {} of {}: {}'.format(s+1, len(subjectdirs), subject))

    shutil.copyfile(join(subjectdir , 'headpos.log'), 
                    join(headposdir, subject+'_headpos.log'))
