import glob, os, pandas, numpy, niprov, nibabel, cPickle
from os.path import join
from nipype.interfaces import fsl
from pylabs.utils.paths import getnetworkdataroot
provenance = niprov.Context()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo')
applyxfm = fsl.ApplyXfm()

fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = ['sub-2013-C028', 'sub-2013-C029', 'sub-2013-C030', 'sub-2013-C037', 'sub-2013-C053', 'sub-2013-C065']

with open(join(fs, project, 'all_5yo_subj_conversion_dict_may17_clouddumps.pickle'), 'rb') as f:
    niftiDict = cPickle.load(f)

for subj in subjects:
    for ses in [1, 2]:
        for run in [1, 2, 3, 4]
        method = 'anat'
        if niftiDict[(subj, 'ses-'+str(ses), method)][subj+'_ses-'+str(ses)+'_wemempr_'+str(run)]['outfilename']
