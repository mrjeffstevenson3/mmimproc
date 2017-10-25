# this is awraper function for mrs that collects the disparate mrs data, calculates group stats, and output to google spreadsheet.
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
from pylabs.utils import ProvenanceWrapper, getnetworkdataroot, appendposix, bumptodefunct, WorkingContext, run_subprocess, pylabs_dir
from pylabs.projects.nbwr.file_names import project
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())

#define fortran programs
stats_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/nbwr_spreadsheet_sep19_2017'
corr_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/nbwr_spreadsheet_sep27_correlations_13_3'
plot_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/makeplots_nbwr.txt'

# define input/output file names
stats_dir = fs/project/'stats'/'mrs'
glu_fname = 'Paros_Chemdata_tablefile_Neva.txt'
jonah_glu_fname = 'jonah_Chemdata_tablefile_reformat2017-10-4.csv'
base_fname = fs / project / 'stats' / 'mrs' / 'all_nbwr_mrs'
uncorr_csv_fname = appendposix(base_fname, '_uncorr_fits.csv')
csfcorr_csv_fname = appendposix(base_fname, '_results_csfcorr_fits.csv')
excel_fname = appendposix(base_fname, '_results_csfcorr_fits.xlsx')
hdf_fname = appendposix(base_fname, '_results_csfcorr_fits.h5')
fcsf_corr_fname = base_fname.parent / 'csfcorrected.csv'
fstats_fname =  base_fname.parent / 'stats_tvalue.csv'

# set up matlab runtime engine
eng = matlab.engine.start_matlab("-nodesktop")
eng.addpath(eng.genpath(str(pylabs_dir)))
eng.addpath(eng.genpath(str(stats_dir)))

# save old data file versions if there
for file in [uncorr_csv_fname, csfcorr_csv_fname, excel_fname, hdf_fname, fcsf_corr_fname, fstats_fname]:
    bumptodefunct(file)

#define dataframe col names
uncorr_cols = [u'left-percCSF', u'left-GABA', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms', u'right-percCSF', u'right-GABA', u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms']
corr_cols = [u'left-GABA', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms', u'left-GluOverGABA', u'right-GABA', u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms', u'right-GluOverGABA']
ftran_cols = [u'csfcorrected_left-GABA             ', u'csfcorrected_left-NAAplusNAAG      ', u'csfcorrected_left-GPCplusPCh       ', u'csfcorrected_left-CrplusPCr        ', u'csfcorrected_left-mIns             ', u'csfcorrected_left-Glu-80ms         ', u'csfcorrected_glu_gaba_ratio_left   ', u'csfcorrected_right-GABA            ', u'csfcorrected_right-NAAplusNAAG     ', u'csfcorrected_right-GPCplusPCh      ', u'csfcorrected_right-CrplusPCr       ', u'csfcorrected_right-mIns            ', u'csfcorrected_right-Glu-80ms        ', u'csfcorrected_glu_gaba_ratio_right  ']
exclude_subj = ['sub-nbwr997', 'sub-nbwr998', 'sub-nbwr999',]
exclude_data = ['Scan', 'Hemisphere', 'short_FWHM', 'short_SNR', 'short_TE', 'long_FWHM', 'long_SNR', 'long_TE']
right_col_map = {'NAA+NAAG': 'right-NAAplusNAAG', 'GPC+PCh': 'right-GPCplusPCh', 'Cr+PCr': 'right-CrplusPCr', 'mIns': 'right-mIns', 'Glu': 'right-Glu-80ms'}
left_col_map = {'NAA+NAAG': 'left-NAAplusNAAG', 'GPC+PCh': 'left-GPCplusPCh', 'Cr+PCr': 'left-CrplusPCr', 'mIns': 'left-mIns', 'Glu': 'left-Glu-80ms'}
ftran2py_col_map = dict(zip(ftran_cols, corr_cols))
left_metab = ['left-GABA', 'left-NAAplusNAAG', 'left-GPCplusPCh', 'left-CrplusPCr', 'left-mIns', 'left-Glu-80ms']
right_metab = [ 'right-GABA', 'right-NAAplusNAAG', 'right-GPCplusPCh', 'right-CrplusPCr', 'right-mIns', 'right-Glu-80ms']

behav_cols_of_interest = [u'VCI Composite', u'PRI Composite', u'FSIQ-4 Composite', u'FSIQ-2 Composite']  # options: u'SRS-2 Total T-Score', u'Awr T-Score', u'Cog T-Score', u'Com T-Score', u'Mot T-Score', u'RRB T-Score', u'SCI T-Score'
behav_col_map = {'VCI Composite':  'VCI-Composite','PRI Composite':  'PRI-Composite', 'FSIQ-4 Composite':  'FSIQ-4-Composite', 'FSIQ-2 Composite': 'FSIQ-2-Composite'}
behav_to_correlate = ['VCI-Composite', 'PRI-Composite',  'FSIQ-4-Composite', 'FSIQ-2-Composite']
metab_to_correlate = [ u'right-Glu-80ms', u'right-GluOverGABA']
ftran_cols_to_correlate = [u'csfcorrected-right-Glu-80ms        ', u'csfcorrected-glu-gaba-ratio-right  ']
# get neva's lc model csv file
glu_data = pd.read_csv(str(stats_dir/glu_fname), delim_whitespace=True)
#need to edit a few subject ids
ids2rename = {'NBWR404c': 'NBWR404', 'NWBR999B': 'NBWR999'}
glu_data.set_index(['Scan'], inplace=True)
glu_data.rename(index=ids2rename, inplace=True)

# prepare data for merge
glu_data['subject'] = glu_data.index.str.replace('NBWR', 'sub-nbwr')
glu_data['region'] = glu_data['Hemisphere'].map({'LT': 'left-insula', 'RT': 'right-insula'})
glu_data['method'] = 'lcmodel'
glu_data.reset_index(inplace=True)
glu_data.drop(exclude_data, axis=1, inplace=True)
right_side_glu = glu_data.loc[1::2]
left_side_glu = glu_data.loc[::2]
right_side_glu.copy('deep')
left_side_glu.copy('deep')
right_side_glu.set_index('subject', inplace=True)
left_side_glu.set_index('subject', inplace=True)
right_side_glu.to_hdf(hdf_fname, 'right_side_glutamate_and_other_metabolites', mode='a', format='t', append=True, data_columns=right_side_glu.columns)
left_side_glu.to_hdf(hdf_fname, 'left_side_glutamate_and_other_metabolites', mode='a', format='t', append=True, data_columns=left_side_glu.columns)
right_side_glu.rename(columns=right_col_map, inplace=True)
left_side_glu.rename(columns=left_col_map, inplace=True)

# get jonah comparison data
jonah_glu_data = pd.read_csv(str(stats_dir/jonah_glu_fname))
jonah_glu_data.set_index('subject', inplace=True)
jonah_glu_data.rename(columns=left_col_map, inplace=True)
jonah_glu_data.drop(exclude_data[1:], axis=1, inplace=True)
jonah_glu_data['left-percCSF'] = np.nan
jonah_glu_data['left-GABA']  = np.nan
jonah_glu_data = jonah_glu_data.T
for ses in ['1','2']:
    mrs_dir = fs / 'tadpole' / 'sub-tadpole001' / str('ses-'+ses) / 'mrs'
    jonah_gaba_fits_logf = sorted(list(mrs_dir.rglob('mrs_gaba_log*.json')),
                            key=lambda date: int(date.stem.split('_')[-1].replace('log', '')))[-1]
    with open(str(jonah_gaba_fits_logf), 'r') as gf:
        log_data = json.load(gf)
    for line in log_data:
        if 'Left gaba results' in line:
            lt_gaba_val = float(line.split()[3])
            jonah_glu_data.loc['left-GABA', 'sub-tadpole00'+ses] = lt_gaba_val
    csf_frac = pd.read_csv(str(mrs_dir / 'sub-tadpole001_csf_fractions.csv'))
    csf_frac.set_index('sub-tadpole001', inplace=True)
    jonah_glu_data.loc['left-percCSF', 'sub-tadpole00'+ses] = csf_frac.loc['left-percCSF'].values[0]

jonah_glu_data = jonah_glu_data.T
jonah_glu_data['left-1over1minfracCSF'] = 1 / (1 - jonah_glu_data.loc[:, 'left-percCSF'])
jonah_lt_corrmetab = jonah_glu_data[left_metab].multiply(jonah_glu_data['left-1over1minfracCSF'], axis='index')
jonah_lt_corrmetab['left-GluOverGABA'] = jonah_lt_corrmetab['left-Glu-80ms']/jonah_lt_corrmetab['left-GABA']
#save jonah data to hdf
jonah_lt_corrmetab.to_hdf(hdf_fname, 'jonah_left_csf_corrected_mrs_data', mode='a', format='t', append=True, data_columns=jonah_lt_corrmetab.columns)

onerowpersubj = pd.merge(left_side_glu, right_side_glu, left_index=True, right_index=True)
onerowpersubj['left-percCSF'] = np.nan
onerowpersubj['right-percCSF']  = np.nan
onerowpersubj['left-GABA']  = np.nan
onerowpersubj['right-GABA']  = np.nan
onerowpersubj = onerowpersubj[uncorr_cols].T
onerowpersubj.reindex_axis(sorted(onerowpersubj.columns), axis=1)
onerowpersubj.drop(exclude_subj, axis=1, inplace=True)
# now get gaba data
for s in onerowpersubj.columns:
    print('working on '+s)
    mrs_dir = fs / project / s / 'ses-1' / 'mrs'
    if len(list(mrs_dir.rglob('mrs_gaba_log*.json'))) in [0,[],None]:
        raise ValueError('mrs_gaba_log file missing for '+s+'. make sure gaba fit was run with MRSfit subdirs in mrs dir.')
    else:
        gaba_fits_logf = sorted(list(mrs_dir.rglob('mrs_gaba_log*.json')), key=lambda date: int(date.stem.split('_')[-1].replace('log', '')))[-1]
    with open(str(gaba_fits_logf), 'r') as gf:
        log_data = json.load(gf)
    for line in log_data:
        if 'Left gaba results' in line:
            lt_gaba_val = float(line.split()[3])
        if 'Right gaba results' in line:
            rt_gaba_val = float(line.split()[3])

    onerowpersubj.loc['right-GABA', s] = rt_gaba_val
    onerowpersubj.loc['left-GABA', s] = lt_gaba_val

    csf_frac = pd.read_csv(str(mrs_dir / str(s + '_csf_fractions.csv')))
    csf_frac.set_index(s, inplace=True)
    onerowpersubj.loc['left-percCSF', s] = csf_frac.loc['left-percCSF'][0]
    onerowpersubj.loc['right-percCSF', s] = csf_frac.loc['right-percCSF'][0]

# behavior data
behav_fname = stats_dir / 'GABA.xlsx'
behav_raw = pd.read_excel(str(behav_fname), sheetname='ASD tracking')
behav_raw['subject'] = behav_raw['Subject #'].str.replace('GABA_', 'sub-nbwr')
behav_raw.set_index(['subject'], inplace=True)
behav_data = behav_raw[behav_cols_of_interest]
behav_data.rename(columns=behav_col_map, inplace=True)
behav_data.copy('deep')
behav_data.sort_index(inplace=True)

# do fortran stats 1st
onerowpersubj.to_csv(str(uncorr_csv_fname), header=True, index=True, na_rep=9999, index_label='metabolite')

rlog = ()
with WorkingContext(str(uncorr_csv_fname.parent)):
    with open('numcol2.txt', mode='w') as nc:
        nc.write(str(2) + '\n')
    with open('numrow2.txt', mode='w') as nr:
        nr.write(str(len(behav_data.index)+1) + '\n')
    with open('numcol3.txt', mode='w') as nc:
        nc.write(str(len(onerowpersubj.columns)) + '\n')
    with open('numrow3.txt', mode='w') as nr:
        nr.write(str(len(onerowpersubj.index)+1) + '\n')
    with open('all_nbwr_uncorr.txt', mode='w') as ufn:
        ufn.write(uncorr_csv_fname.name + '\n')
    with open('all_nbwr.txt', mode='w') as cfn:
        cfn.write(fcsf_corr_fname.name + '\n')  # was csfcorr_csv_fname.name
    rlog += run_subprocess(str(stats_fpgm))

onerowpersubj = onerowpersubj.T
onerowpersubj['left-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc[:,'left-percCSF'])
onerowpersubj['right-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc[:,'right-percCSF'])

lt_corrmetab = onerowpersubj[left_metab].multiply(onerowpersubj['left-1over1minfracCSF'], axis='index')
rt_corrmetab = onerowpersubj[right_metab].multiply(onerowpersubj['right-1over1minfracCSF'], axis='index')
lt_corrmetab['left-GluOverGABA'] = lt_corrmetab['left-Glu-80ms']/lt_corrmetab['left-GABA']
rt_corrmetab['right-GluOverGABA'] = rt_corrmetab['right-Glu-80ms']/rt_corrmetab['right-GABA']
corr_metab = pd.merge(lt_corrmetab, rt_corrmetab, left_index=True, right_index=True)
corr_metab.to_csv(str(csfcorr_csv_fname), header=True, columns=corr_cols, index=True, na_rep=9999, index_label='corr_metabolite')
corr_metab.to_hdf(hdf_fname, 'CSFcorrected_mrs_data', mode='a', format='t', append=True, data_columns=corr_metab.columns)

asd_grp = corr_metab.index.str.replace('sub-nbwr', '').astype('int') < 400  # ASD only
tvalues, pvalues = ss.ttest_ind(corr_metab[asd_grp], corr_metab[~asd_grp], equal_var=False)
descriptives = corr_metab.groupby(asd_grp.astype(int)).describe()
descriptives.rename(index={0: 'control', 1: 'asd'}, inplace=True)
descriptives.index.rename('descriptives', inplace=True)

#organise stats results here
fstats = pd.DataFrame.from_csv(str(fstats_fname))
stats_results = pd.DataFrame.from_dict({'t-stat': tvalues, 'p-value': pvalues})
if len(stats_results.T.columns) == len(corr_cols) == len(corr_metab.columns):
    col_map = {}
    for n, c in zip(range(0, len(corr_metab.columns)), corr_metab.columns):
        col_map[n] = c
else:
    mismatch = [len(stats_results.T.columns), len(corr_cols), len(corr_metab.columns)]
    raise ValueError('stats result cols do not match. stats='+str(mismatch[0])+' corr_cols='+str(mismatch[1])+' metab cols='+str(mismatch[2]))
stats_results.rename(index=col_map,inplace=True)
hdr_txt = {'fortran': 'Stats results from todds fortran code', 'scipy_stats': 'summary t-stats and p-values from python stats', 'descriptive': 'Additional descriptive stats from pandas'}
stats_hdrs = pd.Series(hdr_txt)

# now do fortran correlations
with WorkingContext(str(uncorr_csv_fname.parent)):
    with open('numcol1.txt', mode='w') as nc:
        nc.write(str(len(corr_metab.columns)) + '\n'+str(len(corr_metab.columns)) + '\n')
    with open('numrow1.txt', mode='w') as nr:
        nr.write(str(len(corr_metab.index)+1) + '\n'+str(len(corr_metab.index)+1) + '\n')
    # read back in results of stats
    fcsf_corr = pd.DataFrame.from_csv(str(fcsf_corr_fname))
    fcsf_corr_colrename = fcsf_corr.rename(columns=ftran2py_col_map)
    # loop over correlation
    for mb in itertools.product(ftran_cols_to_correlate, behav_to_correlate):
        # pick column number
        with open('chosen_metabolite.txt', mode='w') as cmet:
            cmet.write(str(fcsf_corr_colrename.columns.get_loc(mb[0])+1) + '\n')
        behav_data.to_csv('behav_corr.csv', header=True, columns=[mb[1]], index=True, na_rep=9999, index_label='subject')
        with open('gaba_scores.txt', mode='w') as gs:
            gs.write('behav_corr.csv' + '\n')
        rlog += run_subprocess(str(corr_fpgm))
        rlog += run_subprocess(str(plot_fpgm))
        rlog += run_subprocess(['octave GenSpec.m'])
        # now save results to new file names
        newname = uncorr_csv_fname.parent / ('_'.join(mb)+'_corr_plot_{:%Y%m%d%H%M}.jpg'.format(datetime.datetime.now()))
        Path(uncorr_csv_fname.parent / 'mrsbehav.jpg').rename(newname)


#write excel workbook and matching h5 dataframes
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

onerowpersubj.to_excel(writer, sheet_name='uncorr', columns=uncorr_cols, index=True, index_label='subject', header=True, startrow=1, na_rep=9999)

onerowpersubj.to_hdf(hdf_fname, 'uncorrected_mrs_data', mode='a', format='t', append=True, data_columns=onerowpersubj.columns)

uncorr_worksheet = writer.sheets['uncorr']
uncorr_worksheet.set_default_row(25)
uncorr_worksheet.set_column('B:O', 24, data_format)
uncorr_worksheet.set_column('A:A', 18, labels_format)
uncorr_worksheet.write_string(0,0,'Uncorrected fit data and CSF correction factor', title_format)

corr_metab.to_excel(writer, sheet_name='corr_metab', columns=corr_cols, index=True, index_label='subject', header=True, startrow=1, na_rep=9999)
corr_worksheet = writer.sheets['corr_metab']
corr_worksheet.set_default_row(25)
corr_worksheet.set_column('B:O', 24, data_format)
corr_worksheet.set_column('A:A', 18, labels_format)
corr_worksheet.write_string(0,0,'Corrected Metabolite Concentration after CSF correction factor applied', title_format)
fcsf_corr.to_excel(writer, sheet_name='fortran_corr', index=True, index_label='subject', header=True, startrow=1, na_rep=9999)
fcsf_worksheet = writer.sheets['fortran_corr']
fcsf_worksheet.set_default_row(25)
fcsf_worksheet.set_column('B:O', 24, data_format)
fcsf_worksheet.set_column('A:A', 18, labels_format)
fcsf_worksheet.write_string(0,0,'Corrected Metabolite Concentration after CSF correction factor applied', title_format)
stats_results.T.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=2, startcol=0)
stats_results.T.to_hdf(hdf_fname, 'CSFcorrected_mrs_stats', mode='a', format='t', append=True, data_columns=stats_results.T.columns)
fstats.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=9, startcol=0)
descriptives.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=22, startcol=0)
descriptives.to_hdf(hdf_fname, 'CSFcorrected_mrs_descriptive_stats', mode='a', format='t', append=True, data_columns=descriptives.columns)

stats_worksheet = writer.sheets['stats']
stats_worksheet.set_column('B:O', 24, data_format)
stats_worksheet.set_default_row(25)
stats_worksheet.set_column('A:A', 18, labels_format)
stats_worksheet.write_string(0,0,'Summary t-stats and p-values from python stats', title_format)
stats_worksheet.write_string(7,0,'Stats results from todds fortran code', title_format)
stats_worksheet.write_string(20,0,'Additional descriptive stats from pandas', title_format)
stats_worksheet.write_string(28,0,'Selected Correlations:', title_format)
stats_worksheet.set_row(18, {'align': 'left'})
stats_worksheet.set_row(19, {'align': 'left'})
#stats_worksheet.conditional_format('B4:O4', {'type': 'cell', 'criteria': '<=', 'value': 0.05, 'bg_color': '#FFC7CE'})
writer.save()


