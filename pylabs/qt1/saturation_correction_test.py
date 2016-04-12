import collections
from os.path import join
from pylabs.utils.paths import getlocaldataroot
import glob
from pylabs.qt1.fitting import spgrformula
from scipy.optimize import curve_fit

fs = getlocaldataroot()
projectdir = join(fs, 'phantom_qT1_slu')
subject = 'sub-phant2016-03-02'
anatdir = join(projectdir, subject, 'anat')

anglefiles = sorted(glob.glob(join(anatdir,'*14*1.nii')))
X = [7,10,15,20,30]


## fitting
ai = 15*Y.max()  # S0
bi = 1000           # T1
p0=[ai, bi]
spgrformula.TR = TR
formula = spgrformula
poi = 1

popt, pcov = curve_fit(formula, Xv, Y, p0=p0)


