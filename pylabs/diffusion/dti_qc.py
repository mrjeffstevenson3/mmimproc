import glob, os, pandas, numpy, niprov, nibabel, cPickle, shutil
from os.path import join
from collections import defaultdict
from nipype.interfaces import fsl
from pylabs.utils._run import run_subprocess
from pylabs.utils.paths import getnetworkdataroot
prov = niprov.ProvenanceContext()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo')
applyxfm = fsl.ApplyXfm()
fs = getnetworkdataroot()
alpha = 3.4


def dti_motion_qc(project, subjects, alpha):
    origdir = os.getcwd()
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
            os.chdir(qcdir)
            with open(join(qcdir, 'alphalevel.txt'), "w") as alphalevel:
                alphalevel.write("{}".format(alpha))
            cmd = ['fslchfiletype', 'ANALYZE', join(qcdir, 'dtishort.nii')]
            run_subprocess(' '.join(cmd))
            run_subprocess(join(origdir, 'pylabs/diffusion/dti_qc_correlation_bval1000'))
    os.chdir(origdir)
    return
