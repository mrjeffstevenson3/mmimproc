import collections
from os.path import join
from pylabs.utils.paths import getlocaldataroot

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subjects = ['sub-phant2016-03-02', 'sub-phant2016-03-11']
niftiDict = collections.defaultdict(list)

## convert parrecs to nifti
for subj in subjects:
    subjectdir = join(projectdir, subj)
