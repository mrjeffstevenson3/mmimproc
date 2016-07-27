import glob, os, pandas, numpy, niprov, nibabel, cPickle, shutil, pylabs
from os.path import join
from collections import defaultdict
from nipype.interfaces import fsl
from pylabs.utils._run import run_subprocess
from pylabs.utils.paths import getnetworkdataroot, getpylabspath
prov = niprov.ProvenanceContext()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo')
applyxfm = fsl.ApplyXfm()
fs = getnetworkdataroot()
alpha = 3.4


def dti_motion_qc(project, subjects, alpha=3.4):
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
            shutil.copy2(join(origdir, 'pylabs/diffusion/plotqc1.m'), join(qcdir, 'plotqc1.m'))
            os.chdir(qcdir)
            with open(join(qcdir, 'alphalevel.txt'), "w") as alphalevel:
                alphalevel.write("{}".format(alpha))
            cmd = 'fslchfiletype ANALYZE ' + join(qcdir, 'dtishort.nii')
            run_subprocess(cmd)
            run_subprocess(join(diffdir, 'dti_qc_correlation_bval1000'))
    os.chdir(origdir)
    return
