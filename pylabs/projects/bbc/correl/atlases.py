from pathlib import *
import pandas as pd
import numpy as np
import nibabel as nib
import scipy.ndimage.measurements as measurements
from pylabs.correlation.atlas import mori_region_labels, JHUtracts_region_labels
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
"""
makes atlas objects.
"""
project = 'bbc'
atlases_in_templ_sp_dir = fs/project/'reg'/'atlases_in_template_space'
# define atlases for labeling in template space
atlas_midx = pd.MultiIndex.from_arrays([['dwi', 'dwi', 'vbm', 'vbm'], ['mori', 'JHU_tracts', 'mori', 'JHU_tracts']])
atlases = pd.DataFrame(index=['img', 'zooms', 'shape'], columns=atlas_midx)
# get atlas data
mori_atlas_vbm = atlases_in_templ_sp_dir/'mori_atlas_reg2template.nii.gz'
JHUtracts_atlas_vbm = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template.nii.gz'
mori_atlas_dwi = atlases_in_templ_sp_dir/'mori_atlas_reg2template_resamp2dwi.nii.gz'
JHUtracts_atlas_dwi = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template_resamp2dwi.nii.gz'

atlases.sort_index(axis=1, inplace=True)
atlases['vbm'].set_value('img', 'mori', nib.load(str(mori_atlas_vbm)))
atlases['vbm'].set_value('img', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)))
atlases['dwi'].set_value('img', 'mori', nib.load(str(mori_atlas_dwi)))
atlases['dwi'].set_value('img', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)))

atlases['vbm'].set_value('zooms', 'mori', nib.load(str(mori_atlas_vbm)).header.get_zooms())
atlases['vbm'].set_value('zooms', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).header.get_zooms())
atlases['dwi'].set_value('zooms', 'mori', nib.load(str(mori_atlas_dwi)).header.get_zooms())
atlases['dwi'].set_value('zooms', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).header.get_zooms())

atlases['vbm'].set_value('shape', 'mori', nib.load(str(mori_atlas_vbm)).get_data().shape)
atlases['vbm'].set_value('shape', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).get_data().shape)
atlases['dwi'].set_value('shape', 'mori', nib.load(str(mori_atlas_dwi)).get_data().shape)
atlases['dwi'].set_value('shape', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).get_data().shape)

atlases['vbm'].set_value('affine', 'mori', nib.load(str(mori_atlas_vbm)).affine)
atlases['vbm'].set_value('affine', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).affine)
atlases['dwi'].set_value('affine', 'mori', nib.load(str(mori_atlas_dwi)).affine)
atlases['dwi'].set_value('affine', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).affine)
