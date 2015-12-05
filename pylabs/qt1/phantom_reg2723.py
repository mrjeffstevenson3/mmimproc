import os, sys
from glob import glob
from os.path import join as pathjoin
from nipype.interfaces.freesurfer import MRIConvert
from pylabs.utils.paths import getlocaldataroot

mc = MRIConvert()
fs = getlocaldataroot()
inxfmfiles = glob(pathjoin(fs, 'phantom_qT1_disc/T1_seir_mag_TR4000_regto723/*.lta'))
indirseir = pathjoin(fs, 'phantom_qT1_disc/T1_seir_mag_TR4000')
indirspgr = pathjoin(fs, 'phantom_qT1_disc/T1_orig_spgr_mag_TR11p0')
outdirseir = pathjoin(fs, 'phantom_qT1_disc/T1_seir_mag_TR4000_regto723_dec4')
outdirspgr =  pathjoin(fs, 'phantom_qT1_disc/T1_orig_spgr_mag_TR11p0_regto723_dec4')
if not os.path.exists(outdirseir):
    os.mkdir(outdirseir)
if not os.path.exists(outdirspgr):
    os.mkdir(outdirspgr)
if not os.path.exists(outdirseir+'_b1corr'):
    os.mkdir(outdirseir+'_b1corr')
if not os.path.exists(outdirspgr+'_b1corr'):
    os.mkdir(outdirspgr+'_b1corr')
fnameprependseir = 'T1_seir_mag_TR4000_'
fnameappend= '_1'
fnameprependspgr = 'T1_orig_spgr_mag_TR11p0_'
fext = '.nii.gz'
#inxfmfiles = inxfmfiles[25]
for xfile in inxfmfiles:
    fname = fnameprependseir + xfile.split('_')[-2] + fnameappend
    if os.path.isfile(pathjoin(indirseir, fname + fext)):
        mc.inputs.apply_transform = xfile
        mc.inputs.in_file = pathjoin(indirseir, fname + fext)
        mc.inputs.out_file = pathjoin(outdirseir, fname + fext)
        mc.run()
        mc.inputs.apply_transform = xfile
        mc.inputs.in_file = pathjoin(indirseir, fname + '_b1corr' + fext)
        mc.inputs.out_file = pathjoin(outdirseir+'_b1corr', fname + '_b1corr' + fext)
        mc.run()
    fname = fnameprependspgr + xfile.split('_')[-2] + fnameappend
    if os.path.isfile(pathjoin(indirspgr, fname + fext)):
        mc.inputs.apply_transform = xfile
        mc.inputs.in_file = pathjoin(indirspgr, fname + fext)
        mc.inputs.out_file = pathjoin(outdirspgr, fname + fext)
        mc.run()
        mc.inputs.apply_transform = xfile
        mc.inputs.in_file = pathjoin(indirspgr, fname + '_b1corr' + fext)
        mc.inputs.out_file = pathjoin(outdirspgr+'_b1corr', fname + '_b1corr' + fext)
        mc.run()
