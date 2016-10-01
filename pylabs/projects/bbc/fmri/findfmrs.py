## reorganize data into MNEFUN system
import glob, shutil, os
from os.path import join, basename, dirname, isfile, isdir
from fmr_runs import picks

rootdir = '/mnt/users/js/bbc/'
targetdir = '/diskArray/data/bbc/'
fmrtem = 'sub-bbc{}/ses-{}/fmri/sub-bbc{}_ses-{}_fmri_{}.nii'
anattem = 'sub-bbc{}/ses-{}/anat/sub-bbc{}_ses-{}_wempr_1.nii'
toCopy = []
files = []

for subjectpick in picks:
    subnum, session, run = subjectpick
    fmr = fmrtem.format(subnum, session, subnum, session, run)
    anat = anattem.format(subnum, session, subnum, session)
    subjectfiles = {'subnum':subnum}
    for tp, relpath in {'func':fmr, 'anat':anat}.items():
        origfile = join(rootdir, relpath)
        if tp is 'anat':
            if not isfile(origfile):
                relpath = anattem.format(subnum, 1, subnum, 1)
                origfile = join(rootdir, relpath)
                msg = 'No anat for sub {} sess {}, using sess 1'
                print(msg.format(subnum, session))
        movedfile = join(targetdir, relpath)
        subjectfiles[tp] = movedfile
        toCopy.append((origfile, movedfile))
    files.append(subjectfiles)

if isdir(rootdir):
    for c, copy in enumerate(toCopy):
        print('Copying file {} of {}'.format(c+1, len(toCopy)))
        if isfile(copy[1]): 
            print('    target file exists, skipping.')
            continue
        os.makedirs(dirname(copy[1]))
        shutil.copy(copy[0], copy[1])
else:
    print('Warning: not on Tintagel, skipping copying / filepaths unreliable')

