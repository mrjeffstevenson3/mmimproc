# 1st attempt at qt1 test retest cross validation
#####====== part 1 =========
# 1. run freesurf on all to get b1map phase. done
# 2. reg with ants all spgr and b1map for both sessions and between sessions (use fa 05 as ref)
# 3. fit both sessions both subjects qt1 with fitT1WholeBrain() using whole head mask with vial
# 4. cross validation with vial fits on neck
####====== part 2 ==========
# 5. setup and convert all phantoms
# 6. extract midline slices
# 7. fit all phantoms spgr and IR/IRTSE
# 8. register all phantoms
# 9. extract all values
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import pandas as pd
import numpy as np
import nibabel as nib
import matlab.engine
from scipy import stats
from dipy.segment.mask import applymask
from scipy.ndimage.morphology import binary_erosion as ero
from scipy.ndimage.measurements import center_of_mass as com
from pylabs.alignment.resample import reslice_roi
from pylabs.alignment.ants_reg import subj2templ_applywarp
from pylabs.alignment.phantom import align, transform
from pylabs.fmap_correction.b1_map_corr import correct4b1
from pylabs.structural.brain_extraction import extract_brain
from pylabs.qt1.fitting import t1fit
from pylabs.qt1.model_pipeline import calculate_model, vialsInOrder
from pylabs.io.images import savenii
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix, getnetworkdataroot, get_antsregsyn_cmd, getspmpath, pylabs_dir
from scipy.ndimage.filters import median_filter as medianf
from pylabs.projects.genz.file_names import project, get_5spgr_names, SubjIdPicks
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
spm_dir, tpm_path = getspmpath()

eng = matlab.engine.start_matlab()
eng.addpath(eng.genpath(str(pylabs_dir)))
eng.addpath(eng.genpath(str(spm_dir)))


bias_corr_cmd = str(get_antsregsyn_cmd(N4bias=True))
bias_corr_cmd += ' -d 3 -i '

# fit methods options are direct, linlstsq, and linregr

scanner = 'slu'
scanner_dir = fs/'phantom_qT1_{}'.format(scanner)
vials_incr_t1 = [8, 7, 10, 9, 11, 13, 14, 15, 17, 16, 18, 12]


phant_act = pd.DataFrame(calculate_model(scanner)).astype('float')
vial_map = {}
for i, v in zip(range(0,len(vialsInOrder)), vialsInOrder):
    vial_map[i] = v
phant_act.rename(index=vial_map, inplace=True)
phant_act.index.rename('vial_num', inplace=True)

ref_phant = 'sub-phant2017-10-19'

def get_exam_date_time(parfile):
    par_date_time = nib.load(str(parfile)).header.general_info['exam_date']
    return pd.to_datetime(par_date_time)


par_files = [fs/'genz'/'sub-genz996/ses-2/phantom_parrec/sub-genz996_oct24_2017_phantom_WIP_T1_MAP_05_SENSE_4_1.PAR',
    fs/'phantom_qT1_slu/sub-phant2017-10-19/source_parrec/sub-genz996_PHANTOM_WIP_T1_MAP_05_SENSE_4_1.PAR',]

# phantoms processed
for par_file in par_files:

    phant_name = 'sub-phant{}'.format(get_exam_date_time(par_file).strftime('%Y'+'-'+'%m'+'-'+'%d'))

    b1map_dir = scanner_dir / phant_name / 'fmap'
    spgr_dir = scanner_dir / phant_name / 'qt1'
    b1map_file = b1map_dir / (phant_name + '_b1map_1.nii')
    spgr_files = sorted(list(spgr_dir.glob(phant_name+'_spgr_fa_??_tr_12p0_1.nii')), key=lambda fa: int(fa.stem.split('_')[3]))
    mask_img = nib.load(str(spgr_files[1]))
    mask_data = mask_img.get_data()
    mask_affine = mask_img.affine
    mask_zooms = mask_img.header.get_zooms()
    mask_data[mask_data < 6000] = 0
    mask_data[mask_data > 0] = 1
    mask_fname = spgr_files[1].parent/(phant_name+'_spgr_mask.nii')
    savenii(mask_data, nib.load(str(spgr_files[1])).affine, str(mask_fname))

    b1map_img = nib.load(str(b1map_file))
    b1map_data = b1map_img.get_data().astype('float32')
    b1map_affine = b1map_img.affine
    b1map_zooms = b1map_img.header.get_zooms()
    phase_data = b1map_data[:,:,:,2]
    phase_data_mf = medianf(phase_data, size=5)
    phase_data_mf_rs, new_affine = reslice_roi(phase_data_mf, b1map_affine, b1map_zooms[:3], mask_affine, mask_zooms)
    savenii(phase_data_mf_rs, mask_affine, str(appendposix(b1map_file, '_phase_mf')))



    TR = float(str(spgr_files[0].name).split('_')[5].replace('p','.'))

    if method == 'direct':
        outfile = str(spgr_dir / '{phant}_qT1_b1corr_5flip_direct.nii'.format(phant=phant_name))
        X = []
        for a in spgr_files:
            X.append(int(a.name.split('_')[3]))
        files = []
        for f in spgr_files:  # already sorted by flip angle
            files.append(f.as_posix())

        kwargs = {}
        kwargs['scantype'] = str(spgr_files[0].name).split('_')[1].upper()
        kwargs['TR'] = TR
        kwargs['t1filename'] = outfile
        if appendposix(b1map_file, '_phase_mf').is_file():
            kwargs['b1file'] = str(appendposix(b1map_file, '_phase_mf'))
        else:
            print('No B1 file for phantom {0}'.format(phant_name))
        if mask_fname.is_file():
            kwargs['maskfile'] = str(mask_fname)

        try:
            t1fit(files, X, **kwargs)
            kwargs['clamp'] = '1 to 6000'
            kwargs['erosion structure'] = (2,2,2)
            kwargs['flips'] = X
            kwargs['files'] = files
            qt1_data = nib.load(kwargs['t1filename']).get_data()
            mask_data = nib.load(kwargs['maskfile']).get_data().astype(int)
            qt1_data[qt1_data < 1] = 0
            qt1_data[qt1_data > 6000] = 6000
            mask_data = ero(mask_data, structure=np.ones((2,2,2))).astype(mask_data.dtype)
            qt1_clamped = applymask(qt1_data, mask_data)
            savenii(qt1_clamped, nib.load(kwargs['t1filename']).affine, str(appendposix(kwargs['t1filename'], '_clamped')))
            prov.log(str(appendposix(kwargs['t1filename'], '_clamped')), 'clamping qT1 fit', kwargs['t1filename'], #script=__file__,
                     provenance=dict(**kwargs))
        except Exception as ex:
            print('\n--> Error during fitting: ', ex)



with WorkingContext(str(fs/'phantom_qT1_{}'.format(scanner)/ref_phant/'qt1')):

    phant1019_img = nib.load('sub-phant2017-10-19_qT1_b1corr_5flip_clamped.nii')
    phant1024_img = nib.load('/Users/mrjeffs/Documents/Research/data/phantom_qT1_slu/sub-phant2017-10-24/qt1/sub-phant2017-10-24_qT1_b1corr_5flip_clamped.nii')
    phant1019_data = phant1019_img.get_data()
    phant1019_affine = phant1019_img.affine
    phant1024_data = phant1024_img.get_data()
    phant1024_affine = phant1024_img.affine
    phant1019_midslice = np.round(com(np.array(phant1019_data))).astype(int)
    phant1024_midslice = np.round(com(np.array(phant1024_data))).astype(int)
    phant1019_data_1slice = np.zeros(phant1019_data.shape)
    phant1019_data_1slice[:,:,120] = phant1019_data[:,:,phant1019_midslice[2]]
    phant1024_data_1slice = np.zeros(phant1019_data.shape)
    phant1024_data_1slice[:,:,120] = phant1024_data[:,:,phant1024_midslice[2]]
    savenii(phant1019_data_1slice, phant1019_affine, 'sub-phant2017-10-19_qT1_b1corr_5flip_clamped_midslice.nii')
    savenii(phant1024_data_1slice, phant1019_affine, 'sub-phant2017-10-24_qT1_b1corr_5flip_clamped_midslice.nii')

    # now loop over combs of offsets using align
    best_xform = align('sub-phant2017-10-24_qT1_b1corr_5flip_clamped_midslice.nii', 'sub-phant2017-10-19_qT1_b1corr_5flip_clamped_midslice.nii', delta=5)
    # can use savetransformed function in pylabs.alignment.phantom or
    phant1024_data_regto1019 = transform(phant1024_data, best_xform['tx'], best_xform['ty'], best_xform['rxy'])
    savenii(phant1024_data_regto1019, phant1019_affine, 'sub-phant2017-10-24_qT1_b1corr_5flip_clamped_midslice_regto1019.nii')
    # make, use, or define vial sampling mask
    phant_mask_data = nib.load('sub-phant2017-10-19_qT1_b1corr_5flip_clamped_midslice_mask.nii.gz').get_data()
    phant_spgr_dt = pd.DataFrame(index=vialsInOrder, columns=pd.to_datetime(['2017-10-19', '2017-10-24']), dtype='float')
    for i in vialsInOrder:
        phant_spgr_dt.loc[i,pd.to_datetime('2017-10-24')] = phant1024_data_regto1019[phant_mask_data == i].mean()
        print 'vial '+ str(i) + ' for 10-24:  '+str(stats.describe(phant1024_data_regto1019[phant_mask_data == i]))
        phant_spgr_dt.loc[i,pd.to_datetime('2017-10-19')] = phant1019_data_1slice[phant_mask_data == i].mean()
        print 'vial '+ str(i) + ' for 10-19:  '+str(stats.describe(phant1019_data_1slice[phant_mask_data == i]))


####  =====================    test of linearization for brain fiting ======================
# instantiate subject id list container
subjids_picks = SubjIdPicks()
# list of subject ids to operate on
picks = [
         {'subj': 'sub-genz996', 'session': 'ses-3', 'run': '1',},
         ]
setattr(subjids_picks, 'subjids', picks)
results = ()
b1corr = 'image'  # or 'fit' or None
b1map5_fnames, spgr5_fa05_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames = get_5spgr_names(subjids_picks)
reg_str = 'reg2spgr20'
datadir = fs/project/picks[0]['subj']/picks[0]['session']/'qt1'/reg_str
fmap_dir = datadir.parent.parent/'fmap'
reg_dir_ses = fs/project/picks[0]['subj']/picks[0]['session']/'reg'/reg_str
reg_dir_subj = fs/project/picks[0]['subj']/'reg'/'spgr20reg2ses1'
if not datadir.is_dir():
    datadir.mkdir(parents=True)
if not reg_dir_ses.is_dir():
    reg_dir_ses.mkdir(parents=True)
faFiles = [spgr5_fa05_fnames[0], spgr5_fa10_fnames[0], spgr5_fa15_fnames[0], spgr5_fa20_fnames[0], spgr5_fa30_fnames[0]]
fa_brains = ['',] * len(faFiles)
fa_brains_masked = ['',] * len(faFiles)
fa_brain_masks = ['',] * len(faFiles)
fa_brain_cropped = ['',] * len(faFiles)
for i, fa in enumerate(faFiles):
    results += run_subprocess(['fslmaths ' + str(datadir.parent / str(fa + '.nii')) + ' -thr 2000 ' + str(datadir / appendposix(fa, '_thr2000.nii.gz'))])
    fa_brains[i], fa_brain_masks[i], fa_brain_cropped[i] = extract_brain(str(datadir/appendposix(fa, '_thr2000.nii.gz')))
mask_spgr20 = fa_brain_masks[3]

# since we are not reg all the spgr we simply mask using spgr20 mask.
for i, fa in enumerate(fa_brains):
    results += run_subprocess(['fslmaths ' + str(fa) + ' -mas ' + str(mask_spgr20)+ ' ' + str(appendposix(fa, '_maskedspgr20'))])
    fa_brains_masked[i] = appendposix(fa, '_maskedspgr20')

# b1 correct in image space:

results += run_subprocess(['fslroi '+str(fmap_dir/appendposix(b1map5_fnames[0],'.nii'))+' '+str(appendposix(fmap_dir/b1map5_fnames[0],'_mag.nii.gz'))+' 0 1'])
results += run_subprocess(['fslroi '+str(fmap_dir/appendposix(b1map5_fnames[0],'.nii'))+' '+str(fmap_dir/appendposix(b1map5_fnames[0],'_phase.nii.gz'))+' 2 1'])
regcmd = str(get_antsregsyn_cmd())+' -d 3 -m '+str(appendposix(fmap_dir/b1map5_fnames[0],'_mag.nii.gz'))+' -f '+str(fa_brains[3])+' -o '+str(appendposix(reg_dir_ses/b1map5_fnames[0],'_mag_'+reg_str+'_'))+' -n 30 -t s -p f -j 1 -s 10 -r 1'
results += run_subprocess([regcmd])
results += subj2templ_applywarp(str(fmap_dir/appendposix(b1map5_fnames[0],'_phase.nii.gz')), str(fa_brains[3]), str(appendposix(reg_dir_ses/b1map5_fnames[0],'_phase_'+reg_str+'.nii.gz')), [str(replacesuffix(reg_dir_ses/b1map5_fnames[0],'_mag_'+reg_str+'_1Warp.nii.gz'))],
                                str(reg_dir_ses), affine_xform=[str(replacesuffix(reg_dir_ses/b1map5_fnames[0],'_mag_'+reg_str+'_0GenericAffine.mat'))])
reg_b1map_fmap = appendposix(fmap_dir/b1map5_fnames[0],'_phase_'+reg_str+'.nii.gz')
reg_b1map_fmap.symlink_to(appendposix(reg_dir_ses/b1map5_fnames[0],'_phase_'+reg_str+'.nii.gz'))
reg_b1map_qt1 = appendposix(datadir/b1map5_fnames[0],'_phase_'+reg_str+'.nii.gz')
reg_b1map_qt1.symlink_to(appendposix(reg_dir_ses/b1map5_fnames[0],'_phase_'+reg_str+'.nii.gz'))
b1map_masked = datadir/appendposix(reg_b1map_qt1, '_mf_masked')
results += run_subprocess(['fslmaths '+str(reg_b1map_qt1)+' -fmedian -mas '+str(mask_spgr20)+' '+str(b1map_masked)])

# skip this if doing b1corr in fitting
if b1corr == 'image':
    for i, br in enumerate(fa_brains):
        spgr_b1corr_cmd = 'fslmaths '+str(datadir/br)+' -div '+str(b1map_masked)+' -mul 100 '+str(datadir/appendposix(br, '_b1corr'))
        spgr_bc_cmd = bias_corr_cmd + str(datadir/appendposix(br, '_b1corr'))+' -x '+str(mask_spgr20)+' -o '+str(datadir/appendposix(br, '_b1corr_N4bc'))
        spgr_susan_cmd = 'susan '+str(datadir/appendposix(br, '_b1corr_N4bc'))+' -1 1 3 1 0 '+str(datadir/appendposix(br, '_b1corr_N4bc_susan'))
        results += run_subprocess([spgr_b1corr_cmd])
        results += run_subprocess([spgr_bc_cmd])
        results += run_subprocess([spgr_susan_cmd])
        faFiles[i] = str(datadir/appendposix(br, '_b1corr_N4bc_susan'))

TR = float(str(Path(faFiles[0]).name).split('_')[3].split('-')[3].replace('p','.'))
flipAngles = [float(str(Path(fa).name).split('_')[3].split('-')[1]) for fa in faFiles]
dims = nib.load(str(faFiles[0])).header.get_data_shape()
k = np.prod(np.array(dims))
data = np.zeros([len(flipAngles), k])
for f, fpath in enumerate(faFiles):
    data[f, :] = nib.load(str(fpath)).get_data().flatten()

# masking:
mask = nib.load(str(mask_spgr20)).get_data().astype('bool').flatten()
mask2d = np.tile(mask, [len(flipAngles), 1])

# b1 correction for fits skipped if b1 correction already done in image space or skipping altogether
if b1corr == 'fit':
    b1map_data = nib.load(str(b1map_masked)).get_data().flatten()
    fa_uncorr = np.zeros(data.shape)
    fa_b1corr = np.zeros(data.shape)
    for i, fa in enumerate(flipAngles):
        fa_uncorr[i,:] = fa
    fa_b1corr = fa_uncorr * (b1map_data * 100)
    fa_b1corr[fa_b1corr == np.inf] = np.nan
    fa_b1corr_rad = np.radians(fa_b1corr)
    fa_b1corr_rad[~mask2d] = np.nan

# assumes image based b1 corr. need to add masking here
t1 = np.zeros([k,])
for v in range(k):
    if mask[v]:
        try:
            if np.alltrue(mask2d[:, v]):
                Sa = data[:, v]
                #a = fa_b1corr_rad[:, v]
                a = np.radians(np.array(flipAngles))
                y = Sa / np.sin(a)
                x = Sa / np.tan(a)
                A = np.vstack([x, np.ones(len(x))]).T
                m, c = np.linalg.lstsq(A, y)[0]
                t1[v] = -TR / np.log(m)
            else:
                t1[v] = 0
        except:
            print('forced nan for voxel '+str(v))
            t1[v] = np.nan

t1data = t1.reshape(dims)
t1data[(t1data < 1) | (t1data == np.nan)] = 0
t1data[t1data > 6000] = 6000
t1img = nib.Nifti1Image(t1data, nib.load(str(faFiles[0])).affine)
nib.save(t1img, str('sub-acdc997_ses-1_qt1_vfa3flip_b1corr_clamped.nii'))


# linear regression
y = data / np.sin(fa_b1corr_rad)
x = data / np.tan(fa_b1corr_rad)
m = np.zeros(k)
for v in range(k):
    if mask[v]:
        m[v], intercept, r, p, std = stats.linregress(x[:,v], y[:,v])
qT1_linregr = -TR/np.log(m)
qT1_linregr_data = qT1_linregr.reshape(dims)
qT1_linregr_data[(qT1_linregr_data < 1) | (qT1_linregr_data == np.nan)] = 0
qT1_linregr_data[qT1_linregr_data > 6000] = 6000
qT1_linregr_img = nib.Nifti1Image(qT1_linregr_data, nib.load(faFiles[0]).affine)
nib.save(qT1_linregr_img, str(datadir/'sub-acdc997_ses-1_qt1_vfa3flip_b1corr_vlinregr-fit_clamped.nii'))

#######===========================
from scipy import stats
TR = 22.448
session = 'ses-1'
subjid = 'sub-acdc997'
project = 'acdc'
os.chdir(str(fs/project/subjid/session/'qt1'))
uncorr_vfa_fnames = sorted(list(Path.cwd().glob('*_brain.nii.gz')))
TR = float(np.unique(nib.load('acdc_vy_quiet_patch_test_WIP_VFA3flip_5-15-30-sans_quiet_incrsense_1mm_SENSE_18_1.PAR').header.general_info['repetition_time']))
flipAngles = [float(str(Path(fa).name).split('_')[1].split('-')[1]) for fa in uncorr_vfa_fnames]

mask = nib.load(str('sub-acdc997_vfa-15-tr-22p448_brain_mask.nii.gz')).get_data().astype('bool').flatten()
mask2d = np.tile(mask, [len(flipAngles), 1])

b1map_masked = 'sub-acdc997_b1map_phase_reg2vfa30_mf5_masked.nii.gz'
b1map_data = nib.load(str(b1map_masked)).get_data().flatten()

dims = nib.load(str(uncorr_vfa_fnames[0])).header.get_data_shape()
k = np.prod(np.array(dims))
data = np.zeros([len(flipAngles), k])
for f, fpath in enumerate(uncorr_vfa_fnames):
    data[f, :] = nib.load(str(fpath)).get_data().flatten()
b1map_data = nib.load(str(b1map_masked)).get_data().flatten()
fa_uncorr = np.zeros(data.shape)
fa_b1corr = np.zeros(data.shape)
for i, fa in enumerate(flipAngles):
    fa_uncorr[i, :] = fa
fa_b1corr = fa_uncorr * b1map_data
fa_b1corr[fa_b1corr == np.inf] = np.nan
fa_b1corr_rad = np.radians(fa_b1corr)
fa_b1corr_rad[~mask2d] = np.nan

data = np.zeros([len(flipAngles), k])
for f, fpath in enumerate(uncorr_vfa_fnames):
    data[f, :] = nib.load(str(fpath)).get_data().flatten()
b1map_data = nib.load(str(b1map_masked)).get_data().flatten()
fa_uncorr = np.zeros(data.shape)
fa_b1corr = np.zeros(data.shape)
for i, fa in enumerate(flipAngles):
    fa_uncorr[i, :] = fa
fa_b1corr = fa_uncorr * b1map_data
fa_b1corr[fa_b1corr == np.inf] = np.nan
fa_b1corr_rad = np.radians(fa_b1corr)
fa_b1corr_rad[~mask2d] = np.nan

# linear regression
y = data / np.sin(fa_b1corr_rad)
x = data / np.tan(fa_b1corr_rad)
m = np.zeros(k)
for v in range(k):
    if mask[v]:
        m[v], intercept, r, p, std = stats.linregress(x[:,v], y[:,v])
qT1_linregr = -TR/np.log(m)
qT1_linregr_data = qT1_linregr.reshape(dims)
qT1_linregr_data[(qT1_linregr_data < 1) | (qT1_linregr_data == np.nan)] = 0
qT1_linregr_data[qT1_linregr_data > 6000] = 6000
qT1_linregr_img = nib.Nifti1Image(qT1_linregr_data, nib.load(str(uncorr_vfa_fnames[0])).affine)
nib.save(qT1_linregr_img, str('sub-acdc997_ses-1_qt1_vfa3flip_b1corr_vlinregr-fit_clamped2.nii'))

## example rms calc
#in_data_rms = np.sqrt(np.sum(np.square(in_data), axis=3)/in_data.shape[3])

vfa2_2ec_pr_img = nib.load('acdc_vy_quiet_patch_test_WIP_VFA3flip_5-15-30-sans_quiet_incrsense_1mm_SENSE_18_1.PAR')
vfa2_2ec_pr_hdr = vfa2_2ec_pr_img.header
TR = float(vfa2_2ec_pr_hdr.general_info['repetition_time'])
vy_vfa2_2ec_data = nib.load('acdc_vy_quiet_patch_test_WIP_VFA-sans-QUIET_SENSE_14_1.nii').get_data()

flipAngles = np.array([5.0, 25.0])


## VASILY PROTO
from dipy.align.reslice import reslice
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf
from pylabs.io.images import savenii
from pylabs.fmap_correction.b1_map_corr import calcb1map
matching_b1map = True
project = 'acdc'
subjid = 'VY_PATCH_TEST_1-3-18'
os.chdir(str(fs/project/subjid))
vfa_fname = 'acdc_vy_quiet_patch_test_WIP_VFA-sans-QUIET_SENSE_14_1.nii'
b1map_fname = 'acdc_vy_quiet_patch_test_WIP_B1-sans_SENSE_13_1.nii'
vy_flipAngles = [4.0, 25.0]
TR = float(np.unique(nib.load(str(replacesuffix(vfa_fname, '.PAR'))).header.general_info['repetition_time']))
vfa_affine = nib.load(vfa_fname).affine
vy_vfa2_2ec_data = nib.load(vfa_fname).get_data()  # scaled to float

## if using matching b1
if matching_b1map:
    vy_b1map_data = nib.load(b1map_fname).get_data()   # scaled to dv
    vy_b1map_phase = vy_b1map_data[:,:,:,2]

    vy_b1map_phase_mf = medianf(vy_b1map_phase, size=5)
    nib.save(nib.Nifti1Image(vy_b1map_phase_mf, nib.load(b1map_fname).affine), 'vy_b1map_match14_phase_mf5.nii')
else:    # assumes b1 map reg using ants and phase warped and masked
    vy_b1map_phase_mf = nib.load(b1map_fname).get_data()


vy_vfa2_ec1 = vy_vfa2_2ec_data[:,:,:,:2]
vy_vfa2_ec2 = vy_vfa2_2ec_data[:,:,:,2:4]
vy_vfa2_ec1_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec1), axis=3)/vy_vfa2_ec1.shape[3])
vy_vfa2_ec2_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec2), axis=3)/vy_vfa2_ec2.shape[3])
k = np.prod(vy_vfa2_ec1_rms.shape)
data = np.zeros([len(vy_flipAngles), k])
data[0,:] = vy_vfa2_ec1_rms.flatten()
data[1,:] = vy_vfa2_ec2_rms.flatten()
fa_uncorr = np.zeros(data.shape)
fa_b1corr = np.zeros(data.shape)
for i, fa in enumerate(vy_flipAngles):
    fa_uncorr[i, :] = fa
fa_b1corr = fa_uncorr * vy_b1map_phase_mf.flatten()  # uses broadcasting
fa_b1corr[fa_b1corr == np.inf] = np.nan
fa_b1corr_rad = np.radians(fa_b1corr)
y = data / np.sin(fa_b1corr_rad)
x = data / np.tan(fa_b1corr_rad)
m = np.zeros(k)
for v in range(k):        #uses no mask yet
    m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
qT1_linregr = -TR/np.log(m)
qT1_linregr_data = qT1_linregr.reshape(vy_vfa2_ec1_rms.shape)
qT1_linregr_data[(qT1_linregr_data < 1) | (qT1_linregr_data == np.nan)] = 0
qT1_linregr_data[qT1_linregr_data > 6000] = 6000
qt1out_fname = 'vy_qt1_scan18_b116_man_calc_mf9_vlinregr-fit_clamped.nii'
savenii(qT1_linregr_data, vfa_affine, qt1out_fname)


#qT1_linregr_img = nib.Nifti1Image(qT1_linregr_data, affine)
#qt1out_fname = '/brainstudio/data/acdc/VY_PATCH_TEST_1-3-18/js_qt1_sc18vfa2flip_2echo_rms_b1corr13_mf_vlinregr-fit_clamped.nii'
#nib.save(qT1_linregr_img, qt1out_fname)


# ##### direct approach
from dipy.align.reslice import reslice
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf
from pylabs.fmap_correction.b1_map_corr import calcb1map
matching_b1map = True
project = 'acdc'
subjid = 'VY_PATCH_TEST_1-3-18'
os.chdir(str(fs/project/subjid))
vfa_fname = 'acdc_vy_quiet_patch_test_WIP_VFA-sans-QUIET_SENSE_14_1.nii'
vy_flipAngles = [4.0, 25.0]
TR = float(np.unique(nib.load(str(replacesuffix(vfa_fname, '.PAR'))).header.general_info['repetition_time']))
affine = nib.load(vfa_fname).affine
vy_vfa2_2ec_data = nib.load(vfa_fname).get_data()  # scaled to float
b1map11_fname = '/brainstudio/data/acdc/VY_PATCH_TEST_1-3-18/b1map_vy13_jsman_mf11.nii'
b1map13_fname = '/brainstudio/data/acdc/VY_PATCH_TEST_1-3-18/b1map_vy13_jsman_mf13.nii'
vy_b1map11_phase_mf = nib.load(b1map11_fname).get_data()
vy_b1map13_phase_mf = nib.load(b1map13_fname).get_data()

### b1map and vfa

from dipy.align.reslice import reslice
from pylabs.io.images import savenii
from pylabs.fmap_correction.b1_map_corr import calcb1map
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf

os.chdir('/brainstudio/data/acdc/sub-acdc104/ses-1/source_parrec')
b1map_fname = 'sub-acdc104_WIP_B1MAP-QUIET_FC_TR70-210_SP-100_SENSE_13_1.nii'
vfa_fname = 'sub-acdc104_WIP_VFA_FA4-25_QUIET_SENSE_10_1.nii'

b1TRs = nib.load(str(replacesuffix(b1map_fname, '.PAR'))).header.general_info['repetition_time']
vfaTR = nib.load(str(replacesuffix(vfa_fname, '.PAR'))).header.general_info['repetition_time']
vy_flipAngles = [4.0, 25.0]
vfa_affine = nib.load(vfa_fname).affine

b1_data = nib.load(b1map_fname).get_data()
vfa_data = nib.load(vfa_fname).get_data()


S1 = medianf(b1_data[:,:,:,0], size=7)
S2 = medianf(b1_data[:,:,:,1], size=7)
b1map = calcb1map(S1, S2, b1TRs)
b1map_out_fname = 'sub-acdc104_ses-1_b1map13_phase_mf7_9.nii'
savenii(b1map, vfa_affine, b1map_out_fname)

vy_vfa2_ec1 = vfa_data[:,:,:,:2]
vy_vfa2_ec2 = vfa_data[:,:,:,2:4]
vy_vfa2_ec1_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec1), axis=3)/vy_vfa2_ec1.shape[3])
vy_vfa2_ec2_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec2), axis=3)/vy_vfa2_ec2.shape[3])
k = np.prod(vy_vfa2_ec1_rms.shape)
data = np.zeros([len(vy_flipAngles), k])
data[0,:] = vy_vfa2_ec1_rms.flatten()
data[1,:] = vy_vfa2_ec2_rms.flatten()
fa_uncorr = np.zeros(data.shape)
fa_b1corr = np.zeros(data.shape)
for i, fa in enumerate(vy_flipAngles):
    fa_uncorr[i, :] = fa
fa_b1corr = fa_uncorr * b1map.flatten()  # uses broadcasting
fa_b1corr[fa_b1corr == np.inf] = np.nan
fa_b1corr_rad = np.radians(fa_b1corr)
y = data / np.sin(fa_b1corr_rad)
x = data / np.tan(fa_b1corr_rad)
m = np.zeros(k)
for v in range(k):        #uses no mask yet
    m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
qT1_linregr = -vfaTR/np.log(m)
qT1_linregr_data = qT1_linregr.reshape(vy_vfa2_ec1_rms.shape)
qT1_linregr_data[qT1_linregr_data < 1.0] = 0
qT1_linregr_data[qT1_linregr_data > 6000] = 6000
qT1_linregr_data_clean = np.nan_to_num(qT1_linregr_data, copy=True)
qt1out_fname = 'sub-acdc104_ses-1_vfa_qt1_b1corr9_mf9_vlinregr-fit_clamped.nii'
savenii(qT1_linregr_data_clean, vfa_affine, qt1out_fname)







# now segment using spm

