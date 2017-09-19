# this is awraper function for mrs that collects the disparate mrs data, calculates group stats, and output to google spreadsheet.
# first set global root data directory
import pylabs
pylabs.datadir.target = 'scotty'
from pathlib import *
import datetime
import numpy as np
import pandas as pd
import json
from pylabs.utils import ProvenanceWrapper, getnetworkdataroot, appendposix, replacesuffix
from pylabs.projects.nbwr.file_names import project
prov = ProvenanceWrapper()

fs = Path(getnetworkdataroot())

cols = [u'left-percCSF', u'left-GABA', u'left-NAAplusNAAG', u'left-GPCplusPCh', u'left-CrplusPCr', u'left-mIns', u'left-Glu-80ms', u'right-percCSF', u'right-GABA', u'right-NAAplusNAAG', u'right-GPCplusPCh', u'right-CrplusPCr', u'right-mIns', u'right-Glu-80ms']
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
right_side_glu = glu_data[1::2]
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
onerowpersubj = onerowpersubj[cols].T
onerowpersubj.reindex_axis(sorted(onerowpersubj.columns), axis=1)
onerowpersubj.drop(exclude_subj, axis=1, inplace=True)
# now get gaba data
for s in onerowpersubj.columns:
    mrs_dir = fs / project / s / 'ses-1' / 'mrs'
    gaba_fits_logf = sorted(list(mrs_dir.glob('mrs_gaba_log*.json')), key=lambda date: int(date.stem.split('_')[-1].replace('log', '')))[-1]
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
    csf_frac.set_index(csf_frac.subject, inplace=True)
    csf_frac.drop(['subject'], axis=1, inplace=True)
    onerowpersubj.loc['left-percCSF', s] = csf_frac.loc['left-percCSF', s]
    onerowpersubj.loc['right-percCSF', s] = csf_frac.loc['right-percCSF', s]

uncorr_csv_fname = fs / project / 'stats' / 'mrs' / 'all_nbwr_mrs_uncorr_fits.csv'
if uncorr_csv_fname.is_file():
    uncorr_csv_fname.rename(appendposix(uncorr_csv_fname, '_replaced_on_{:%Y%m%d%H%M}'.format(datetime.datetime.now())))

onerowpersubj.to_csv(str(uncorr_csv_fname), header=True, index=True, na_rep=9999, index_label='metabolite')
writer = pd.ExcelWriter(str(replacesuffix(uncorr_csv_fname, 'xlsx')))
onerowpersubj.T.to_excel(writer, sheet_name='uncorr', index=True, index_label='subject', header=True, freeze_panes=(1,1), na_rep=9999)
onerowpersubj.loc['left-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc['left-percCSF'])
onerowpersubj.loc['right-1over1minfracCSF'] = 1 / (1 - onerowpersubj.loc['right-percCSF'])

onerowpersubj = onerowpersubj.T
left_metab = ['left-GABA', 'left-NAAplusNAAG', 'left-GPCplusPCh', 'left-CrplusPCr', 'left-mIns', 'left-Glu-80ms']
right_metab = [ 'right-GABA', 'right-NAAplusNAAG', 'right-GPCplusPCh', 'right-CrplusPCr', 'right-mIns', 'right-Glu-80ms']

lt_corrmetab = onerowpersubj[left_metab].multiply(onerowpersubj['left-1over1minfracCSF'], axis='index')
rt_corrmetab = onerowpersubj[right_metab].multiply(onerowpersubj['right-1over1minfracCSF'], axis='index')

writer.save()