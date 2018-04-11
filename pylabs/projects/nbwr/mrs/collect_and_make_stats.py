# this is a wrapper function for mrs that collects the disparate mrs data, calculates group stats, and output to google spreadsheet.
# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import datetime
import numpy as np
import pandas as pd
import scipy.stats as ss
import itertools
import json
import matlab.engine
from pylabs.io.mixed import get_h5_keys, h52df, df2h5
from pylabs.utils import *
from pylabs.projects.nbwr.file_names import project
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())
include_jonah = False  # broken

# define fortran programs
stats_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/nbwr_spreadsheet_sep19_2017'
corr_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/nbwr_spreadsheet_sep27_correlations_13_3'
plot_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/makeplots_nbwr.txt'

# define input/output file names
all_info_fname = fs/project/'all_{project}_info.h5'.format(**{'project': project})
stats_dir = fs/project/'stats'/'mrs'
glu_fname = 'Paros_Chemdata_tablefile.txt'
jonah_glu_fname = 'jonah_Chemdata_tablefile_reformat2017-10-4.csv'
base_fname = fs / project / 'stats' / 'mrs' / 'all_nbwr_mrs'
uncorr_csv_fname = appendposix(base_fname, '_uncorr_fits.csv')
csfcorr_csv_fname = appendposix(base_fname, '_results_csfcorr_fits.csv')
excel_fname = appendposix(base_fname, '_results_csfcorr_fits.xlsx')
hdf_fname = appendposix(base_fname, '_results_csfcorr_fits.h5')
fcsf_corr_fname = base_fname.parent / 'csfcorrected.csv'
fstats_fname = base_fname.parent / 'stats_tvalue.csv'

# for todds correlation plots
# set up matlab runtime engine - disable for manual runs
# eng = matlab.engine.start_matlab("-noFigureWindows -nodesktop -nodisplay -nosplash")    #"-nodesktop" or try "-nodisplay"
# eng.addpath(eng.genpath(str(pylabs_dir)))
# eng.addpath(eng.genpath(str(stats_dir)))
# eng.cd(str(stats_dir))
# print("current matlab working directory is " + str(eng.pwd()))

# save old data file versions if there
for afile in [uncorr_csv_fname, csfcorr_csv_fname, excel_fname, hdf_fname, fcsf_corr_fname, fstats_fname]:
    bumptodefunct(afile)

# define dataframe col names
uncorr_cols = [u'left-SPM-percCSF', u'left-FSL-percCSF', u'left-GABA', u'left-gabaovercr', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms',u'right-SPM-percCSF', u'right-FSL-percCSF', u'right-GABA', u'right-gabaovercr',  u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms']
corr_cols = [u'left-GABA', u'left-gabaovercr', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms', u'left-GluOverGABA', u'right-GABA', u'right-gabaovercr', u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms', u'right-GluOverGABA']
ftran_cols = [u'csfcorrected_left-GABA             ', u'csfcorrected_left-NAAplusNAAG      ', u'csfcorrected_left-GPCplusPCh       ', u'csfcorrected_left-CrplusPCr        ', u'csfcorrected_left-mIns             ', u'csfcorrected_left-Glu-80ms         ', u'csfcorrected_glu_gaba_ratio_left   ', u'csfcorrected_right-GABA            ', u'csfcorrected_right-NAAplusNAAG     ', u'csfcorrected_right-GPCplusPCh      ', u'csfcorrected_right-CrplusPCr       ', u'csfcorrected_right-mIns            ', u'csfcorrected_right-Glu-80ms        ', u'csfcorrected_glu_gaba_ratio_right  ']
exclude_subj = []   # ['sub-nbwr997', 'sub-nbwr998', 'sub-nbwr999', ]  # 'sub-nbwr136', 'sub-nbwr447']
exclude_data = ['Scan', 'Hemisphere', 'short_FWHM', 'short_SNR', 'short_TE', 'long_FWHM', 'long_SNR', 'long_TE']
right_col_map = {'NAA+NAAG': 'right-NAAplusNAAG', 'GPC+PCh': 'right-GPCplusPCh', 'Cr+PCr': 'right-CrplusPCr', 'mIns': 'right-mIns', 'Glu': 'right-Glu-80ms', 'region': 'right-region', 'method': 'right-method'}
left_col_map = {'NAA+NAAG': 'left-NAAplusNAAG', 'GPC+PCh': 'left-GPCplusPCh', 'Cr+PCr': 'left-CrplusPCr', 'mIns': 'left-mIns', 'Glu': 'left-Glu-80ms', 'region': 'left-region', 'method': 'left-method'}
ftran2py_col_map = dict(zip(ftran_cols, corr_cols))
# fcsf_corr.columns.str.strip().str.replace('_', '-') use this to change and map new fortran df cols
left_metab = ['left-GABA', 'left-NAAplusNAAG', 'left-GPCplusPCh', 'left-CrplusPCr', 'left-mIns', 'left-Glu-80ms']
right_metab = ['right-GABA', 'right-NAAplusNAAG', 'right-GPCplusPCh', 'right-CrplusPCr', 'right-mIns', 'right-Glu-80ms']
subjs_on_meds = ['sub-nbwr007', 'sub-nbwr081', 'sub-nbwr215', 'sub-nbwr317']

behav_cols_of_interest = [u'VCI Composite', u'PRI Composite', u'FSIQ-4 Composite', u'FSIQ-2 Composite']  # options: u'SRS-2 Total T-Score', u'Awr T-Score', u'Cog T-Score', u'Com T-Score', u'Mot T-Score', u'RRB T-Score', u'SCI T-Score'
behav_col_map = {'VCI Composite':  'VCI-Composite','PRI Composite':  'PRI-Composite', 'FSIQ-4 Composite':  'FSIQ-4-Composite', 'FSIQ-2 Composite': 'FSIQ-2-Composite'}
behav_to_correlate = ['VCI-Composite', 'PRI-Composite',  'FSIQ-4-Composite', 'FSIQ-2-Composite']
metab_to_correlate = [u'right-Glu-80ms', u'right-GluOverGABA']
ftran_cols_to_correlate = [u'csfcorrected-right-Glu-80ms        ', u'csfcorrected-glu-gaba-ratio-right  ']
# get neva's lc model csv file
glu_data = pd.read_csv(str(stats_dir/glu_fname), delim_whitespace=True)
# may not need to edit a few subject ids as of feb 2018
ids2rename = {'NBWR404c': 'NBWR404', 'NWBR999B': 'NBWR999'}
glu_data.set_index(['Scan'], inplace=True)
glu_data.rename(index=ids2rename, inplace=True)

# prepare data for merge
glu_data['subject'] = glu_data.index.str.replace('NBWR', 'sub-nbwr')
glu_data['region'] = glu_data['Hemisphere'].map({'LT': 'left-insula', 'RT': 'right-insula'})
glu_data['method'] = 'lcmodel'
glu_data.reset_index(inplace=True)
glu_data.drop(exclude_data, axis=1, inplace=True)
right_side_glu = glu_data.loc[1::2].copy('deep')  # start row 1 skip every other
left_side_glu = glu_data.loc[::2].copy('deep')  # start row 0 skip every other
right_side_glu.set_index('subject', inplace=True)
left_side_glu.set_index('subject', inplace=True)
right_side_glu.rename(columns=right_col_map, inplace=True)
left_side_glu.rename(columns=left_col_map, inplace=True)
onerowpersubj = pd.merge(left_side_glu, right_side_glu, left_index=True, right_index=True)
onerowpersubj.drop(exclude_subj, axis=1, inplace=True)
# save orig glu fits to h5
df2h5(onerowpersubj, all_info_fname, '/stats/mrs/orig_glu_fits')
# collect CSF Correction and GABA data
csf_corr_keys = sorted(get_h5_keys(str(all_info_fname), 'CSF_correction_factors'))
gaba_keys = sorted(get_h5_keys(str(all_info_fname), 'gaba'))
if not len(csf_corr_keys) == len(gaba_keys):
    raise ValueError('gaba and csf keys not equal. asymetric processing not supported at this time.')
# test data alignment
all_same = []
for i, (c, g) in enumerate(zip(csf_corr_keys, gaba_keys)):
    if c.split('/')[1] == g.split('/')[1]:
        all_same.append(True)
if not all(all_same):
    raise ValueError('Subjects index not aligned in csf and gaba hdf keys. stopping now.')
for csf_k, gaba_k in zip(csf_corr_keys, gaba_keys):
    csf_df = h52df(all_info_fname, csf_k)
    gaba_df = h52df(all_info_fname, gaba_k)
    subj = gaba_k.split('/')[1]
    onerowpersubj.loc[subj, 'left-SPM-percCSF'] = np.float64(csf_df.loc['frac_CSF', 'left_SPM'])
    onerowpersubj.loc[subj, 'right-SPM-percCSF'] = np.float64(csf_df.loc['frac_CSF', 'right_SPM'])
    onerowpersubj.loc[subj, 'left-FSL-percCSF'] = np.float64(csf_df.loc['frac_CSF', 'left_FSL'])
    onerowpersubj.loc[subj, 'right-FSL-percCSF'] = np.float64(csf_df.loc['frac_CSF', 'right_FSL'])
    onerowpersubj.loc[subj, 'left-GABA'] = np.float64(gaba_df.loc['left-gaba', 'gaba_fit_info'])
    onerowpersubj.loc[subj, 'right-GABA'] = np.float64(gaba_df.loc['right-gaba', 'gaba_fit_info'])
    onerowpersubj.loc[subj, 'left-gabaovercr'] = np.float64(gaba_df.loc['left-gabaovercr', 'gaba_fit_info'])
    onerowpersubj.loc[subj, 'right-gabaovercr'] = np.float64(gaba_df.loc['right-gabaovercr', 'gaba_fit_info'])
# calculate CSF correction factor
onerowpersubj['left-SPM-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc[:, 'left-SPM-percCSF'])
onerowpersubj['right-SPM-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc[:, 'right-SPM-percCSF'])
onerowpersubj['left-FSL-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc[:, 'left-FSL-percCSF'])
onerowpersubj['right-FSL-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc[:, 'right-FSL-percCSF'])
# apply correction factor
left_SPMcorr = onerowpersubj[left_metab].multiply(onerowpersubj['left-SPM-1over1minfracCSF'], axis='index')
right_SPMcorr = onerowpersubj[right_metab].multiply(onerowpersubj['right-SPM-1over1minfracCSF'], axis='index')
left_FSLcorr = onerowpersubj[left_metab].multiply(onerowpersubj['left-FSL-1over1minfracCSF'], axis='index')
right_FSLcorr = onerowpersubj[right_metab].multiply(onerowpersubj['right-FSL-1over1minfracCSF'], axis='index')
# calculate ratios for each correction method
left_SPMcorr['left-GluOverGABA'] = left_SPMcorr['left-Glu-80ms']/left_SPMcorr['left-GABA']
left_SPMcorr = left_SPMcorr.join(onerowpersubj['left-gabaovercr'])
right_SPMcorr['right-GluOverGABA'] = right_SPMcorr['right-Glu-80ms']/right_SPMcorr['right-GABA']
right_SPMcorr = right_SPMcorr.join(onerowpersubj['right-gabaovercr'])
SPMcorr_metab = pd.merge(left_SPMcorr, right_SPMcorr, left_index=True, right_index=True)

left_FSLcorr['left-GluOverGABA'] = left_FSLcorr['left-Glu-80ms']/left_FSLcorr['left-GABA']
left_FSLcorr = left_FSLcorr.join(onerowpersubj['left-gabaovercr'])
right_FSLcorr['right-GluOverGABA'] = right_FSLcorr['right-Glu-80ms']/right_FSLcorr['right-GABA']
right_FSLcorr = right_FSLcorr.join(onerowpersubj['right-gabaovercr'])
FSLcorr_metab = pd.merge(left_FSLcorr, right_FSLcorr, left_index=True, right_index=True)

# shortcut to get data to todd
SPMcorr_metab.to_csv(str(stats_dir/'for_todd_SPMcorrected_metabolites.csv'), header=True, index=True, sep=',', float_format='%.8f')
FSLcorr_metab.to_csv(str(stats_dir/'for_todd_FSLcorrected_metabolites.csv'), header=True, index=True, sep=',', float_format='%.8f')
df2h5(SPMcorr_metab, all_info_fname, '/stats/mrs/SPM_CSFcorr_metabolites')
df2h5(FSLcorr_metab, all_info_fname, '/stats/mrs/FSL_CSFcorr_metabolites')

# fetch behavior data
behav_fname = stats_dir / 'GABA_subject_information.xlsx'      # 'GABA.xlsx'
behav_raw = pd.read_excel(str(behav_fname), sheet_name='ASD Tracking')
behav_raw['subject'] = behav_raw['Subject #'].str.replace('GABA_', 'sub-nbwr')
behav_raw.set_index(['subject'], inplace=True)
behav_data = behav_raw[behav_cols_of_interest].copy('deep')
behav_data.rename(columns=behav_col_map, inplace=True)
behav_data.sort_index(inplace=True)

if include_jonah:
    # get jonah comparison data (broken)
    jonah_glu_data = pd.read_csv(str(stats_dir/jonah_glu_fname))
    jonah_glu_data.set_index('subject', inplace=True)
    jonah_glu_data.rename(columns=left_col_map, inplace=True)
    jonah_glu_data.drop(exclude_data[1:], axis=1, inplace=True)
    jonah_glu_data['left-percCSF'] = np.nan
    jonah_glu_data['left-GABA'] = np.nan
    jonah_glu_data = jonah_glu_data.T
    for ses in ['1','2']:
        mrs_dir = fs / 'tadpole' / 'sub-tadpole001' / str('ses-'+ses) / 'mrs'
        jonah_gaba_fits_logf = sorted(list(mrs_dir.rglob('mrs_gaba_log*.json')),
                                key=lambda date: int(date.stem.split('_')[-1].replace('log', '')))[-1]
        with open(str(jonah_gaba_fits_logf), 'r') as gf:
            log_data = json.load(gf)
        for line in log_data:
            if 'Left gaba results' in line:
                lt_gaba_val = np.float64(line.split()[3])
                jonah_glu_data.loc['left-GABA', 'sub-tadpole00'+ses] = lt_gaba_val
        csf_frac = pd.read_csv(str(mrs_dir / 'sub-tadpole001_csf_fractions.csv'))
        csf_frac.set_index('sub-tadpole001', inplace=True)
        jonah_glu_data.loc['left-percCSF', 'sub-tadpole00'+ses] = csf_frac.loc['left-percCSF'].values[0]

    jonah_glu_data = jonah_glu_data.T
    jonah_glu_data['left-1over1minfracCSF'] = 1 / (1 - jonah_glu_data.loc[:, 'left-percCSF'])
    jonah_lt_corrmetab = jonah_glu_data[left_metab].multiply(jonah_glu_data['left-1over1minfracCSF'], axis='index')
    jonah_lt_corrmetab['left-GluOverGABA'] = jonah_lt_corrmetab['left-Glu-80ms']/jonah_lt_corrmetab['left-GABA']
    # save jonah data to hdf
    df2h5(jonah_lt_corrmetab, all_info_fname, '/stats/mrs/jonah_left_CSFcorr_metabolites')


# make scipy python stats
asd_grp = SPMcorr_metab.index.str.replace('sub-nbwr', '').astype('int') < 400  # ASD only
SPM_tvalues, SPM_pvalues = ss.ttest_ind(SPMcorr_metab[asd_grp], SPMcorr_metab[~asd_grp], equal_var=False)
FSL_tvalues, FSL_pvalues = ss.ttest_ind(FSLcorr_metab[asd_grp], FSLcorr_metab[~asd_grp], equal_var=False)
# organise stats results and save to HDF
stats_results = pd.DataFrame.from_dict({'SPMcorr_t-stat': SPM_tvalues, 'SPMcorr_p-value': SPM_pvalues, 'FSLcorr_t-stat': FSL_tvalues, 'FSLcorr_p-value': FSL_pvalues})
if len(stats_results.T.columns) == len(corr_cols) == len(SPMcorr_metab.columns):
    col_map = {}
    for n, c in zip(range(0, len(SPMcorr_metab.columns)), SPMcorr_metab.columns):
        col_map[n] = c
else:
    mismatch = [len(stats_results.T.columns), len(corr_cols), len(SPMcorr_metab.columns)]
    raise ValueError('stats result cols do not match. stats='+str(mismatch[0])+' corr_cols='+str(mismatch[1])+' metab cols='+str(mismatch[2]))
stats_results.rename(index=col_map,inplace=True)
df2h5(stats_results, all_info_fname, '/stats/mrs/all_CSFcorr_metab_stats_group_t_test_results')
# generate descriptive stats DF
SPM_descriptives = SPMcorr_metab.groupby(asd_grp.astype(int)).describe()
SPM_descriptives.rename(index={0: 'control_SPM', 1: 'asd_SPM'}, inplace=True)
SPM_descriptives.index.rename('descriptives', inplace=True)
FSL_descriptives = FSLcorr_metab.groupby(asd_grp.astype(int)).describe()
FSL_descriptives.rename(index={0: 'control_FSL', 1: 'asd_FSL'}, inplace=True)
FSL_descriptives.index.rename('descriptives', inplace=True)
descriptives = pd.merge(SPM_descriptives.T, FSL_descriptives.T, left_index=True, right_index=True)
df2h5(descriptives, all_info_fname, '/stats/mrs/all_CSFcorr_metab_descriptive_stats_results')

# # do fortran stats. export to fortran compat csv.
# rlog = ()
# SPMuncorr_cols = [x for x in uncorr_cols if ('gabaovercr' not in x and 'FSL' not in x)]
# FSLuncorr_cols = [x for x in uncorr_cols if ('gabaovercr' not in x and 'SPM' not in x)]
# fortran seaches for 'left-percCSF' and 'right-percCSF'
# for cols in [SPMuncorr_cols, FSLuncorr_cols]:
#     onerowpersubj.to_csv(str(uncorr_csv_fname), header=True, index=True, columns=cols, na_rep=9999, index_label='metabolite')
#     with WorkingContext(str(uncorr_csv_fname.parent)):
#         with open('numcol2.txt', mode='w') as nc:
#             nc.write(str(2) + '\n')
#         with open('numrow2.txt', mode='w') as nr:
#             nr.write(str(len(behav_data.index)+1) + '\n')
#         with open('numcol3.txt', mode='w') as nc:   # for t-stat
#             nc.write(str(len(cols)) + '\n')
#         with open('numrow3.txt', mode='w') as nr:    # for t-stat
#             nr.write(str(len(onerowpersubj.index) + 1) + '\n')
#         with open('all_nbwr_uncorr.txt', mode='w') as ufn:
#             ufn.write(uncorr_csv_fname.name + '\n')
#         with open('all_nbwr.txt', mode='w') as cfn:
#             cfn.write(fcsf_corr_fname.name + '\n')  # was csfcorr_csv_fname.name
#         rlog += run_subprocess(str(stats_fpgm))


#         if 'left-SPM-percCSF' in cols:
#             SPMcorr_fstats = pd.read_csv(str(fstats_fname))
#         if 'left-FSL-percCSF' in cols:
#             FSLcorr_fstats = pd.read_csv(str(fstats_fname))
# hdr_txt = {'fortran': 'Stats results from todds fortran code', 'scipy_stats': 'summary t-stats and p-values from python stats', 'descriptive': 'Additional descriptive stats from pandas'}
# stats_hdrs = pd.Series(hdr_txt)
#
# # now do fortran correlations
# with WorkingContext(str(stats_dir)):
#     with open('numcol1.txt', mode='w') as nc:
#         nc.write(str(len(corr_metab.columns)) + '\n'+str(len(corr_metab.columns)) + '\n')
#     with open('numrow1.txt', mode='w') as nr:
#         nr.write(str(len(corr_metab.index)+1) + '\n'+str(len(corr_metab.index)+1) + '\n')
#     # read back in results of stats
#     fcsf_corr = pd.DataFrame.from_csv(str(fcsf_corr_fname))
#     fcsf_corr_colrename = fcsf_corr.rename(columns=ftran2py_col_map)
#     # loop over correlation
#     for mb in itertools.product(ftran_cols_to_correlate, behav_to_correlate):
#         # pick column number
#         with open('chosen_metabolite.txt', mode='w') as cmet:
#             cmet.write(str(fcsf_corr_colrename.columns.get_loc(mb[0])+1) + '\n')
#         behav_data.to_csv('behav_corr.csv', header=True, columns=[mb[1]], index=True, na_rep=9999, index_label='subject')
#         with open('gaba_scores.txt', mode='w') as gs:
#             gs.write('behav_corr.csv' + '\n')
#         print("working on "+'_'.join(mb)+" correlations")
#         rlog += run_subprocess(str(corr_fpgm))
#         rlog += run_subprocess(str(plot_fpgm))
#         #rlog += eng.GenSpec(nargout=0)
#         # now save results to new file names
#         newname = stats_dir / ('_'.join(mb)+'_corr_plot_{:%Y%m%d%H%M}.jpg'.format(datetime.datetime.now()))
#         #Path(stats_dir / 'mrsbehav.jpg').rename(newname)

''' 
mrs data saved to hdf file:
    uncorrected metabolites
    raw behavior df
    CSF corrected metab
    fortran stats
    fortran correlations
    python stats
    python correlations

'''

# write excel workbook and matching h5 dataframes
writer = pd.ExcelWriter(str(excel_fname), engine='xlsxwriter')
workbook = writer.book

title_format = workbook.add_format({'bold': True, 'font_size': '24', 'text_wrap': False})
title_format.set_align('vcenter')
title_format.set_align('left')
title_format.set_text_wrap(False)

labels_format = workbook.add_format({'bold': True, 'font_size': '18',})
labels_format.set_align('vcenter')
labels_format.set_align('right')
labels_format.set_text_wrap(False)

data_format = workbook.add_format({'num_format': '0.0000', 'bold': False, 'font_size': '18',})
data_format.set_align('vcenter')
data_format.set_align('center')
data_format.set_text_wrap(False)

# # why write uncorrected to excel 1st?
# onerowpersubj.to_hdf(hdf_fname, 'uncorrected_mrs_data', mode='a', format='t', append=True, data_columns=onerowpersubj.columns)
# onerowpersubj.to_excel(writer, sheet_name='uncorr', columns=uncorr_cols, index=True, index_label='subject', header=True, startrow=1, na_rep=9999)
# uncorr_worksheet = writer.sheets['uncorr']
# uncorr_worksheet.set_default_row(25)
# uncorr_worksheet.set_column('B:O', 24, data_format)
# uncorr_worksheet.set_column('A:A', 18, labels_format)
# uncorr_worksheet.write_string(0,0,'Uncorrected fit data and CSF correction factor', title_format)

# write csf corrected data
SPMcorr_metab.to_excel(writer, sheet_name='SPMcorr_metab', columns=corr_cols, index=True, index_label='subject', header=True, startrow=1, na_rep=9999)
FSLcorr_metab.to_excel(writer, sheet_name='FSLcorr_metab', columns=corr_cols, index=True, index_label='subject', header=True, startrow=1, na_rep=9999)

SPMcorr_worksheet = writer.sheets['SPMcorr_metab']
SPMcorr_worksheet.set_default_row(35)
SPMcorr_worksheet.set_column('B:Q', 24, data_format)
SPMcorr_worksheet.set_column('A:A', 18, labels_format)
SPMcorr_worksheet.write_string(0, 0, 'Corrected Metabolite Concentrations after CSF correction factor applied using SPM segmentation', title_format)

FSLcorr_worksheet = writer.sheets['FSLcorr_metab']
FSLcorr_worksheet.set_default_row(35)
FSLcorr_worksheet.set_column('B:Q', 24, data_format)
FSLcorr_worksheet.set_column('A:A', 18, labels_format)
FSLcorr_worksheet.write_string(0, 0, 'Corrected Metabolite Concentrations after CSF correction factor applied using FSL segmentation', title_format)


# # write fortran corrected data
# fcsf_corr.to_excel(writer, sheet_name='fortran_corr', index=True, index_label='subject', header=True, startrow=1, na_rep=9999)
# fcsf_worksheet = writer.sheets['fortran_corr']
# fcsf_worksheet.set_default_row(25)
# fcsf_worksheet.set_column('B:O', 24, data_format)
# fcsf_worksheet.set_column('A:A', 18, labels_format)
# fcsf_worksheet.write_string(0,0,'Corrected Metabolite Concentration after CSF correction factor applied', title_format)
# fstats.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=9, startcol=0)

stats_results.T.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=2, startcol=0)
# format descriptives as 2 cols SPM and FSL
SPM_descriptives.T.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=22, startcol=0)
FSL_descriptives.T.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=22, startcol=6)

stats_worksheet = writer.sheets['stats']
stats_worksheet.set_column('B:Q', 22, data_format)
stats_worksheet.set_default_row(35)
stats_worksheet.set_column('A:A', 18, labels_format)
stats_worksheet.write_string(0, 0, 'Summary t-stats and p-values from python stats for both SPM and FSL CSF corrected metabolites', title_format)
# stats_worksheet.write_string(7,0,'Stats results from todds fortran code', title_format)
stats_worksheet.write_string(20, 0, 'Additional SPM CSF corrected descriptive stats from pandas', title_format)
stats_worksheet.write_string(20, 6, 'Additional FSL CSF corrected descriptive stats from pandas', title_format)
# stats_worksheet.write_string(28,0,'Selected Correlations:', title_format)
# stats_worksheet.set_row(18, {'align': 'left'})
# stats_worksheet.set_row(19, {'align': 'left'})

# stats_worksheet = writer.sheets['fortran_stats']

writer.save()
# close matlab instance
# eng.quit()

'''
# test of meds interaction stats
import scipy.stats as ss
from statsmodels.stats.multicomp import pairwise_tukeyhsd
# for SPM csf correction
spm_corr_metab = h52df(all_info_fname, '/stats/mrs/SPM_CSFcorr_metabolites')
asd_grp3 = spm_corr_metab.index.str.replace('sub-nbwr', '').astype('int') < 400
spm_corr_metab.loc[asd_grp3, 'group'] = 'asd'
spm_corr_metab.loc[subjs_on_meds, 'group'] = 'asd-meds'
spm_corr_metab.loc[~asd_grp3, 'group'] = 'cntrl'
spm_corr_metab.columns.name = 'metabolites'
spm_corr_metab.set_index('group', append=True, inplace=True)
spm_corr_metab_stacked = spm_corr_metab.stack()
spm_corr_metab_stacked.name = 'values'
for metab_group in spm_corr_metab_stacked.groupby('metabolites'):
    samples = [group[1] for group in metab_group[1].groupby('group')]
    f_val, p_val = ss.f_oneway(*samples)
    print('SPMcorr Metabolite: {}, F value: {:.5f}, p value: {:.5f}'.format(metab_group[0], f_val, p_val))
for metab in spm_corr_metab:
    results = pairwise_tukeyhsd(spm_corr_metab[metab], spm_corr_metab.reset_index(level=1)['group'])
    print('SPMcorr Metabolite {}'.format(metab))
    print(results)

# FSL corrected 
fsl_corr_metab = h52df(all_info_fname, '/stats/mrs/FSL_CSFcorr_metabolites')
asd_grp_fsl = fsl_corr_metab.index.str.replace('sub-nbwr', '').astype('int') < 400
fsl_corr_metab.loc[asd_grp_fsl, 'group'] = 'asd'
fsl_corr_metab.loc[subjs_on_meds, 'group'] = 'asd-meds'
fsl_corr_metab.loc[~asd_grp_fsl, 'group'] = 'cntrl'
fsl_corr_metab.columns.name = 'metabolites'
fsl_corr_metab.set_index('group', append=True, inplace=True)
fsl_corr_metab_stacked = fsl_corr_metab.stack()
fsl_corr_metab_stacked.name = 'values'
for metab_group in fsl_corr_metab_stacked.groupby('metabolites'):
    samples = [group[1] for group in metab_group[1].groupby('group')]
    f_val, p_val = ss.f_oneway(*samples)
    print('FSLcorr Metabolite: {}, F value: {:.5f}, p value: {:.5f}'.format(metab_group[0], f_val, p_val))

for metab in fsl_corr_metab:
    results = pairwise_tukeyhsd(fsl_corr_metab[metab], fsl_corr_metab.reset_index(level=1)['group'])
    print('FSLcorr Metabolite {}'.format(metab))
    print(results)
'''