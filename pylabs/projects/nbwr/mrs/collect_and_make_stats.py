# this is awraper function for mrs that collects the disparate mrs data, calculates group stats, and output to google spreadsheet.
# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import datetime
import numpy as np
import pandas as pd
import scipy.stats as ss
import json
from pylabs.utils import ProvenanceWrapper, getnetworkdataroot, appendposix, bumptodefunct, WorkingContext, run_subprocess, pylabs_dir
from pylabs.projects.nbwr.file_names import project
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())

stats_fpgm = pylabs_dir / 'pylabs/projects/nbwr/mrs/nbwr_spreadsheet_sep19_2017'

uncorr_cols = [u'left-percCSF', u'left-GABA', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms', u'right-percCSF', u'right-GABA', u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms']
corr_cols = [u'left-GABA', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms', u'left-GluOverGABA', u'right-GABA', u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms', u'right-GluOverGABA']
exclude_subj = ['sub-nbwr997', 'sub-nbwr998', 'sub-nbwr999',]
exclude_data = ['Scan', 'Hemisphere', 'short_FWHM', 'short_SNR', 'short_TE', 'long_FWHM', 'long_SNR', 'long_TE']
right_col_map = {'NAA+NAAG': 'right-NAAplusNAAG', 'GPC+PCh': 'right-GPCplusPCh', 'Cr+PCr': 'right-CrplusPCr', 'mIns': 'right-mIns', 'Glu': 'right-Glu-80ms'}
left_col_map = {'NAA+NAAG': 'left-NAAplusNAAG', 'GPC+PCh': 'left-GPCplusPCh', 'Cr+PCr': 'left-CrplusPCr', 'mIns': 'left-mIns', 'Glu': 'left-Glu-80ms'}
stats_dir = fs/project/'stats'/'mrs'
glu_fname = 'Paros_Chemdata_tablefile_Sep19_2017.txt'
glu_data = pd.read_csv(str(stats_dir/glu_fname), delim_whitespace=True)
#need to edit a few subject ids
ids2rename = {'NBWR404c': 'NBWR404', 'NWBR999B': 'NBWR999'}
glu_data.set_index(['Scan'], inplace=True)
glu_data.rename(index=ids2rename, inplace=True)


glu_data['subject'] = glu_data.index.str.replace('NBWR', 'sub-nbwr')
glu_data['region'] = glu_data['Hemisphere'].map({'LT': 'left-insula', 'RT': 'right-insula'})
glu_data['method'] = 'lcmodel'
glu_data.reset_index(inplace=True)
glu_data.drop(exclude_data, axis=1, inplace=True)
right_side_glu = glu_data.loc[1::2]
left_side_glu = glu_data.loc[::2]
right_side_glu.copy('deep')
left_side_glu.copy('deep')
right_side_glu.rename(columns=right_col_map, inplace=True)
left_side_glu.rename(columns=left_col_map, inplace=True)
right_side_glu.set_index('subject', inplace=True)
left_side_glu.set_index('subject', inplace=True)
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

# make output file names
base_fname = fs / project / 'stats' / 'mrs' / 'all_nbwr_mrs'
uncorr_csv_fname = appendposix(base_fname, '_uncorr_fits.csv')
csfcorr_csv_fname = appendposix(base_fname, '_results_csfcorr_fits.csv')
excel_fname = appendposix(base_fname, '_results_csfcorr_fits.xlsx')
hdf_fname = appendposix(base_fname, '_results_csfcorr_fits.h5')
fcsf_corr_fname = base_fname.parent / 'csfcorrected.csv'
fstats_fname =  base_fname.parent / 'stats_tvalue.csv'

# save old versions if there
for file in [uncorr_csv_fname, csfcorr_csv_fname, excel_fname, hdf_fname, fcsf_corr_fname, fstats_fname]:
    bumptodefunct(file)

# do fortran stats 1st
onerowpersubj.to_csv(str(uncorr_csv_fname), header=True, index=True, na_rep=9999, index_label='metabolite')

rlog = ()
with WorkingContext(str(uncorr_csv_fname.parent)):
    with open('numcol.txt', mode='w') as nc:
        nc.write(str(len(onerowpersubj.columns)) + '\n')
    with open('numrow.txt', mode='w') as nr:
        nr.write(str(len(onerowpersubj.index)+1) + '\n')
    rlog += run_subprocess(str(stats_fpgm))

onerowpersubj.loc['left-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc['left-percCSF'])
onerowpersubj.loc['right-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc['right-percCSF'])

onerowpersubj = onerowpersubj.T
left_metab = ['left-GABA', 'left-NAAplusNAAG', 'left-GPCplusPCh', 'left-CrplusPCr', 'left-mIns', 'left-Glu-80ms']
right_metab = [ 'right-GABA', 'right-NAAplusNAAG', 'right-GPCplusPCh', 'right-CrplusPCr', 'right-mIns', 'right-Glu-80ms']

lt_corrmetab = onerowpersubj[left_metab].multiply(onerowpersubj['left-1over1minfracCSF'], axis='index')
rt_corrmetab = onerowpersubj[right_metab].multiply(onerowpersubj['right-1over1minfracCSF'], axis='index')
lt_corrmetab['left-GluOverGABA'] = lt_corrmetab['left-Glu-80ms']/lt_corrmetab['left-GABA']
rt_corrmetab['right-GluOverGABA'] = rt_corrmetab['right-Glu-80ms']/rt_corrmetab['right-GABA']
corr_metab = pd.merge(lt_corrmetab, rt_corrmetab, left_index=True, right_index=True)
corr_metab.to_csv(str(csfcorr_csv_fname), header=True, columns=corr_cols, index=True, na_rep=9999, index_label='corr_metabolite')

asd_grp = corr_metab.index.str.replace('sub-nbwr', '').astype('int') < 400  # ASD only
tvalues, pvalues = ss.ttest_ind(corr_metab[asd_grp], corr_metab[~asd_grp], equal_var=False)
descriptives = corr_metab.groupby(asd_grp.astype(int)).describe()
descriptives.rename(index={0: 'control', 1: 'asd'}, inplace=True)
descriptives.index.rename('descriptives', inplace=True)

#organise stats results here
fcsf_corr = pd.DataFrame.from_csv(str(fcsf_corr_fname))
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
fstats.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=9, startcol=0)
descriptives.to_excel(writer, sheet_name='stats', index_label='stats', header=True, startrow=22, startcol=0)
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


