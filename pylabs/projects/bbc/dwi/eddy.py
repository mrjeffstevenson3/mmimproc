import os
from os.path import join, basename, dirname, isfile, isdir
from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
fs = getnetworkdataroot()
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
subjid, sespassqc, runpassqc = zip(*dwi_passed_qc)
methodpassqc = ['dti_15dir_b1000'] * len(dwi_passed_qc)
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in zip(subjid, sespassqc, methodpassqc, runpassqc)]

for dwif in dwi_fnames:
    infpath = join(fs, project, dwif.split('_')[0] , dwif.split('_')[1], 'dwi')
    fdwi = join(infpath, dwif + '.nii')
    fbvecs = join(fpath, dwif + '.bvecs')
    fbvals = join(fpath, dwif + '.bvals')
    fdwell = join(fpath, dwif + '.dwell_time')
    with WorkingContext(infpath):
        bvals, bvecs = read_bvals_bvecs(fbvals, fbvecs)
        gtab = gradient_table(bvals, bvecs)
        # make index and acquisition parameters files
        with open(join(fpath, 'index.txt'), 'w') as f:
            f.write('1 ' * len(gtab.bvals))

        with open(fdwell, 'r') as f:
            dwell = f.read().replace('\n', '')

        with open(join(fpath, 'acq_params.txt'), 'w') as f:
            f.write('0 1 0 ' + dwell)
        # execute eddy command in subprocess in local working directory using defaults
        outpath = join(infpath, 'cuda_defaults')
        if not isdir(outpath):
            os.makedirs(outpath)
        cmd = ''
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + fbvals + ' --bvecs=' + fbvecs
        cmd += ' --imain=' + fdwi + ' --index=index.txt --mask=' + brain_outfname + '_mask.nii '
        cmd += '--out=' + join(outpath, dwif + '_eddy_corrected')
        run_subprocess(cmd)
        # execute eddy command in subprocess in local working directory using repol
        outpath = join(infpath, 'cuda_repol')
        if not isdir(outpath):
            os.makedirs(outpath)
        cmd = ''
        cmd += 'eddy_cuda7.5 --acqp=acq_params.txt --bvals=' + fbvals + ' --bvecs=' + fbvecs
        cmd += ' --imain=' + fdwi + ' --index=index.txt --mask=' + brain_outfname + '_mask.nii '
        cmd += '--out=' + join(outpath, dwif + '_eddy_corrected_repol') + ' --repol'
        run_subprocess(cmd)
