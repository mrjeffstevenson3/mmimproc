from os.path import join
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
from pylabs.atlassing import atlasWiseSignificantVoxelsFrame
fs = getlocaldataroot()
statsdir = join(fs, 'roots_of_empathy', 'correlations_qt1')
# atkas + stats > frame > table
atlasfpath = 'data/atlases/test-atlas-240x240x116.nii.gz'

statfiles = {
    'Affect-Knowledge-Test':{
        '2minp':'R-POST-Affect-Knowledge-Test-Sum-of-8-Vignettes_2minp.nii.gz',
        'r': 'R-POST-Affect-Knowledge-Test-Sum-of-8-Vignettes_r.nii.gz',
        'tneg':'R-POST-Affect-Knowledge-Test-Sum-of-8-Vignettes_tneg.nii.gz',
        'tpos':'R-POST-Affect-Knowledge-Test-Sum-of-8-Vignettes_tpos.nii.gz',
    },
    'Flag-Switch':{
        '2minp':'R-POST-Flag-Switch_2minp.nii.gz',
        'r': 'R-POST-Flag-Switch_r.nii.gz',
        'tneg':'R-POST-Flag-Switch_tneg.nii.gz',
        'tpos':'R-POST-Flag-Switch_tpos.nii.gz',
    }
}
for var in statfiles.keys():
    for stat in statfiles[var].keys():
        statfiles[var][stat] = join(statsdir, statfiles[var][stat])

F = atlasWiseSignificantVoxelsFrame(statfiles, pmax=.001, atlas=atlasfpath)
print(F)
