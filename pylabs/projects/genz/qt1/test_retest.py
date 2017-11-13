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
from dipy.segment.mask import applymask
from scipy.ndimage.morphology import binary_erosion as ero
from pylabs.alignment.resample import reslice_roi
from pylabs.qt1.fitting import t1fit
from pylabs.qt1.model_pipeline import calculate_model
from pylabs.io.images import savenii
from pylabs.utils import run_subprocess, WorkingContext, appendposix, replacesuffix, getnetworkdataroot
from scipy.ndimage.filters import median_filter as medianf
from pylabs.utils.provenance import ProvenanceWrapper
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())

scanner = 'slu'
scanner_dir = fs/'phantom_qT1_{}'.format(scanner)

phant_act = pd.DataFrame(calculate_model(scanner))

def get_exam_date_time(parfile):
    par_date_time = nib.load(str(parfile)).header.general_info['exam_date']
    return pd.to_datetime(par_date_time)


#par_file = fs/'genz'/'sub-genz996/ses-2/phantom_parrec/sub-genz996_oct24_2017_phantom_WIP_T1_MAP_05_SENSE_4_1.PAR'
par_file = fs/'phantom_qT1_slu/sub-phant2017-10-19/source_parrec/sub-genz996_PHANTOM_WIP_T1_MAP_05_SENSE_4_1.PAR'

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

outfile = str(spgr_dir / '{phant}_qT1_b1corr_5flip.nii'.format(phant=phant_name))

TR = float(str(spgr_files[0].name).split('_')[5].replace('p','.'))

X = []
for a in spgr_files:
    X.append(int(a.name.split('_')[3]))
files = []
for f in spgr_files:
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

