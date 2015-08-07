import os, glob
from os.path import join
import niprov
from pylabs.utils.paths import getlocaldataroot
from niprov.options import NiprovOptions
from pylabs.vbm.upsample import upsample1mm
opts = NiprovOptions()
opts.dryrun = True
opts.verbose = True

fs = getlocaldataroot()
resultdir = join(fs,'self_control/hbm_group_data/mmpa/')
images = []

## Behavior
behavdir = join(fs,'self_control/behavioral_data/behav_from_andy_march27_2015/')
csvfile = join(behavdir,'EF_and_Brain_july08_2015_Meq0_delta.csv')
niprov.add(csvfile)

## VBM
vbmdir = join(fs,'self_control/hbm_group_data/vbm_15subj/workdir_v1/stats/')
images += glob.glob(join(vbmdir, '?M_mod_merg_s4.nii.gz'))
# selectedCorrPfiles1mm = upsample1mm(selectedCorrPfiles, opts=opts)

## TBSS
tbssdir = join(fs,'self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/')
imgtemplate = 'all_{0}_skeletonised.nii.gz'
measures = ['F1', 'F2', 'FA', 'L1', 'MD', 'MO', 'RA', 'AD', 'L2', 'L3']
skellist = [imgtemplate.format(m) for m in measures]
images += [join(tbssdir,i) for i in skellist]

## FMRI
fmridir = join(fs,'self_control/hbm_group_data/fmri')
images += glob.glob(join(fmridir, 'analyze', '*_Congruent_gt_Incongruent.hdr'))

## MM
#[niprov.add(img) for img in images]
for i in images:
    print(i)



