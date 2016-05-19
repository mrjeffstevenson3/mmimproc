import glob, os, pandas, numpy, niprov, nibabel, cPickle
from os.path import join
from collections import defaultdict
from nipype.interfaces import fsl
import subprocess
from datetime import datetime
from time import sleep
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.utils.paths import getnetworkdataroot
provenance = niprov.Context()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXfm(output_type='NIFTI')
fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = ['sub-2013-C028', 'sub-2013-C029', 'sub-2013-C030', 'sub-2013-C037', 'sub-2013-C053', 'sub-2013-C065']
convert = False
#run conversion if needed
if convert:
    niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
else:
    with open(join(fs, project, 'niftiDict_all_subj_201605190953.pickle'), 'rb') as f:
        niftiDict = cPickle.load(f)

for subj in subjects:
    for ses in [1, 2]:    # arbitrary! fix by testing range in dict
        for run in [1, 2, 3, 4]:      # arbitrary! fix by testing range in dict
            method = 'anat'
            k1a = (subj, 'ses-'+str(ses), method)
            k2w = subj+'_ses-'+str(ses)+'_wemempr_'+str(run)
            if niftiDict[k1a][k2w]['outfilename'] == []:
                continue
            cmd = 'mri_concat --rms --i '
            cmd += niftiDict[k1a][k2w]['outfilename']
            cmd += ' --o '
            cmd += niftiDict[k1a][k2w]['outpath']
            cmd += '/'+k2w+'_rms.nii'
            subprocess.check_call(cmd, shell=True)
            niftiDict[k1a][k2w + '_rms']['wemempr_fname'] = niftiDict[k1a][k2w]['outpath']+'/'+k2w+'_rms.nii'
            niftiDict[k1a][k2w]['rms_fname'] = niftiDict[k1a][k2w]['outpath']+'/'+k2w+'_rms.nii'
            k2v = subj+'_ses-'+str(ses)+'_vbmmempr_'+str(run)
            cmd = 'mri_concat --rms --i '
            cmd += niftiDict[k1a][k2v]['outfilename']
            cmd += ' --o '
            cmd += niftiDict[k1a][k2v]['outpath']
            cmd += '/' + k2v + '_rms.nii'
            subprocess.check_call(cmd, shell=True)
            niftiDict[k1a][k2v + '_rms']['vbmmempr_fname'] = niftiDict[k1a][k2v]['outpath']+ '/' + k2v + '_rms.nii'
            niftiDict[k1a][k2v]['rms_fname'] = niftiDict[k1a][k2v]['outpath']+ '/' + k2v + '_rms.nii'
            method = 'fmap'
            k1b = (subj, 'ses-'+str(ses), method)
            k2b = subj+'_ses-'+str(ses)+'_b1map_'+str(run)
            if niftiDict[k1b][k2b]['outfilename'] == []:
                continue
            flt.inputs.in_file = niftiDict[k1b][k2b]['outfilename']
            flt.inputs.reference = niftiDict[k1a][k2v]['rms_fname']
            flt.inputs.out_matrix_file = niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_reg2vbmmpr.mat'
            res = flt.run()
            cmd = 'fslroi '+niftiDict[k1b][k2b]['outfilename']+' '+niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_phase.nii.gz 2 1'
            subprocess.check_call(cmd, shell=True)
            sleep(5)
            niftiDict[k1b][k2b]['phase_fname'] = niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_phase.nii.gz'
            applyxfm.inputs.in_matrix_file = niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_reg2vbmmpr.mat'
            applyxfm.inputs.in_file = niftiDict[k1b][k2b]['phase_fname']
            applyxfm.inputs.out_file = niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_phase_reg2vbmmpr.nii'
            applyxfm.inputs.reference = niftiDict[k1a][k2v]['rms_fname']
            applyxfm.inputs.apply_xfm = True
            result = applyxfm.run()
            cmd = 'fslmaths '+niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_phase_reg2vbmmpr.nii -s 6 '
            cmd += niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_phase_reg2vbmmpr_s6.nii.gz'
            subprocess.check_call(cmd, shell=True)
            niftiDict[k1b][k2b]['phase_reg2vbm_s6_fname'] = niftiDict[k1b][k2b]['outpath']+'/'+k2b+'_phase_reg2vbmmpr_s6.nii.gz'
            cmd = 'fslmaths '+niftiDict[k1a][k2v]['rms_fname']+' -div '+niftiDict[k1b][k2b]['phase_reg2vbm_s6_fname']
            cmd += ' -mul 100 '+niftiDict[k1a][k2v]['outpath']+ '/' + k2v + '_rms_b1corr.nii'
            subprocess.check_call(cmd, shell=True)
            niftiDict[k1a][k2v]['b1corr_fname'] = niftiDict[k1a][k2v]['outpath']+ '/' + k2v + '_rms_b1corr.nii.gz'
            cmd = 'fslmaths ' + niftiDict[k1a][k2w]['rms_fname'] + ' -div ' + niftiDict[k1b][k2b]['phase_reg2vbm_s6_fname']
            cmd += ' -mul 100 ' + niftiDict[k1a][k2w]['outpath'] + '/' + k2w + '_rms_b1corr.nii'
            subprocess.check_call(cmd, shell=True)
            niftiDict[k1a][k2w]['b1corr_fname'] = niftiDict[k1a][k2w]['outpath'] + '/' + k2w + '_rms_b1corr.nii.gz'
            k2t2 = subj+'_ses-'+str(ses)+'_3dt2_'+str(run)
            if not os.path.isfile(niftiDict[k1a][k2t2]['outfilename']):
                continue
            cmd = 'fslmaths ' + niftiDict[k1a][k2t2]['outfilename'] + ' -div ' + niftiDict[k1b][k2b]['phase_reg2vbm_s6_fname']
            cmd += ' -mul 100 ' + niftiDict[k1a][k2t2]['outpath'] + '/' + k2t2 + '_b1corr.nii'
            subprocess.check_call(cmd, shell=True)
            niftiDict[k1a][k2t2]['b1corr_fname'] = niftiDict[k1a][k2t2]['outpath'] + '/' + k2t2 + '_b1corr.nii.gz'


with open(join(fs, project, "niftiDict_all_struc_b1corr_{:%Y%m%d%H%M}.pickle".format(datetime.now())), "wb") as f:
    f.write(dumps(niftiDict))
with open(join(fs, project, "niftidict_all_struc_b1corr_{:%Y%m%d%H%M}.pickle".format(datetime.now())), "wb") as f:
    f.write(dumps(niftidict))
