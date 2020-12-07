from pathlib import *
import pandas as pd
import numpy as np
import nibabel as nib
import scipy.ndimage.measurements as measurements
from mmimproc.correlation.atlas import mori_region_labels, JHUtracts_region_labels
from mmimproc.utils.paths import getnetworkdataroot
fs = mmimproc.fs_local
"""
makes atlas objects.
"""
project = 'bbc'
atlas_in_templ_sp_dir = fs/project/'reg'/'atlases_in_template_space'
# define atlas for labeling in template space
atlas_midx = pd.MultiIndex.from_arrays([['dwi', 'dwi', 'vbm', 'vbm'], ['mori', 'JHU_tracts', 'mori', 'JHU_tracts']])
atlas = pd.DataFrame(index=['img', 'zooms', 'shape'], columns=atlas_midx)
# get atlas data
mori_atlas_vbm = atlas_in_templ_sp_dir/'mori_atlas_reg2template.nii.gz'
JHUtracts_atlas_vbm = atlas_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template.nii.gz'
mori_atlas_dwi = atlas_in_templ_sp_dir/'mori_atlas_reg2template_resamp2dwi.nii.gz'
JHUtracts_atlas_dwi = atlas_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template_resamp2dwi.nii.gz'

atlas.sort_index(axis=1, inplace=True)
atlas['vbm'].set_value('img', 'mori', nib.load(str(mori_atlas_vbm)))
atlas['vbm'].set_value('img', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)))
atlas['dwi'].set_value('img', 'mori', nib.load(str(mori_atlas_dwi)))
atlas['dwi'].set_value('img', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)))

atlas['vbm'].set_value('zooms', 'mori', nib.load(str(mori_atlas_vbm)).header.get_zooms())
atlas['vbm'].set_value('zooms', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).header.get_zooms())
atlas['dwi'].set_value('zooms', 'mori', nib.load(str(mori_atlas_dwi)).header.get_zooms())
atlas['dwi'].set_value('zooms', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).header.get_zooms())

atlas['vbm'].set_value('shape', 'mori', nib.load(str(mori_atlas_vbm)).get_data().shape)
atlas['vbm'].set_value('shape', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).get_data().shape)
atlas['dwi'].set_value('shape', 'mori', nib.load(str(mori_atlas_dwi)).get_data().shape)
atlas['dwi'].set_value('shape', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).get_data().shape)

atlases = atlas

# atlas['vbm'].set_value('affine', 'mori', [nib.load(str(mori_atlas_vbm)).affine])
# atlas['vbm'].set_value('affine', 'JHU_tracts', [nib.load(str(JHUtracts_atlas_vbm)).affine])
# atlas['dwi'].set_value('affine', 'mori', [nib.load(str(mori_atlas_dwi)).affine])
# atlas['dwi'].set_value('affine', 'JHU_tracts', [nib.load(str(JHUtracts_atlas_dwi)).affine])
