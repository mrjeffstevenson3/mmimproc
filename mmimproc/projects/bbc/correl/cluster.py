# incomplete cluster analysis prog. in codus interuptus

from pathlib import *
import pandas as pd
import numpy as np
import nibabel as nib
from mmimproc.correlation.atlas import mori_region_labels
from mmimproc.alignment.resample import reslice_roi
from mmimproc.utils.paths import getnetworkdataroot
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.projects.bbc.pairing import foster_behav_data, control_behav_data, behav_list

#set up roi
provenance = ProvenanceWrapper()
fs = mmimproc.fs
project = 'bbc'
statsdir = fs/project/'stats'/'py_correl_3rdpass'
cluster_results_file = 'cluster_results_v5.txt'