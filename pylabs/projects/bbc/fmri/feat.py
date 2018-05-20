import os, subprocess, datetime, nibabel, numpy
from os.path import join, basename, dirname, isfile, isdir, abspath
import shell
EVs = numpy.loadtxt('data/explvars.txt', dtype=int)

# run script
import findfmrs
subjects = findfmrs.files

if not isdir('fsfs'):
    os.makedirs('fsfs')
if not isdir('evfiles'):
    os.makedirs('evfiles')

bbcfuncdir = dirname(dirname(abspath(__file__)))

for s, subjectinfo in enumerate(subjects):
    subnum = subjectinfo['subnum']
    msg = 'Running FEAT for subject {} of {}: {}.'
    print(msg.format(s+1, len(subjects), subnum))
    with open('feat/full.fsf.template') as temfile:
        template = temfile.read()
    func = subjectinfo['func']
    anat = subjectinfo['anat']
    anatbrain = anat.replace('.nii','_brain.nii')

    img = nibabel.load(func)
    nvols = img.shape[-1]
    print('    # volumes: {}'.format(nvols))
    if nvols < 10:
        print('Too few volumes, skipping.')
        continue

    evfiles = [None, None]
    for c, condition in enumerate(['words', 'tones']):
        evfiles[c] = join(bbcfuncdir,'evfiles',
            '{}_{}.ev'.format(subnum, condition))
        with open(evfiles[c], 'w') as evfile:
            for vol in range(nvols):
                evfile.write(str(EVs[vol, c])+'\n')

    params = {
        'func': func, 
        'anat': anatbrain, 
        'nvols': nvols,
        'evfile1': evfiles[0],
        'evfile2': evfiles[1],
    }

    contents = template.format(**params)
    fsfname = join('fsfs',str(subnum)+'.fsf')
    with open(fsfname, 'w') as fsf:
        fsf.write(contents)

    env = os.environ.copy()
    if 'FSLPARALLEL' in env:
        del env['FSLPARALLEL']
    
    shell.tryrun(['feat', fsfname], env=env)


    
