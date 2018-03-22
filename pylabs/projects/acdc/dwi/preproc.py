# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
import os, itertools
from pathlib import *
from collections import defaultdict
import nipype
from nipype.interfaces import fsl
import nibabel as nib
import numpy as np
import pandas as pd
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
from dipy.reconst.dti import mode
import shutil
import datetime
from scipy.ndimage.filters import median_filter as medianf
from pylabs.structural.brain_extraction import extract_brain
from pylabs.conversion.brain_convert import conv_subjs
from pylabs.conversion.nifti2nrrd import nii2nrrd
from pylabs.conversion.parrec2nii_convert import mergeddicts
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.correlation.atlas import mori_network_regions
from pylabs.io.images import savenii
from pylabs.io.mixed import h52df
from pylabs.utils import *
#set up provenance
from pylabs.utils import ProvenanceWrapper
prov = ProvenanceWrapper()

# project, subject, and file objects to work on
from pylabs.projects.acdc.file_names import project, SubjIdPicks, get_dwi_names, Optsd

#setup paths and file names to process
fs = Path(getnetworkdataroot())

antsRegistrationSyN = get_antsregsyn_cmd()
slicer_path = getslicercmd()
opts = Optsd()
dwi_qc = True
if not dwi_qc:
    opts.dwi_pass_qc = ''

# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = [
         {'subj': 'sub-acdc117', 'session': 'ses-1', 'run': '1',  # subject selection info
          },
         ]

setattr(subjids_picks, 'subjids', picks)

# topup command for unwarping dti
topup_cmd = 'topup --imain={topup_dn_fname} --datain=acq_params.txt --config=b02b0.cnf --out={topup_out}'
topup_cmd += ' --iout={topup_out}_unwarped.nii.gz --fout={topup_out}_topdn_concat_mf_warp_field.nii.gz'
# makes mean of unwarped topup down b0 for brain extraction, mask, b0
mean_b0_cmd = 'fslmaths {topup_out}_unwarped -Tmean {topup_out}_unwarped_mean.nii.gz'
# fsl eddy cmd using cuda for speedup
eddy_cmd = 'eddy_cuda7.5 --imain={dwif_fname} --mask={b0_brain_mask_fname} --acqp=../acq_params.txt  --index=../index.txt'
eddy_cmd += ' --bvecs={dwi_bvecs_fname} --bvals={dwi_bvals_fname} --topup={topup_out} --repol --ol_nstd=1.96 --out={ec_dwi_fname}'
# fsl dtifit command to make FA, MD maps etc.
fsl_fit_cmd = 'dtifit -k {ec_dwi_clamp_fname} -o {fsl_fits_out} -m {b0_brain_mask_fname} -b {dwi_bvals_fname}'
fsl_fit_cmd += ' -r {dwi_bvecs_ec_rot_fname} --save_tensor --wls --sse'

# slicer UKF commands and default parameters to run
ukfcmds =  {'UKF_whbr': str(slicer_path) + 'UKFTractography --dwiFile %(dwi_nrrd_fname)s --seedsFile %(b0_brain_mask_fname)s'
                    ' --labels 1 --maskFile %(b0_brain_mask_fname)s --tracts %(ec_dwi_fname)s_mf_clamp1_UKF_whbr.vtk'
                    ' --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.2 --numThreads -1 --numTensor 2 --stepLength 0.3'
                    ' --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --recordNMSE --freeWater'
                    ' --recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004'
                    ' --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0',
            'NODDI': str(slicer_path) + 'UKFTractography --dwiFile %(dwi_nrrd_fname)s --seedsFile %(b0_brain_mask_fname)s'
                    ' --labels 1 --maskFile %(b0_brain_mask_fname)s --tracts %(ec_dwi_fname)s_mf_clamp1_whbr_1tensor_noddi.vtk'
                    ' --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 1 --stepLength 0.3'
                    ' --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --Ql 0 --Qw 0 --noddi --recordVic --recordKappa --recordViso'
                    ' --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0'
            }
# to get indices of upper triangle of tensor for fsl compat
_ut_rows = np.array([0, 0, 0, 1, 1, 2])
_ut_cols = np.array([0, 1, 2, 1, 2, 2])
_all_cols = np.zeros(9, dtype=np.int)
_all_rows = np.zeros(9, dtype=np.int)
for i, j in enumerate(list(itertools.product(*(range(3), range(3))))):
    _all_rows[i] = int(j[0])
    _all_cols[i] = int(j[1])

# define local functions
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d

def test4file(file):
    file = Path(file)
    if file.is_file():
        return True
    else:
        raise ValueError(str(file) + ' not found.')


#  define hostnames with working gpus for processing
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI_GZ')
if nipype.__version__ == '0.12.0':
    applyxfm = fsl.ApplyXfm(interp='nearestneighbour', output_type='NIFTI_GZ')
else:
    applyxfm = fsl.ApplyXFM(interp='nearestneighbour', output_type='NIFTI_GZ')

print(os.environ['FSLOUTPUTTYPE'])

# move to opts settings
# other future stages to run
subT2 = False   #wip
b1corr = False
bet = False
prefilter = False
templating = False

"""
i = 0
topup, topdn, dwif = topup_fnames[i], topdn_fnames[i], dwi_fnames[i]

dwipath = fs / project / picks[i]['subj'] / picks[i]['session'] / 'dwi'
orig_dwi_data = nib.load(str(dwipath / (dwi_fnames[i]+'.nii'))).get_data()
voli = range(orig_dwi_data.shape[3])
good_voli = list(set(voli) - set(picks[i]['dwi_badvols']))
good_dwi_data = orig_dwi_data[:,:,:,good_voli]
orig_bvecs = pd.read_csv(str(dwipath / (dwi_fnames[i]+'.bvecs')), header=None, delim_whitespace=True)
orig_bvals = pd.read_csv(str(dwipath / (dwi_fnames[i]+'.bvals')), header=None, delim_whitespace=True)
good_bvecs = orig_bvecs.iloc[:, good_voli]
good_bvals = orig_bvals.iloc[:, good_voli]
good_bvecs.to_csv(str(dwipath/ (dwi_fnames[i]+'_selected_vols.bvecs')), header=None, index=None, sep=' ', float_format='%.4f')
good_bvals.to_csv(str(dwipath/ (dwi_fnames[i]+'_selected_vols.bvals')), header=None, index=None, sep=' ', float_format='%.4f')
nib.save(nib.Nifti1Image(good_dwi_data,  nib.load(str(dwipath / (dwi_fnames[i]+'.nii'))).affine), str(dwipath / (dwi_fnames[i]+'_selected_vols.nii')))

orig_dwif_fname = dwipath / str(dwif + opts.dwi_pass_qc+'.nii')
dwi_bvals_fname = dwipath / str(dwif + opts.dwi_pass_qc+'.bvals')
dwi_bvecs_fname = dwipath / str(dwif + opts.dwi_pass_qc+'.bvecs')
# pick up at dwi_dwellt_fname below

to do:
UKF command to modify 
/home/toddr/.config/NA-MIC/Extensions-26072/UKFTractography/lib/Slicer-4.7/cli-modules/UKFTractography 
--dwiFile /tmp/Slicer/CGGHB_vtkMRMLDiffusionWeightedVolumeNodeB.nhdr --seedsFile /tmp/Slicer/CGGHB_vtkMRMLLabelMapVolumeNodeB.nhdr --labels 1 --maskFile /tmp/Slicer/CGGHB_vtkMRMLLabelMapVolumeNodeB.nhdr --tracts /tmp/Slicer/CGGHB_vtkMRMLFiberBundleNodeB.vtp --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 2 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --recordNMSE --freeWater --recordFA --recordTrace --recordFreeWater --recordTensors --Ql 0 --Qw 0 --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 
NODDI Command to modify
/home/toddr/.config/NA-MIC/Extensions-26072/UKFTractography/lib/Slicer-4.7/cli-modules/UKFTractography --dwiFile /tmp/Slicer/CECH_vtkMRMLDiffusionWeightedVolumeNodeB.nhdr --seedsFile /tmp/Slicer/CECH_vtkMRMLLabelMapVolumeNodeB.nhdr --labels 1 --maskFile /tmp/Slicer/CECH_vtkMRMLLabelMapVolumeNodeB.nhdr --tracts /tmp/Slicer/CECH_vtkMRMLFiberBundleNodeB.vtp --seedsPerVoxel 1 --seedFALimit 0.18 --minFA 0.15 --minGA 0.1 --numThreads -1 --numTensor 1 --stepLength 0.3 --Qm 0 --recordLength 1.8 --maxHalfFiberLength 250 --Ql 0 --Qw 0 --noddi --recordVic --recordKappa --recordViso --Qkappa 0.01 --Qvic 0.004 --Rs 0 --sigmaSignal 0 --maxBranchingAngle 0 --minBranchingAngle 0 
"""


# run conversion if needed
# if convert:
#     subjects = [x['subj'] for x in subjids_picks.subjids]
#     niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#     niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)

picks =  get_dwi_names(subjids_picks)

# i = 0
# pick = picks[i]

"""
pick dict guide:
'subj' = subject being processed
'session' = session being processed
topup_dn_fname = combined topup and topdown pre unwarping
topup_out = topup out file basename for unwarping

dwi_fname = dwi file name to be processed if qc then opts.dwi_pass_qc appended to name
'ec_dwi_fname' = eddy current corrected dwi file for fits and bedpost
dwi_bvecs_ec_rot_fname = ec rotated bvecs to be used for fits, bedpost etc
"""

for i, pick in enumerate(picks):
    result = ()
    dwipath = fs / project / '{subj}/{session}/dwi'.format(**pick)
    regpath = fs / project / '{subj}/{session}/reg'.format(**pick) / opts.dwi_reg_dir
    ec_dir = dwipath / opts.eddy_corr_dir
    bedpost_dir = dwipath / opts.dwi_bedpost_dir
    fits_dir = dwipath / opts.dwi_fits_dir
    if not ec_dir.is_dir():
        ec_dir.mkdir(parents=True)
    if not regpath.is_dir():
        regpath.mkdir(parents=True)
    # define files
    orig_dwif_fname = dwipath / '{dwi_fname}.nii'.format(**pick)
    orig_dwi_bvals_fname = dwipath / '{dwi_fname}.bvals'.format(**pick)
    orig_dwi_bvecs_fname = dwipath / '{dwi_fname}.bvecs'.format(**pick)
    dwi_dwellt_fname = dwipath / '{dwi_fname}.dwell_time'.format(**pick)
    orig_topup_fname = dwipath / '{topup_fname}.nii'.format(**pick)
    orig_topdn_fname = dwipath / '{topdn_fname}.nii'.format(**pick)
    topup_dwellt_fname = dwipath / '{topup_fname}.dwell_time'.format(**pick)
    topdn_dwellt_fname = dwipath / '{topdn_fname}.dwell_time'.format(**pick)
    # test they exist
    for f in [orig_dwif_fname, orig_dwi_bvals_fname, orig_dwi_bvecs_fname, dwi_dwellt_fname, orig_topup_fname,
              topup_dwellt_fname, orig_topdn_fname, topdn_dwellt_fname]:
        test4file(f)
    # get data
    orig_dwi_img = nib.load(str(orig_dwif_fname))
    orig_dwi_data = orig_dwi_img.get_data()
    orig_dwi_affine = orig_dwi_img.affine
    orig_topup_img = nib.load(str(orig_topup_fname))
    orig_topup_data = orig_topup_img.get_data()
    orig_topup_affine = orig_topup_img.affine
    orig_topdn_img = nib.load(str(orig_topdn_fname))
    orig_topdn_data = orig_topdn_img.get_data()
    orig_topdn_affine = orig_topdn_img.affine

    if dwi_qc:
        vis_qc = h52df(opts.info_fname, '/{subj}/{session}/dwi/vis_qc'.format(**pick))
        vis_qc.replace({'True': True, 'False': False}, inplace=True)
        dwi_good_vols = vis_qc[vis_qc.dwi_visqc]
        topup_goodvols = vis_qc[vis_qc.itopup_visqc]
        topdn_goodvols = vis_qc[vis_qc.itopdn_visqc]
        qc_dwi_data = orig_dwi_data[:, :, :, np.array(dwi_good_vols.index)]
        dwif_fname = appendposix(orig_dwif_fname, opts.dwi_pass_qc)
        pick['dwif_fname'] = dwif_fname
        dwi_bvals_fname = appendposix(orig_dwi_bvals_fname, opts.dwi_pass_qc)
        pick['dwi_bvals_fname'] = dwi_bvals_fname
        dwi_bvecs_fname = appendposix(orig_dwi_bvecs_fname, opts.dwi_pass_qc)
        pick['dwi_bvecs_fname'] = dwi_bvecs_fname
        topup_fname = appendposix(orig_topup_fname, opts.dwi_pass_qc)
        topdn_fname = appendposix(orig_topdn_fname, opts.dwi_pass_qc)
        savenii(qc_dwi_data, orig_dwi_affine, dwif_fname)
        dwi_good_vols[[u'x_bvec', u'y_bvec', u'z_bvec']].T.to_csv(str(dwi_bvecs_fname), index=False, header=False, sep=' ')
        pd.DataFrame(dwi_good_vols[u'bvals']).T.to_csv(str(dwi_bvals_fname), index=False, header=False, sep=' ')
        bvecs = dwi_good_vols[[u'x_bvec', u'y_bvec', u'z_bvec']].T.values
        bvals = pd.DataFrame(dwi_good_vols[u'bvals']).T.values[0]
        gtab = gradient_table(bvals, bvecs)
        #add topup and dn qc vols select
        topup_data = orig_topup_data[:,:,:,np.array(topup_goodvols.index)]
        topdn_data = orig_topdn_data[:, :, :, np.array(topdn_goodvols.index)]
        savenii(topup_data, orig_topup_affine, topup_fname)
        savenii(topdn_data, orig_topdn_affine, topdn_fname)

    else:
        bvals, bvecs = read_bvals_bvecs(str(orig_dwi_bvals_fname), str(orig_dwi_bvecs_fname))
        gtab = gradient_table(bvals, bvecs)
        dwif_fname = orig_dwif_fname
        pick['dwif_fname'] = dwif_fname
        dwi_bvals_fname = orig_dwi_bvals_fname
        dwi_bvecs_fname =orig_dwi_bvecs_fname
        topup_fname = orig_topup_fname
        topdn_fname = orig_topdn_fname
        topup_data = orig_topup_data
        topdn_data = orig_topdn_data

    # make acq_params and index files for fsl eddy
    with open(str(topup_dwellt_fname), 'r') as tud:
        topup_dwellt = tud.read().replace('\n', '')

    with open(str(topdn_dwellt_fname), 'r') as tdd:
        topdn_dwellt = tdd.read().replace('\n', '')

    topup_numlines = (nib.load(str(topup_fname))).header['dim'][4]
    topdn_numlines = (nib.load(str(topdn_fname))).header['dim'][4]

    with open(str(dwipath / 'acq_params.txt'), 'w') as ap:
        for x in range(topup_numlines):
            ap.write('0 1 0 ' + topup_dwellt + '\n')
        for x in range(topdn_numlines):
            ap.write('0 -1 0 ' + topdn_dwellt + '\n')


    # topup distortion correction
    if opts.run_topup or opts.overwrite:
        topup_dn_data_concat = np.concatenate((topup_data, topdn_data), axis=3)
        topup_dn_data_concat_mf = medianf(topup_dn_data_concat, size=3)
        pick['topup_dn_fname'] = dwipath / '{topup_fname}_topdn_concat_mf.nii.gz'.format(**pick)
        pick['topup_out'] = dwipath / '{topup_fname}_topdn_concat_mf'.format(**pick)
        savenii(topup_dn_data_concat_mf, orig_topup_affine, str(pick['topup_dn_fname']))
        prov.log(str(pick['topup_dn_fname']), 'concatenated topup-dn S0 vols', [str(topup_fname), str(topdn_fname)])

        with WorkingContext(str(dwipath)):
            with open('index.txt', 'w') as f:
                f.write('1 ' * len(gtab.bvals))
            result += run_subprocess([topup_cmd.format(**pick)])
            result += run_subprocess([mean_b0_cmd.format(**pick)])
            prov.log('{topup_out}_unwarped_mean.nii.gz'.format(**pick), 'median filtered mean of topup-dn S0 vols', [str(topup_fname), str(topdn_fname)])


    # eddy current correction
    pick['ec_dwi_fname'] = ec_dir / '{dwi_fname}_topdn_unwarped_ec'.format(**pick)
    pick['dwi_bvecs_ec_rot_fname'] = '{ec_dwi_fname}.eddy_rotated_bvecs'.format(**pick)
    if opts.eddy_corr or opts.overwrite:
        with WorkingContext(str(ec_dir)):
            b0_brain_fname, b0_brain_mask_fname, b0_brain_cropped_fname = extract_brain('{topup_out}_unwarped_mean.nii.gz'.format(**pick))
            pick['b0_brain_mask_fname'] = b0_brain_mask_fname
            result += run_subprocess([eddy_cmd.format(**pick)])
            # clamp, filter, and make nrrd
            ec_data = nib.load('{ec_dwi_fname}.nii.gz'.format(**pick)).get_data()
            ec_data_affine = nib.load('{ec_dwi_fname}.nii.gz'.format(**pick)).affine
            bvals, ec_bvecs = read_bvals_bvecs(str(pick['dwi_bvals_fname']), pick['dwi_bvecs_ec_rot_fname'])
            ec_gtab = gradient_table(bvals, ec_bvecs)
            if opts.mf_str != '':
                S0 = ec_data[:, :, :, gtab.b0s_mask]
                S0_mf = medianf(S0, size=3)
                ec_data[:, :, :, gtab.b0s_mask] = S0_mf
            ec_data[ec_data <= 0.1] = 0
            pick['ec_dwi_clamp_fname'] = '{ec_dwi_fname}{mf_str}_clamp1.nii.gz'.format(**mergeddicts(pick, vars(opts)))
            savenii(ec_data, ec_data_affine, pick['ec_dwi_clamp_fname'])
            prov.log(pick['ec_dwi_clamp_fname'], 'median filtered mean of topup-dn S0 vols clamped','{ec_dwi_fname}.nii.gz'.format(**pick))
            nii2nrrd(pick['ec_dwi_clamp_fname'], str(replacesuffix(pick['ec_dwi_clamp_fname'], '.nhdr')), bvalsf=pick['dwi_bvals_fname'], bvecsf=pick['dwi_bvecs_ec_rot_fname'])
            pick['dwi_nrrd_fname'] = replacesuffix(pick['ec_dwi_clamp_fname'], '.nhdr')
            prov.log(str(replacesuffix(pick['ec_dwi_clamp_fname'], '.nhdr')), 'nrrd converted median filtered mean of topup-dn S0 vols', pick['ec_dwi_clamp_fname'])


    # do fsl fits and dipy fits
    if not (dwipath / opts.dwi_fits_dir).is_dir():
        (dwipath / opts.dwi_fits_dir).mkdir()
    pick['fsl_fits_out'] = dwipath / opts.dwi_fits_dir / '{subj}_{session}_dwi_unwarped_ec_fslfit'.format(**pick)
    pick['dipy_fits_out'] = dwipath / opts.dwi_fits_dir / '{subj}_{session}_dwi_unwarped_ec_dipyfit'.format(**pick)
    with WorkingContext(str(dwipath / opts.dwi_fits_dir)):
        # do fsl dtifit cmd
        result += run_subprocess([fsl_fit_cmd.format(**pick)])
        # do dipy fits
        tenmodel = dti.TensorModel(ec_gtab, fit_method='WLS')
        data = nib.load(pick['ec_dwi_clamp_fname']).get_data()
        affine = nib.load(pick['ec_dwi_clamp_fname']).affine
        mask = nib.load(str(pick['b0_brain_mask_fname'])).get_data()
        fit = tenmodel.fit(data, mask)
        # filter and save all dipy files
        fit_quad_form = fit.quadratic_form
        fit_quad_form_mf = np.zeros(fit_quad_form.shape)
        for r, c in zip(_all_rows, _all_cols):
            fit_quad_form_mf[..., r, c] = medianf(fit_quad_form[..., r, c], size=1, mode='constant', cval=0)
        tensor_ut = fit_quad_form[..., _ut_rows, _ut_cols]
        tensor_ut_mf = fit_quad_form_mf[..., _ut_rows, _ut_cols]
        savenii(tensor_ut, affine, '{dipy_fits_out}_tensor.nii'.format(**pick))
        savenii(tensor_ut_mf, affine, '{dipy_fits_out}_tensor_mf.nii'.format(**pick))
        nii2nrrd('{dipy_fits_out}_tensor_mf.nii'.format(**pick), '{dipy_fits_out}_tensor_mf.nhdr'.format(**pick), istensor=True)
        savenii(fit.fa, affine,'{dipy_fits_out}_FA.nii'.format(**pick), minmax=(0, 1))
        savenii(fit.md, affine, '{dipy_fits_out}_MD.nii'.format(**pick))
        savenii(fit.rd, affine, '{dipy_fits_out}_RD.nii'.format(**pick))
        savenii(fit.ad, affine, '{dipy_fits_out}_AD.nii'.format(**pick))
        savenii(fit.mode, affine, '{dipy_fits_out}_MO.nii'.format(**pick), minmax=(-1, 1))
        # calculate eigenvalues for median filtered tensor and then FA, MD, RD etc and save
        evals, evecs = np.linalg.eigh(fit_quad_form_mf)
        evals = np.rollaxis(evals, axis=-1)  # order evals
        all_zero = (evals == 0).all(axis=0)  # remove NaNs
        ev1, ev2, ev3 = evals  # need to test if ev1 > ev2 > ev3
        fa_mf = np.sqrt(0.5 * ((ev1 - ev2) ** 2 +
                               (ev2 - ev3) ** 2 +
                               (ev3 - ev1) ** 2) /
                        ((evals * evals).sum(0) + all_zero))
        savenii(fa_mf, affine, '{dipy_fits_out}_mf_FA.nii'.format(**pick), minmax=(0, 1))
        savenii(evals.mean(0), affine, '{dipy_fits_out}_mf_MD.nii'.format(**pick))
        savenii(ev1, affine, '{dipy_fits_out}_mf_AD.nii'.format(**pick))
        savenii(evals[1:].mean(0), affine, '{dipy_fits_out}_mf_RD.nii'.format(**pick))
        savenii(mode(fit_quad_form_mf), affine, '{dipy_fits_out}_mf_MO.nii'.format(**pick), minmax=(-1, 1))

    if opts.do_ukf:
        try:
            with WorkingContext(str(ec_dir)):
                result += run_subprocess([ukfcmds['UKF_whbr'] % pick])
                result += run_subprocess([ukfcmds['NODDI'] % pick])
        except:
            print('ukf failed to run with {slicer}'.format(**{'slicer': slicer_path}))

    # bedpost input files and execute (hopefully) on gpu
    if opts.run_bedpost or opts.overwrite:
        if not bedpost_dir.is_dir():
            bedpost_dir.mkdir()
        with WorkingContext(str(bedpost_dir)):
            shutil.copy(pick['ec_dwi_clamp_fname'], str(bedpost_dir))
            os.rename(Path(pick['ec_dwi_clamp_fname']).name, str(bedpost_dir/'data.nii.gz'))
            shutil.copy(pick['dwi_bvecs_ec_rot_fname'], str(bedpost_dir))
            os.rename(Path(pick['dwi_bvecs_ec_rot_fname']).name, str(bedpost_dir/'bvecs'))
            shutil.copy(str(pick['dwi_bvals_fname']), str(bedpost_dir))
            os.rename(Path(pick['dwi_bvals_fname']).name, str(bedpost_dir/'bvals'))
            shutil.copy(str(pick['b0_brain_mask_fname']), str(bedpost_dir))
            os.rename(pick['b0_brain_mask_fname'].name, str(bedpost_dir/'nodif_brain_mask.nii.gz'))
            # run bedpost, probtracks, network, UKF, NODDI, and DKI here
            with WorkingContext(str(dwipath)):
                if test4working_gpu():
                    result += run_subprocess(['bedpostx_gpu bedpost -n 3 --model=2'])
                    # what cleanup is required?
                else:
                    result += run_subprocess(['bedpostx bedpost -n 3 --model=2'])


####################### end here for now


    # use ants to warp mori atlas into subj space
    if not test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) or (test4file(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')) & overwrite):
        with WorkingContext(regpath):
            MNI2b0_brain_antscmd = [str(antsRegistrationSyN), '-d 3 -m', str(MNI1mm_T2_brain), '-f',str(b0_brain_fname), '-o',
                                    str(regpath / replacesuffix(MNI1mm_T2_brain, '_reg2dwi_').name),'-n 30 -t s -p f -j 1 -s 10 -r 1']
            result += run_subprocess([' '.join(MNI2b0_brain_antscmd)])
            warpfiles = [regpath/replacesuffix(moriMNIatlas, '_reg2dwi_1Warp.nii.gz'),]
            affines = [regpath/replacesuffix(moriMNIatlas, '_reg2dwi_0GenericAffine.mat'),]
            subj2templ_applywarp(str(moriMNIatlas), str(b0_brain_fname), str(regpath/replacesuffix(moriMNIatlas.name, '_reg2dwi.nii.gz')), warpfiles=warpfiles, regpath, affine_xform=affines)
            subj2templ_applywarp(str(MNI1mm_T1_brain), str(b0_brain_fname), str(regpath/replacesuffix(MNI1mm_T1_brain.name, '_reg2dwi.nii.gz')), warpfiles=warpfiles, regpath, affine_xform=affines)




    cmdvars = {'fdwinrrd': str(ec_dwi_name)+mf_str+'_clamp1.nhdr',
               'mask_fnamenrrd': str(dwipath/str(topup + '_topdn_concat_mf_unwarped_mean_brain_mask.nii.gz')),
               'dwif': str(fits_dir/dwif)}



'''
warp MNI_T1 to dwi for mricros :done
loop over mori to gen seed bin mask and dilate and get com coord and put subject.node 
probtracts cmd:
probtrackx2 --network -x listseeds.txt  -l --onewaycondition --omatrix1 -c 0.2 -S 1000 --steplength=0.5 -P 1000 --fibthresh=0.01 --distthresh=0.0 --sampvox=0.0 --forcedir --opd -s bedpost.bedpostX/merged -m bedpost.bedpostX/nodif_brain_mask  --dir=probtrackoutput


subject.node is row by row x y z center of mass coordinate for each seed plus 3 3 3 (space separated
150 130 48 3 3 3\n # for seed001.nii.gz
matrix2 = for loop by row matrix / waytotal to normalise and rename to .edge
this is the input for mricros 
'''