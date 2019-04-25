# inject R1 and MPF output from vasily into UKF
# todo: add ants cmds for reg to dwi without preserving resolution. eg downsample qt1.
from pathlib import *
import nibabel as nib
import numpy as np
from mmimproc.utils import *
from mmimproc.io.images import savenii
from mmimproc.conversion.analyze import reorient_img_with_pr_affine
from mmimproc.io.mixed import get_pr_affine_fromh5
from mmimproc.diffusion.vol_into_vtk import inject_vol_data_into_vtk
from mmimproc.structural.brain_extraction import extract_brain
from mmimproc.alignment.resample import reslice_niivol
from mmimproc.projects.genz.file_names import SubjIdPicks, Optsd, get_vfa_names, merge_ftempl_dicts
antsRegistrationSyN_cmd = get_antsregsyn_cmd(default_cmd_str=True)
antsN4bias_cmd = get_antsregsyn_cmd(N4bias=True, default_cmd_str=True)
project = 'genz'
subjids_picks = SubjIdPicks()
opts = Optsd()
picks = [
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz105', 'vol2vtk_offsets': (1.5,0,0)},  # 1.5 is good
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz103', 'vol2vtk_offsets': (1,0,0)},   # 1 is good and done
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz106', 'vol2vtk_offsets': (-4.5,0,0)},  # -4.5 is good and done
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz102', 'vol2vtk_offsets': (0,0,0)},
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz205', 'vol2vtk_offsets': (-6,0,0)},  # -6 is good
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz211', 'vol2vtk_offsets': (7.5,0,0)},   # +ve moves r1 to subj left/image right (halo on lt side of brain)
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz212', 'vol2vtk_offsets': (-7,0,0)},  # -ve moves r1 to subj right/image left (halo on rt side of brain)
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz304', 'vol2vtk_offsets': (1.5,0,0)},  # 1.5 is good
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz303', 'vol2vtk_offsets': (15,0,0)},   # 15 is good and done
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz305', 'vol2vtk_offsets': (-4.5,0,0)}, # -4.5 is good and done
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz412', 'vol2vtk_offsets': (24.5,0,0)},  # 24.5 is good
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz410', 'vol2vtk_offsets': (1, 0, 0)},    # 1 is good and done
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz415', 'vol2vtk_offsets': (1, 0, 0)},    # 1 is good and done
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz510', 'vol2vtk_offsets': (5,0,0)},  # 5 is good
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz506', 'vol2vtk_offsets': (16.5,0,0)},  # 16.5 is good
        {'run': '1', 'session': 'ses-1', 'subj': 'sub-genz508', 'vol2vtk_offsets': (6,0,0)},   # 6 is good
        # no offsets determined for these subj
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz104', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz107', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz108', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz109', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz110', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz111', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz112', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz113', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz114', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz115', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz116', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz117', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz118', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz119', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz120', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz121', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz122', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz123', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz124', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz125', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz126', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz127', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz128', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz129', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz130', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz131', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz132', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz133', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz201', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz202', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz203', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz204', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz206', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz208', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz209', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz210', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz213', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz214', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz215', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz216', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz218', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz219', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz220', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz221', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz222', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz223', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz224', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz225', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz226', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz227', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz228', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz229', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz230', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz231', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz232', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz233', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz235', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz302', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz306', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz307', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz308', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz310', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz311', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz312', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz313', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz314', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz315', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz316', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz318', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz319', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz320', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz321', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz322', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz323', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz324', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz325', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz326', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz327', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz328', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz329', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz330', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz331', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz332', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz333', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz334', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz335', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz337', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz401', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz402', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz404', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz405', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz406', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz408', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz409', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz411', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz413', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz414', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz416', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz417', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz418', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz419', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz420', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz421', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz422', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz423', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz424', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz425', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz426', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz427', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz428', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz429', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz430', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz431', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz432', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz501', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz502', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz503', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz504', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz505', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz507', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz509', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz511', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz512', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz513', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz514', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz515', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz516', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz517', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 2, 'session': 'ses-1', 'subj': 'sub-genz518', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz519', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz520', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz521', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz522', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz523', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz524', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz525', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz526', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz527', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz528', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz529', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz530', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz531', 'vol2vtk_offsets': (0, 0, 0)},
        {'run': 1, 'session': 'ses-1', 'subj': 'sub-genz532', 'vol2vtk_offsets': (0, 0, 0)},
        ]
setattr(subjids_picks, 'subjids', picks)
setattr(subjids_picks, 'getR1_MPF_nii_fnames', True)
setattr(subjids_picks, 'get_analyse_R1_MPF_names', True)

r1_fname_templ = '{subj}_{session}_vasily_r1_ras'
mpf_fname_templ = '{subj}_{session}_vasily_mpf_ras'
orig_r1_fname_templ = 'R1_{subj}.img'  # not matching PAR file
orig_mpf_fname_templ = 'MPF_{subj}.img'

setattr(subjids_picks, 'r1_fname_templ', r1_fname_templ)
setattr(subjids_picks, 'mpf_fname_templ', mpf_fname_templ)
setattr(subjids_picks, 'orig_r1_fname_templ', orig_r1_fname_templ)
setattr(subjids_picks, 'orig_mpf_fname_templ', orig_mpf_fname_templ)

qt1_picks = get_vfa_names(subjids_picks)

results = ('',)
errors = ('',)

for pick in qt1_picks:
    # all dwi use run 1 even if qt1 use run 2
    if pick['run'] == 2:
        pick['topup_brain_fname'] = pick['topup_brain_fname'].replace('_2_', '_1_')
    print('Working on {subj} and {session}'.format(**pick))
    pick['ext'] = opts.ext
    if not pick['qt1_path'].is_dir():
        pick['qt1_path'].mkdir(parents=True)
        raise ValueError('missing qt1 directory and hence qt1 files. please check for {subj} in {session}/qt1'.format(**pick))
    # convert R1 and MPF to nifti
    pr_affine, pr_shape = get_pr_affine_fromh5(opts.info_fname, pick['subj'], pick['session'], 'qt1', pick['vfa_fname'])
    if pr_shape[:3] != opts.vfa_pr_shape:
        print('found discrepancy between pr_shape ', pr_shape[:3], ' and opts shape ', opts.vfa_pr_shape)
    reorient_img_with_pr_affine(pick['vasily_mpf_path'] / pick['orig_r1_fname'], pr_affine, pr_shape=opts.vfa_pr_shape, out_nii_fname=pick['qt1_path']/(pick['r1_fname']+opts.ext), mpf_dtype=opts.mpf_img_dtype)
    reorient_img_with_pr_affine(pick['vasily_mpf_path'] / pick['orig_mpf_fname'], pr_affine, pr_shape=opts.vfa_pr_shape, out_nii_fname=pick['qt1_path']/(pick['mpf_fname']+opts.ext), mpf_dtype=opts.mpf_img_dtype)
    with WorkingContext(pick['qt1_path']):
        pick['vfa_ec-1_fname'] = pick['vfa_fname'].replace('fa-4-25', 'ec-1-fa-4')
        results += run_subprocess([' '.join(['fslroi', pick['vfa_fname'], pick['vfa_ec-1_fname'], '0 1'])])
        pick['vfa_ec-1_N4bias_fname'] = pick['vfa_ec-1_fname'] + '_N4bias' + opts.ext
        results += run_subprocess([antsN4bias_cmd.format(**{'infile': pick['vfa_ec-1_fname'] + opts.ext, 'outfile':pick['vfa_ec-1_N4bias_fname']})])
        vfa_brain_fname, vfa_brain_mask_fname, vfa_brain_cropped_fname = extract_brain(pick['vfa_ec-1_N4bias_fname'], mode='T2', f_factor=0.5, robust=True)
        results += run_subprocess([' '.join(['fslmaths', str(vfa_brain_mask_fname), '-ero -ero', str(appendposix(vfa_brain_mask_fname, '_ero2'))])])
        pick['r1_brain_fname'], pick['mpf_brain_fname'] = pick['r1_fname']+ '_brain', pick['mpf_fname']+ '_brain'
        results += run_subprocess([' '.join(['fslmaths', pick['r1_fname'], '-mas', str(appendposix(vfa_brain_mask_fname, '_ero2')), str(pick['r1_brain_fname'])])])
        results += run_subprocess([' '.join(['fslmaths', pick['mpf_fname'], '-mas', str(appendposix(vfa_brain_mask_fname, '_ero2')), str(pick['mpf_brain_fname'])])])
        with WorkingContext(pick['vtk_path']):
            results += run_subprocess(['ln -sf ../../qt1/{r1_brain_fname}{ext} {r1_brain_fname}{ext}'.format(**pick)])
            results += run_subprocess(['ln -sf ../../qt1/{mpf_brain_fname}{ext} {mpf_brain_fname}{ext}'.format(**pick)])
    if not pick['reg2dwi_path'].is_dir():
        pick['reg2dwi_path'].mkdir(parents=True)
    if not pick['vtk_path'].is_dir():
        pick['vtk_path'].mkdir(parents=True)
    with WorkingContext(pick['reg2dwi_path']):
        # add ants cmd here to reg qt1 directly to orig low res dwi b0.
        pick['moving'] = pick['qt1_path'] / (pick['r1_brain_fname']+opts.ext)
        pick['fixed'] = pick['dwi_path'] / '{topup_brain_fname}{ext}'.format(**pick)
        pick['outfile'] = pick['reg2dwi_path'].joinpath(pick['r1_brain_fname'] + '_reg2dwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['qt1_path']):
            results += run_subprocess(['ln -sf ../reg/{qt12dwi_reg_dir}/{outfile}Warped{ext} {r1_brain_fname}_reg2dwi{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
        pick['moving'] = pick['qt1_path'] / '{mpf_brain_fname}{ext}'.format(**pick)
        pick['outfile'] = pick['reg2dwi_path'].joinpath(pick['mpf_brain_fname'] + '_reg2dwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['qt1_path']):
            results += run_subprocess(['ln -sf ../reg/{qt12dwi_reg_dir}/{outfile}Warped{ext} {mpf_brain_fname}_reg2dwi{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
        mpf_img = nib.load('{outfile}Warped{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name})))
        mpf_data = mpf_img.get_data().astype(np.float32)
        unscaled_data = mpf_data / 100.0
        perc_myelin = (unscaled_data - 3.9) / 0.21
        scaled_perc_myelin = perc_myelin * 100.0
        savenii(scaled_perc_myelin, mpf_img.affine, '{mpf_brain_fname}_reg2dwi_percent_myelin{ext}'.format(**pick))
        with WorkingContext(pick['qt1_path']):
            results += run_subprocess(['ln -sf ../reg/{qt12dwi_reg_dir}/{mpf_brain_fname}_reg2dwi_percent_myelin{ext} {mpf_brain_fname}_reg2dwi_percent_myelin{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
        pick['moving'] = pick['qt1_path'] / (pick['r1_brain_fname']+opts.ext)
        reslice_niivol(pick['moving'], pick['dwi_path'] / '{topup_brain_fname}{ext}'.format(**pick),  pick['dwi_path'] / '{topup_brain_fname}_resampled2qt1{ext}'.format(**pick))
        pick['fixed'] = pick['dwi_path'] / '{topup_brain_fname}_resampled2qt1{ext}'.format(**pick)
        pick['outfile'] = pick['reg2dwi_path'].joinpath(pick['r1_brain_fname'] + '_reg2resampleddwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['vtk_path']):
            results += run_subprocess(['ln -sf ../../reg/{qt12dwi_reg_dir}/{outfile}Warped{ext} {r1_brain_fname}_reg2resampleddwi{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
        pick['moving'] = pick['qt1_path'] / '{mpf_brain_fname}{ext}'.format(**pick)
        pick['outfile'] = pick['reg2dwi_path'].joinpath(pick['mpf_brain_fname'] + '_reg2resampleddwi_')
        results += run_subprocess([antsRegistrationSyN_cmd.format(**pick)])
        with WorkingContext(pick['vtk_path']):
            results += run_subprocess(['ln -sf ../../reg/{qt12dwi_reg_dir}/{outfile}Warped{ext} {mpf_brain_fname}_reg2resampleddwi{ext}'.format(**merge_ftempl_dicts(pick, vars(opts), {'outfile': pick['outfile'].name}))])
    try:
        with WorkingContext(pick['vtk_path']):
            print('Injecting {UKF_fname} for {subj} and {session} with {r1_brain_fname}'.format(**pick))
            results += inject_vol_data_into_vtk(Path('.'), '{r1_brain_fname}_reg2resampleddwi{ext}'.format(**pick), pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectR1.vtk'), offset_adj=pick['vol2vtk_offsets'])
            print('Injecting {UKF_fname} for {subj} and {session} with {mpf_brain_fname}'.format(**pick))
            results += inject_vol_data_into_vtk(Path('.'), '{mpf_brain_fname}_reg2resampleddwi{ext}'.format(**pick), pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectMPF.vtk'), offset_adj=pick['vol2vtk_offsets'])
            print('Calculating percent myelin for {subj} and {session} with {mpf_brain_fname}_reg2resampleddwi_percent_myelin'.format(**pick))
            mpf_img = nib.load(pick['mpf_brain_fname'] + '_reg2resampleddwi' + opts.ext)
            mpf_data = mpf_img.get_data().astype(np.float32)
            unscaled_data = mpf_data / 100.0
            perc_myelin = (unscaled_data -3.9) / 0.21
            scaled_perc_myelin = perc_myelin * 100.0
            savenii(scaled_perc_myelin, mpf_img.affine, pick['mpf_brain_fname'] + '_reg2resampleddwi_percent_myelin' + opts.ext)
            results += inject_vol_data_into_vtk(Path('.'), pick['mpf_brain_fname'] + '_reg2resampleddwi_percent_myelin' + opts.ext,
                                     pick['UKF_fname'], replacesuffix(pick['UKF_fname'], '_resampledB0_injectpercentmyelin.vtk'),
                                     offset_adj=pick['vol2vtk_offsets'])
            print('Successful Injection of {UKF_fname} for {subj} and {session} with {r1_brain_fname} and {mpf_brain_fname}'.format(**pick))
    except:
        print('injection failed with errors for {subj} and {session} on vtk file {UKF_fname} and injection file {r1_brain_fname} or {mpf_brain_fname}.'.format(**pick))
        errors += ('injection failed with errors for {subj} and {session} on vtk file {UKF_fname} and injection file {r1_brain_fname} or {mpf_brain_fname}.\n'.format(**pick),)
        print(' \n'.join(results))

print(' \n'.join(errors))
