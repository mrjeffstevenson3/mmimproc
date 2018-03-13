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

gnuplot_cmds_part2 = ('set xlabel \'Slice number\' font \"Helvetica,24\" \n'
                    'set xtics font \"Helvetica,18\" \n'
                    'set ytics font \"Helvetica,18\" \n'
                    'set border lw 4\n'
                    'set ylabel \'DTI intensity\' font \"Helvetica,16\"\n'
                    'set xrange [0:90]\n'
                    'set pointsize 3.0\n'
                    'set key top right\n'
                    'set key autotitle columnheader\n'
                    'set timestamp\n')

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

def dwi_qc_1bv(dwi_data, output_pname, alpha=3.0):
    results = ()
    dwi_qc, plot_vols = getqccmd()
    if not output_pname.parent.is_dir():
        output_pname.parent.mkdir(parents=True)
    nib.save(nib.AnalyzeImage(dwi_data.astype('float32'), None), str(output_pname.parent/'dtishort.hdr'))
    print('Working on '+output_pname.name)
    with WorkingContext(str(output_pname.parent)):
        # make alpha_level.txt parameter file
        with open('alphalevel.txt', 'w') as f:
            f.write(str(alpha) + '\n')
        if Path('plotbad1.txt').is_file():
            Path('plotbad1.txt').unlink()
        if Path('plotgood1.txt').is_file():
            Path('plotgood1.txt').unlink()
        results += run_subprocess([str(dwi_qc)])
        badvols = pd.read_csv('bad_vols_index.txt', header=None, delim_whitespace=True, index_col=0, dtype={1: 'int64'})
        try:
            num_badvols = badvols.iloc[:,0].value_counts()[1]
        except KeyError:
            num_badvols = 0
        num_goodvols = dwi_data.shape[3] - num_badvols
        print('found '+str(num_badvols)+' out of '+str(dwi_data.shape[3])+' for '+str(output_pname.name).split('_')[-1])
        # add set commands for subj ids
        if Path('gnuplot_for_dtiqc_bad.txt').is_file():
            Path('gnuplot_for_dtiqc_bad.txt').unlink()
        if Path('gnuplot_for_dtiqc_good.txt').is_file():
            Path('gnuplot_for_dtiqc_good.txt').unlink()
        with open('gnuplot_for_dtiqc_bad.txt', mode='a') as bad_qc:
            bad_qc.write('#!/usr/bin/gnuplot\n')
            bad_qc.write('reset\n')
            bad_qc.write('set title \''+ output_pname.parts[-5] + ' ' + output_pname.parts[-4] +
                         ' DTI QC shows '+str(num_badvols)+' BAD vols for '+str(output_pname.name).split('_')[-1]+'\' font \"Helvetica,24\"\n')
            bad_qc.write(gnuplot_cmds_part2)
            if num_badvols <= 2:
                bad_qc.write('plot for [n=2:2] \'./plotbad1.txt\' u 1:(column(n)) w lines lw 4\n'
                             'set terminal png size 1200, 800 font 12\n'
                             'set output \'gnuplot_for_dtiqc_bad.png\'\n'
                             'replot\n')

            else:
                bad_qc.write('plot for [n=2:'+str(num_badvols + 1)+'] \'./plotbad1.txt\' u 1:(column(n)) w lines lw 4\n'
                             'set terminal png size 1200, 800 font 12\n'
                             'set output \'gnuplot_for_dtiqc_bad.png\'\n'
                             'replot\n')

        with open('gnuplot_for_dtiqc_good.txt', mode='a') as good_qc:
            good_qc.write('#!/usr/bin/gnuplot\n')
            good_qc.write('reset\n')
            good_qc.write('set title \'' + output_pname.parts[-5] + ' ' + output_pname.parts[-4] + ' DTI QC shows '+str(num_goodvols)+' GOOD vols for '+str(output_pname.name).split('_')[-1]+'\' font \"Helvetica,24\"\n')
            good_qc.write(gnuplot_cmds_part2)
            good_qc.write('plot for [n=2:' + str(num_goodvols + 1) + '] \'./plotgood1.txt\' u 1:(column(n)) w lines lw 4\n'
                              'set terminal png size 1200, 800 font 12\n'
                              'set output \'gnuplot_for_dtiqc_good.png\'\n'
                              'replot\n')

        results += run_subprocess(['gnuplot gnuplot_for_dtiqc_bad.txt'])
        results += run_subprocess(['gnuplot gnuplot_for_dtiqc_good.txt'])
        try:
            Path('gnuplot_for_dtiqc_good.png').rename(appendposix(output_pname, '_good_plot.png'))
            Path('gnuplot_for_dtiqc_bad.png').rename(appendposix(output_pname, '_bad_plot.png'))
            Path('qc_report.txt').rename(appendposix(output_pname, '_report.txt'))
        except OSError:
            print(str(output_pname)+' files not found. moving on.')
    return badvols  # results dataframe
