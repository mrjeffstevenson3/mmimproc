from pathlib import *
import pandas as pd
import numpy as np
import os, six
import mne
import nibabel as nib
import math
import statsmodels as sm
import csv
from scipy import stats as ss
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
project = 'bbc'
# first set up the 3 cortical thickness dataframes as input
contrl_sid = ['sub-bbc209', 'sub-bbc211', 'sub-bbc208', 'sub-bbc202', 'sub-bbc249', 'sub-bbc241', 'sub-bbc243', 'sub-bbc231', 'sub-bbc253']
foster_sid = ['sub-bbc101', 'sub-bbc105', 'sub-bbc106', 'sub-bbc108', 'sub-bbc113', 'sub-bbc116', 'sub-bbc118', 'sub-bbc119', 'sub-bbc120']
lh_ct = pd.DataFrame.from_csv(fs/project/'grp_parc_stats_lh_cortical_thickness.csv', index_col=None)
rh_ct = pd.DataFrame.from_csv(fs/project/'grp_parc_stats_rh_cortical_thickness.csv', index_col=None)


lh_ct['Subjid'] = lh_ct['lh.aparc.a2009s.thickness'].str.partition('/').drop([2,1], axis=1)
lh_ct = lh_ct.set_index(['Subjid'])
lh_ct = lh_ct.drop('lh.aparc.a2009s.thickness', axis=1)
lh_ct = lh_ct.transpose().astype('float')
rh_ct['Subjid'] = rh_ct['rh.aparc.a2009s.thickness'].str.partition('/').drop([2,1], axis=1)
rh_ct = rh_ct.set_index(['Subjid'])
rh_ct = rh_ct.drop('rh.aparc.a2009s.thickness', axis=1)
rh_ct = rh_ct.transpose().astype('float')


lh_ct_ctrl = lh_ct[contrl_sid]
lh_ct_fost = lh_ct[foster_sid]
lh_ct['209-101'] = lh_ct['sub-bbc209'] - lh_ct['sub-bbc101']
lh_ct['211-105'] = lh_ct['sub-bbc211'] - lh_ct['sub-bbc105']
lh_ct['208-106'] = lh_ct['sub-bbc208'] - lh_ct['sub-bbc106']
lh_ct['202-108'] = lh_ct['sub-bbc202'] - lh_ct['sub-bbc108']
lh_ct['249-113'] = lh_ct['sub-bbc249'] - lh_ct['sub-bbc113']
lh_ct['241-116'] = lh_ct['sub-bbc241'] - lh_ct['sub-bbc116']
lh_ct['243-118'] = lh_ct['sub-bbc243'] - lh_ct['sub-bbc118']
lh_ct['231-119'] = lh_ct['sub-bbc231'] - lh_ct['sub-bbc119']
lh_ct['253-120'] = lh_ct['sub-bbc253'] - lh_ct['sub-bbc120']
lh_paired_sub = lh_ct[['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']]
lh_paired_sub = lh_paired_sub.transpose()

lh_ct_stats = lh_paired_sub.apply(ss.ttest_1samp, axis=0, args=(0.0,)).apply(pd.Series)
lh_ct_stats.columns = ['lh-tstat', 'lh-p-value']
lh_ct_stats.index.name = 'Region'
lh_ct_stats['Region'] = lh_ct_stats.index.str.replace('lh_', '').str.replace('_thickness', '')
lh_sig_results = lh_ct_stats[lh_ct_stats['lh-p-value'] <= 0.05].sort_values(by='lh-p-value')
lh_sig_results.set_index('Region')

rh_ct['209-101'] = rh_ct['sub-bbc209'] - rh_ct['sub-bbc101']
rh_ct['211-105'] = rh_ct['sub-bbc211'] - rh_ct['sub-bbc105']
rh_ct['208-106'] = rh_ct['sub-bbc208'] - rh_ct['sub-bbc106']
rh_ct['202-108'] = rh_ct['sub-bbc202'] - rh_ct['sub-bbc108']
rh_ct['249-113'] = rh_ct['sub-bbc249'] - rh_ct['sub-bbc113']
rh_ct['241-116'] = rh_ct['sub-bbc241'] - rh_ct['sub-bbc116']
rh_ct['243-118'] = rh_ct['sub-bbc243'] - rh_ct['sub-bbc118']
rh_ct['231-119'] = rh_ct['sub-bbc231'] - rh_ct['sub-bbc119']
rh_ct['253-120'] = rh_ct['sub-bbc253'] - rh_ct['sub-bbc120']
rh_paired_sub = rh_ct[['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']]
rh_paired_sub = rh_paired_sub.transpose()

rh_ct_stats = rh_paired_sub.apply(ss.ttest_1samp, axis=0, args=(0.0,)).apply(pd.Series)
rh_ct_stats.columns = ['rh-tstat', 'rh-p-value']
rh_ct_stats.index.name = 'Region'
rh_ct_stats['Region'] = rh_ct_stats.index.str.replace('rh_', '').str.replace('_thickness', '')
rh_sig_results = rh_ct_stats[rh_ct_stats['rh-p-value'] <= 0.05].sort_values(by='rh-p-value')
rh_sig_results.set_index('Region')
# merge stat results
rh_sig_results.merge(lh_sig_results, left_on='Region', right_on='Region', how='outer').fillna('').set_index('Region').sort_values(['rh-p-value', 'lh-p-value'])

# read in verticees to test against
label_dir = fs / project / 'reg' / 'ants_vbm_pairedLH_in_template_space' / 'template_hires_br_freesurf_v6' / 'label' / 'test'
label_flist = label_dir.glob('*.label')
all_labels = {}
for label_fname in label_flist:
        label = 'ctx_' + str(label_fname.name).replace('.label', '').replace('.', '_')
        all_labels[label] = []
        reader = csv.reader(open(str(label_fname)), skipinitialspace=True, delimiter=' ')
        #skip 1st 2 lines
        next(reader, None)
        next(reader, None)
        for row in reader:
            all_labels[label].append(int(row[0]))

# read, find region, replace, write new thickness file
lh_ct_fname = fs/project/'reg'/'ants_vbm_pairedLH_in_template_space'/'template_hires_br_freesurf_v6'/'surf'/'lh.thickness.asc'
lh_contrl_mean_ct_fname = fs/project/'reg'/'ants_vbm_pairedLH_in_template_space'/'template_hires_br_freesurf_v6'/'surf'/'lh.meanthickness_contrl.asc'
lh_fost_mean_ct_fname = fs/project/'reg'/'ants_vbm_pairedLH_in_template_space'/'template_hires_br_freesurf_v6'/'surf'/'lh.meanthickness_foster.asc'
lh_mean_diff_ct_fname = fs/project/'reg'/'ants_vbm_pairedLH_in_template_space'/'template_hires_br_freesurf_v6'/'surf'/'lh.mean_diff_thickness.asc'

with open(str(lh_ct_fname), 'rb') as lh_ct , open(str(lh_contrl_mean_ct_fname), 'wb') as lh_contrl_mean_ct , \
        open(str(lh_fost_mean_ct_fname), 'wb') as lh_fost_mean_ct, \
        open(str(lh_mean_diff_ct_fname), 'wb') as lh_mean_diff_ct:
    reader = csv.reader(lh_ct, skipinitialspace=True, delimiter=' ')
    cntrl_writer = csv.writer(lh_contrl_mean_ct, delimiter=' ')
    foster_writer = csv.writer(lh_fost_mean_ct, delimiter=' ')
    diff_writer = csv.writer(lh_mean_diff_ct, delimiter=' ')
    for row in reader:
        # get vertex
        vert = int(row[0])
        # get region
        region = [k for k, v in all_labels.iteritems() if vert in v][0]
        if region == '':
            cntrl_thickn = [2.785]
            foster_thickn = [2.7127]
            diff_thickn = [0.0732]
        else:
            region = region.replace('ctx_', '') + '_thickness'
            try:
                cntrl_thickn = [round(lh_ct_ctrl.mean(axis=1)[region], 5)]
                foster_thickn = [round(lh_ct_fost.mean(axis=1)[region], 5)]
                diff_thickn = [round(lh_paired_sub.mean(axis=0).loc[region], 5)]
            except:
                cntrl_thickn = [2.785]
                foster_thickn = [2.7127]
                diff_thickn = [0.0732]
                print ('exception caught in region '+region)
        new_ctrl_row = row[:4] + cntrl_thickn
        new_foster_row = row[:4] + foster_thickn
        new_diff_row = row[:4] + diff_thickn

        cntrl_writer.writerow(new_ctrl_row)
        foster_writer.writerow(new_foster_row)
        diff_writer.writerow(new_diff_row)


