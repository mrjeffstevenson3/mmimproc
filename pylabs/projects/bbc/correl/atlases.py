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
atlas_midx = pd.MultiIndex.from_arrays([['data', 'data', 'shape', 'shape', 'zooms', 'zooms'], ['mori', 'JHU_tracts', 'mori', 'JHU_tracts', 'mori', 'JHU_tracts']])
atlases = pd.DataFrame(index=['dwi', 'vbm'], columns=atlas_midx)
# get atlas data

mori_atlas_vbm = atlases_in_templ_sp_dir/'mori_atlas_reg2template.nii.gz'
JHUtracts_atlas_vbm = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template.nii.gz'
mori_atlas_dwi = atlases_in_templ_sp_dir/'mori_atlas_reg2template_resamp2dwi.nii.gz'
JHUtracts_atlas_dwi = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template_resamp2dwi.nii.gz'


atlases['shape'].set_value('vbm', 'mori', nib.load(str(mori_atlas_vbm)).get_data().shape)
atlases['shape'].set_value('vbm', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).get_data().shape)
atlases['shape'].set_value('dwi', 'mori', nib.load(str(mori_atlas_dwi)).get_data().shape)
atlases['shape'].set_value('dwi', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).get_data().shape)
atlases['zooms'].set_value('vbm', 'mori', nib.load(str(mori_atlas_vbm)).header.get_zooms())
atlases['zooms'].set_value('vbm', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).header.get_zooms())
atlases['zooms'].set_value('dwi', 'mori', nib.load(str(mori_atlas_dwi)).header.get_zooms())
atlases['zooms'].set_value('dwi', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).header.get_zooms())
atlases['data'].set_value('vbm', 'mori', nib.load(str(mori_atlas_vbm)).get_data())
atlases['data'].set_value('vbm', 'JHU_tracts', nib.load(str(JHUtracts_atlas_vbm)).get_data())
atlases['data'].set_value('dwi', 'mori', nib.load(str(mori_atlas_dwi)).get_data().shape)
atlases['data'].set_value('dwi', 'JHU_tracts', nib.load(str(JHUtracts_atlas_dwi)).get_data())


