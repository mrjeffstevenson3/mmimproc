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
from scipy import stats
from dipy.segment.mask import applymask
from scipy.ndimage.morphology import binary_erosion as ero
from scipy.ndimage.measurements import center_of_mass as com
from pylabs.alignment.resample import reslice_roi
from pylabs.alignment.phantom import align, transform
from pylabs.qt1.fitting import t1fit
from pylabs.qt1.model_pipeline import calculate_model, vialsInOrder
from pylabs.io.images import savenii
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix, getnetworkdataroot
from scipy.ndimage.filters import median_filter as medianf
from pylabs.projects.genz.file_names import project, get_5spgr_names, SubjIdPicks
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())

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
         {'subj': 'sub-genz996', 'session': 'ses-1', 'run': '1',},
         ]
setattr(subjids_picks, 'subjids', picks)

b1map5_fnames, spgr5_fa05_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames = get_5spgr_names(subjids_picks)
datadir = fs/project/picks[0]['subj']/picks[0]['session']/'qt1'/'reg2spgr05_br'
faFiles = [spgr5_fa05_fnames[0], spgr5_fa10_fnames[0], spgr5_fa15_fnames[0], spgr5_fa20_fnames[0], spgr5_fa30_fnames[0]]
for i, fa in enumerate(faFiles):
    faFiles[i] = str(datadir/appendposix(fa, '_thr2000_brain_maskedfa20.nii.gz'))

TR = float(str(Path(faFiles[0]).name).split('_')[3].split('-')[3].replace('p','.'))
flipAngles = [float(str(Path(fa).name).split('_')[3].split('-')[1]) for fa in faFiles]
dims = nib.load(faFiles[0]).header.get_data_shape()
k = np.prod(np.array(dims))
data = np.full([len(flipAngles), k], np.nan)
for f, fpath in enumerate(faFiles):
    data[f, :] = nib.load(fpath).get_data()[:,:,:].flatten()
t1 = np.full([k,], np.nan)
# need to add b1 correction and masking here
for v in range(k):
    Sa = data[:, v]
    a = np.radians(flipAngles)
    y = Sa / np.sin(a)
    x = Sa / np.tan(a)
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y)[0]
    t1[v] = -TR / np.log(m)

t1data = t1.reshape(dims)
t1img = nib.Nifti1Image(t1data, nib.load(faFiles[0]).affine)
nib.save(t1img, str(datadir/'sub-genz996_ses-1_qt1_noreg_nob1corr_lstsq-fit.nii'))

# b1 correction and masking:
mask = nib.load(str(datadir/'sub-genz996_ses-1_spgr_fa-20-tr-12p0_1_thr2000_brain_mask.nii.gz')).get_data().astype('bool').flatten()
b1map_data = nib.load(str(datadir/'sub-genz996_ses-1_b1map_1_phase_b1spgr2spgr30_mf_maskedfa20.nii.gz')).get_data().flatten()

fa_uncorr = np.full(data.shape, np.nan)
fa_b1corr = np.full(data.shape, np.nan)
for i, fa in enumerate(flipAngles):
    fa_uncorr[i,:] = fa

fa_b1corr = fa_uncorr / b1map_data[None, :] * 100

# for linear regression:
for v in range(k):
    if mask[v]:
        Sa = data[:, v]
        a = np.radians(flipAngles)
        y = Sa / np.sin(a)
        x = Sa / np.tan(a)
        m, intercept, r, p, std = stats.linregress(x, y)
        t1[v] = -TR/np.log(m)

# 1st attempt at vectorizing
fa_b1corr_rad = np.radians(fa_b1corr)
y = data / np.sin(fa_b1corr_rad)
x = data / np.tan(fa_b1corr_rad)
m, intercept, r, p, std = stats.linregress(x, y)
qT1_linregr = -TR/np.log(m)
qT1_linregr_data = qT1_linregr.reshape(dims)
qT1_linregr_img = nib.Nifti1Image(qT1_linregr_data, nib.load(faFiles[0]).affine)
nib.save(qT1_linregr_img, str(datadir/'sub-genz996_ses-1_qt1_noreg_b1corr_vlinregr-fit.nii'))