import glob, os, niprov
from os.path import join
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
from pylabs.utils import WorkingContext
provenance = niprov.Context()

"""
The bulk of the roots qt1 pipeline is in qt1pipeline.py,
but this script covers the lengthy ANTS alignment and is run separately.
"""

## behavior
from pylabs.projects.roots.behavior import selectedvars
behavior = selectedvars.T

## directories
fs = getnetworkdataroot()
projectdir = join(fs, 'roots_of_empathy')
regdir = join(projectdir, 'reg', 'qt1')
templatedir = join(projectdir, 'reg', 'templ_ANTS_we_b1corr_brain_susanthr200')
targettemplate = '{}_ses-1_wemempr_1_rms_b1corr_brain_susan200.nii.gz'
subjects = ['sub-2013-C0{}'.format(s) for s in behavior.index.values]
nsubjects = len(subjects)


ref = None
subjectfiles = []
outputs = {}
for s, subject in enumerate(subjects):
    print('Subject {} of {}: {}'.format(s+1, nsubjects, subject))
    sessiondir = join(projectdir, subject, 'ses-1')
    movingfpath = join(sessiondir, 'qt1', '{}_t1.nii.gz'.format(subject))
    targetfpath = join(templatedir, targettemplate.format(subject))
    outprefix = subject + '_qt1'
    print(movingfpath)
    print(targetfpath)
    cmd = []
    antsbin = join(os.environ['ANTSPATH'], 'antsRegistrationSyN.sh')
    cmd += ['antsRegistrationSyN.sh', '-d','3','-n','10','-t','s']
    cmd += ['-f', targetfpath]
    cmd += ['-m', movingfpath]
    cmd += ['-o', outprefix]
    with WorkingContext(regdir):
        output = subprocess.check_output(cmd)
    outputs[subject] = output

