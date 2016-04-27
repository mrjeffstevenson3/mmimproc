# J-correction for brains
from __future__ import division
import datetime
from pylabs.qt1.formulas import spgrWithJ

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
date = datetime.date(2015, 6, 8)
subject = 'sub-phant'+str(date)
subjectdir = join(projectdir, subject)

alphafiles = sorted(glob.glob(join(subjectdir,'anat',alphafilter)))
b1file = join(subjectdir, 'fmap', '{}_b1map_phase_1.nii'.format(subject))

# ## Need j, TR, TE, T2s
j = 9
T2s = 50
TE = 4.6 ?
# spgrWithJ(a, S0, T1)
