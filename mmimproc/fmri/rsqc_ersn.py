"""
Testing needed: 1. more than 4 voxels away in y or z direction.
"""
from pathlib import *
from io import StringIO
import itertools
import numpy as np
import pandas as pd
import nibabel as nib
import mmimproc as ip
from mmimproc.io.mixed import df2h5
from mmimproc.utils import run_subprocess
import matplotlib.pyplot as plt
import seaborn as sns

# set display options
sns.set(color_codes=True)
pd.set_option('display.max_colwidth', 90)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

coordcols = ['MAX X (vox)', 'MAX Y (vox)', 'MAX Z (vox)']
cluster_df_dtypes = {'Cluster Index': 'Int64', 'Voxels': 'Int64', 'MAX': float, 'MAX X (vox)': 'Int64', 'MAX Y (vox)': 'Int64',
                 'MAX Z (vox)': 'Int64', 'COG X (vox)': float, 'COG Y (vox)': float, 'COG Z (vox)': float}

def append2fn(fn, newstr):
    """Appends new string to end of file name and before file extentions.
    """
    return Path(fn).stem + newstr + ''.join(Path(fn).suffixes)


def fslcluster2list(cluster_output):
    return [line.split('\t') for line in StringIO(cluster_output.decode('UTF-8')).read().split('\n')]


def fslcluster2DF(fname, thresh, *argv):
    if not Path(fname).is_file():
        raise ValueError('Cannot find stats file ' + str(fname))
    cluster_output = run_subprocess([' '.join(['cluster', '-i', fname, '-t', str(thresh), *argv])])
    cluster_data = fslcluster2list(cluster_output[0])
    cluster_df = pd.DataFrame(cluster_data[1:], columns=cluster_data[0], dtype=np.float)
    cluster_df.replace('', np.nan, inplace=True)
    cluster_df.dropna(how='all', inplace=True)
    cluster_df = cluster_df.astype(cluster_df_dtypes, errors="ignore")
    return cluster_df


ssvolnum = 10  # integer volume number where steady state is acheived
thresh = 9.5  # zstat file fsl cluster threshold
radius = 1  # radius of cylinder mask for zstat median calculation
# set up file naming
datadir = ip.fs_local  # enter pathlib or string for BIDS root data directory
proj = 'toddandclark'  # enter BIDS project name
subj = 'connect_dn'  # enter BIDS subject name (todo: subject list option for for loop)
sess = 1  # BIDS session number
mod = 'rest_1'  # BIDS modality of interest (here session number appended manually)
stats_dir = 'stats'  # stats folder with stats output
niiname = 'Step0Orig.nii.gz'  # name of raw resting nifti file to process (todo: for loop if needed)
statsfile = 'zstat1.nii.gz'  # name of z-stat file in stats folder
seedfile = 'shadowreg_centralsignal.nii.gz'  # optional mask file with DN seed ROI
resultsh5 = 'tcj_results1.h5'  # name of results .h5 file to keep all our hard work safe
# dictionary with all stored nomenclature
namedict = {'datadir': datadir, 'proj': proj, 'subj': subj, 'sess': 'session_{0}'.format(sess), 'modality': mod,
            'niiname': niiname,
            'maskname': append2fn(niiname, '_mask'), 'snrmaskname': append2fn(niiname, '_snrmask'),
            'statsfile': statsfile,
            'seedfile': seedfile, 'resultsname': resultsh5}

cluster_df = fslcluster2DF('{datadir}/{proj}/{subj}/{sess}/stats/{statsfile}'.format(**namedict), thresh)
cluster_df.loc[cluster_df['MAX'].idxmax(axis=1), 'location'] = 'central'
cluster_df.loc[cluster_df.loc[:, 'MAX X (vox)'] < cluster_df.loc[cluster_df.loc[:, 'location'] == 'central']
                ['MAX X (vox)'][0], 'location'] = 'left'
cluster_df.loc[cluster_df.loc[:, 'MAX X (vox)'] > cluster_df.loc[cluster_df.loc[:, 'location'] == 'central']
                ['MAX X (vox)'][0], 'location'] = 'right'
cluster_df.set_index('location', inplace=True)
cluster_df.loc['central', ['dist2central', 'num_y_breaks', 'num_z_breaks']] = 0

# calculate distances from central DN to left and right parietal DN in voxels
cluster_df.loc['right', 'dist2central'] = np.linalg.norm(cluster_df.loc['right', coordcols].values -
                                            cluster_df.loc['central', coordcols].values).round().astype(np.int64)
cluster_df.loc['left', 'dist2central'] = np.linalg.norm(cluster_df.loc['left', coordcols].values -
                                            cluster_df.loc['central', coordcols].values).round().astype(np.int64)


cluster_df.loc['left', 'num_y_breaks'] = np.round(cluster_df.T.loc[coordcols[1], 'central'] - cluster_df.T.loc[
                                                                        coordcols[1], 'left']).astype(np.int64)
cluster_df.loc['left', 'num_z_breaks'] = np.round(cluster_df.T.loc[coordcols[2], 'central'] - cluster_df.T.loc[
                                                                        coordcols[2], 'left']).astype(np.int64)
cluster_df.loc['right', 'num_y_breaks'] = np.round(cluster_df.T.loc[coordcols[1], 'central'] - cluster_df.T.loc[
                                                                        coordcols[1], 'right']).astype(np.int64)
cluster_df.loc['right', 'num_z_breaks'] = np.round(cluster_df.T.loc[coordcols[2], 'central'] - cluster_df.T.loc[
                                                                        coordcols[2], 'right']).astype(np.int64)
cluster_df_dtypes.update({'dist2central': 'Int64', 'num_y_breaks': 'Int64', 'num_z_breaks': 'Int64',})
                          #'y_break_coords': 'Int64', 'z_break_coords': 'Int64'})
cluster_df = cluster_df.round({'dist2central': 0, 'num_y_breaks': 0, 'num_z_breaks': 0})
cluster_df['Cluster Index'] = pd.to_numeric(cluster_df['Cluster Index']).astype('Int64')
cluster_df = cluster_df.astype(cluster_df_dtypes)
tempdf = pd.DataFrame(
    {'y_break_coords': [np.empty((0,), dtype=np.int64)] * 2, 'z_break_coords': [np.empty((0,), dtype=np.int64)] * 2},
    index=['left', 'right'])

cluster_df = pd.concat([cluster_df, tempdf], axis=1)
cluster_df.loc['central', ['y_break_coords', 'z_break_coords']] = 0

for i, j in enumerate(list(itertools.product(*(['left', 'right'], [['num_y_breaks', 'y_break_coords'], ['num_z_breaks', 'z_break_coords']])))):

    if cluster_df.loc[j[0], j[1][0]] > 4:
        raise ValueError("Woops! too far away in the y direction on the left side from center max, shifting no more than 4 voxels for now.")

    for pixmove in range(4, -1, -1):
        if cluster_df.loc[j[0], j[1][0]] == pixmove:
            xshift = cluster_df.loc[j[0], 'dist2central'].round().astype(int) // (pixmove + 1)
            cluster_df.loc[j[0], j[1][1]] = cluster_df.loc[j[0], 'dist2central'] // (pixmove + 1)





        if cluster_df.loc[j[0], j[1][0]] == 4:
            """set up array of x values dividing distance vox by 4 """
        elif cluster_df.loc[j[0], j[1][0]] == 3:
            """set up array of x values dividing distance vox by 3 """
        elif cluster_df.loc[j[0], j[1][0]] == 2:
            """set up array of x values dividing distance vox by 2 """
        elif cluster_df.loc[j[0], j[1][0]] == 1:
            """set up array of x values dividing distance vox by 1 """
        elif cluster_df.loc[j[0], j[1][0]] == 0:
            """set y break coord to x dist2central as int round down """

# todo: do all the same for right side and num_z_breaks. make combination for loop? yes!
# todo: generalize up to max distance in x
# todo: paint lines and build function for cylinder indexed coding




# for i in range(np.abs(cluster_df.loc['left', 'num_y_breaks']).astype('Int64')):
# if cluster_df.loc['left', 'num_y_breaks'] < 2:
#     cluster_df.at['left', 'y_break_coords'] = np.append([np.array([cluster_df.loc['left', 'y_break_coords']])],
#                                                     np.array([- ((cluster_df.T.loc[coordcols[0], 'central']
#                                                                   - cluster_df.T.loc[coordcols[0], 'left']) //
#                                                                  (cluster_df.loc['left', 'num_y_breaks'] + 1)) +
#                                                         cluster_df.T.loc[coordcols[0], 'central']]).astype('Int64'))
