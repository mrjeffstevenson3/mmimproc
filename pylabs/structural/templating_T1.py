import glob, os, pandas, numpy, niprov, nibabel, cPickle
from os.path import join
from nipype.interfaces import fsl
import subprocess
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.utils.paths import getnetworkdataroot
provenance = niprov.Context()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo')
applyxfm = fsl.ApplyXfm()
fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = ['sub-2013-C028', 'sub-2013-C029', 'sub-2013-C030', 'sub-2013-C037', 'sub-2013-C053', 'sub-2013-C065']
convert = False
#run conversion if needed
if convert:
    niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
else:
    with open(join(fs, project, 'niftiDict_all_subj_201605181335.pickle'), 'rb') as f:
        niftiDict = cPickle.load(f)

for subj in subjects:
    for ses in [1, 2]:    # arbitrary! fix by testing range in dict
        for run in [1, 2, 3, 4]:      # arbitrary! fix by testing range in dict
        method = 'anat'
        if niftiDict[(subj, 'ses-'+str(ses), method)][subj+'_ses-'+str(ses)+'_wemempr_'+str(run)]['outfilename'] == []:
            continue
        cmd = 'mri_concat --rms --i '
        cmd += niftiDict[(subj, 'ses-'+str(ses), method)][subj+'_ses-'+str(ses)+'_wemempr_'+str(run)]['outfilename']
        cmd += ' --o '
        cmd += niftiDict[(subj, 'ses-'+str(ses), method)][subj+'_ses-'+str(ses)+'_wemempr_'+str(run)]['outpath']
        wemempr_fname = subj+'_ses-'+str(ses)+'_wemempr_'+str(run)+'_rms.nii'
        cmd += '/'+wemempr_fname
        subprocess.check_call(cmd, shell=True)
        niftiDict[(subj, 'ses-' + str(ses), method)][subj + '_ses-' + str(ses) + '_wemempr_' + str(run) + '_rms']['wemempr_fname'] = wemempr_fname

        cmd = 'mri_concat --rms --i '
        cmd += niftiDict[(subj, 'ses-' + str(ses), method)][subj + '_ses-' + str(ses) + '_vbmmempr_' + str(run)]['outfilename']
        cmd += ' --o '
        cmd += niftiDict[(subj, 'ses-' + str(ses), method)][subj + '_ses-' + str(ses) + '_vbmmempr_' + str(run)]['outpath']
        vbmmempr_fname = subj + '_ses-' + str(ses) + '_vbmmempr_' + str(run) + '_rms.nii'
        cmd += '/' + vbmmempr_fname
        subprocess.check_call(cmd, shell=True)
        niftiDict[(subj, 'ses-' + str(ses), method)][subj + '_ses-' + str(ses) + '_vbmmempr_' + str(run) + '_rms']['vbmmempr_fname'] = vbmmempr_fname
