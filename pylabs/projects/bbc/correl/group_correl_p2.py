# this script generates the subtracted and unsubtracted fsl mat files for group and correlation stats
from pathlib import *
import pandas as pd
import numpy as np
from scipy.stats import spearmanr as sp_correl
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.correlation.correlate import wholeBrain
from pylabs.projects.bbc.pairing import FA_foster_pnames, FA_control_pnames, \
    MD_foster_pnames, MD_control_pnames, RD_foster_pnames, RD_control_pnames, \
    AD_foster_pnames, AD_control_pnames, foster_paired_behav_subjs, control_paired_behav_subjs

provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())
project = 'bbc'
behav_csv_name = 'bbc_behav_2-22-2017_rawsub.csv'
results_dirname = 'py_correl_1stpass'
behav_list = [(u'21', u'PATrhyTotSS') , (u'22', u'PATsegTotSS') , (u'23', u'CTOPPphoaCS')  ,(u'24', u'CTOPPrnCS') ,(u'25', u'CTOPPphomCS'), (u'26', u'PPVTSS'), (u'27', u'TOPELeliSS') ,(u'28', u'STIMQ-PSDSscaleScore1-to-15-SUM'), (u'29', u'self-esteem-IAT')]
csvraw = fs / project / 'behavior' / behav_csv_name
mat_outdir = fs / project / 'stats' / 'matfiles'
results_dir = fs / project / 'stats' / results_dirname
data = pd.read_csv(str(csvraw), header=[0,1], index_col=1, tupleize_cols=True)

foster_data = data.loc[foster_paired_behav_subjs, behav_list]
control_data = data.loc[control_paired_behav_subjs, behav_list]

if not mat_outdir.is_dir():
    mat_outdir.mkdir(parents=True)
if not results_dir.is_dir():
    results_dir.mkdir(parents=True)


