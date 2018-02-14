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
        results += run_subprocess(['octave '+str(plot_vols)])
        badvols = pd.read_csv('bad_vols_index.txt', header=None, delim_whitespace=True,
                              index_col=0)
    return badvols  # results dataframe
