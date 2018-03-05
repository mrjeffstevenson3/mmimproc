from pathlib import *
import glob, os, pandas, numpy, nibabel, cPickle, shutil, pylabs
from os.path import join
import nibabel as nib
import pandas as pd
from collections import defaultdict
from nipype.interfaces import fsl
from pylabs.utils import *
prov = ProvenanceWrapper()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo')
applyxfm = fsl.ApplyXFM()
fs = getnetworkdataroot()

def dti_motion_qc(project, subjects, alpha=3.0):
    origdir = os.getcwd()
    diffdir = join(getpylabspath(), 'pylabs', 'diffusion')
    for subject in subjects:
        dwifiles = glob.glob(join(fs, project, subject, 'ses-?', 'dwi', '*.nii'))
        for dwifile in dwifiles:
            dtidir = join('/', *dwifile.split('/')[:-1])
            dtifbasenm = dwifile.split('.')[0]
            qcdir = join(dtidir, 'dwi_qc')
            if os.path.exists(qcdir):
                shutil.rmtree(qcdir)
            os.makedirs(qcdir)
            shutil.copy2(dwifile, join(qcdir, 'dtishort.nii'))
            shutil.copy2(dtifbasenm+'.bvals', join(qcdir, 'bvals'))
            shutil.copy2(dtifbasenm+'.bvecs', join(qcdir, 'bvecs'))
            shutil.copy2(join(diffdir, 'plotqc1.m'), join(qcdir, 'plotqc1.m'))
            os.chdir(qcdir)
            with open(join(qcdir, 'alphalevel.txt'), "w") as alphalevel:
                alphalevel.write("{}".format(alpha))
            cmd = 'fslchfiletype ANALYZE ' + join(qcdir, 'dtishort.nii')
            run_subprocess(cmd)
            run_subprocess(join(diffdir, 'dti_qc_correlation_bval1000'))
    os.chdir(origdir)
    return

def dwi_qc_1bv(dwi_data, affine, output_pname, alpha=3.0):
    results = ()
    dwi_qc, plot_vols = getqccmd()
    if not output_pname.parent.is_dir():
        output_pname.parent.mkdir(parents=True)
    nib.save(nib.AnalyzeImage(dwi_data.astype('float32'), affine), str(output_pname.parent/'dtishort.hdr'))

    with WorkingContext(str(output_pname.parent)):
        # make alpha_level.txt parameter file
        with open('alphalevel.txt', 'w') as f:
            f.write(str(alpha) + '\n')
        results += run_subprocess([str(dwi_qc)])
        # add set commands for subj ids
        Path('gnuplot_for_dtiqc_bad.txt').unlink()
        Path('gnuplot_for_dtiqc_good.txt').unlink()
        with open('gnuplot_for_dtiqc_bad.txt', mode='a') as bad_qc:
            bad_qc.write('#!/usr/bin/gnuplot\n')
            bad_qc.write('reset\n')
            bad_qc.write('set title \''+ output_pname.parts[-5] + ' ' + output_pname.parts[-4] +' DTI QC plot key shows bad number\' font \"Helvetica,24\"\n')
        with open('gnuplot_for_dtiqc_good.txt', mode='a') as good_qc:
            good_qc.write('#!/usr/bin/gnuplot\n')
            good_qc.write('reset\n')
            good_qc.write('set title \'' + output_pname.parts[-5] + ' ' + output_pname.parts[-4] + ' DTI QC plot key shows good number of volumes\' font \"Helvetica,24\"\n')


        results += run_subprocess(['bash '+str(plot_vols)])
        badvols = pd.read_csv('bad_vols_index.txt', header=None, delim_whitespace=True, index_col=0, dtype={1: 'int64'})
        try:
            Path('gnuplot_for_dtiqc_good.png').rename(appendposix(output_pname, '_good_plot.png'))
            Path('gnuplot_for_dtiqc_bad.png').rename(appendposix(output_pname, '_bad_plot.png'))
            Path('qc_report.txt').rename(appendposix(output_pname, '_report.txt'))
        except OSError:
            print(str(output_pname)+' files not found. moving on.')
    return badvols  # results dataframe
