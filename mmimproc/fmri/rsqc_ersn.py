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
cluster_df_dtypes = {'Cluster Index': 'Int64', 'Voxels': 'Int64', 'MAX': float, 'MAX X (vox)': 'Int64',
                     'MAX Y (vox)': 'Int64', 'MAX Z (vox)': 'Int64', 'COG X (vox)': float, 'COG Y (vox)': float,
                     'COG Z (vox)': float}

def append2fn(fn, newstr):
    """Appends new string to end of file name and before file .nii or .nii.gz extensions.
    """
    if str(Path(fn).parent) == '.':
        return Path(Path(fn).stem).stem + newstr + ''.join(Path(fn).suffixes)
    else:
        return Path(Path(fn).parent, Path(Path(fn).stem).stem + newstr + ''.join(Path(fn).suffixes))


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
radius = 2  # radius of cylinder mask for zstat median calculation
# set up file naming
datadir = ip.fs_local  # enter pathlib or string for BIDS root data directory
proj = 'toddandclark'  # enter BIDS project name
subj = '50320_connect_dn'
sess = 1  # BIDS session number
mod = 'rest_1'  # BIDS modality of interest (here session number appended manually)
stats_dir = 'stats'  # stats folder with stats output
niiname = 'Step0Orig.nii.gz'  # name of raw resting nifti file to process
statsfile = 'zstat1.nii.gz'  # name of z-stat file in stats folder
seedfile = 'shadowreg_centralsignal.nii.gz'  # optional mask file with DN seed ROI
resultsh5 = 'tcj_results1.h5'  # name of results .h5 file to keep all our hard work safe
# dictionary with all stored file and path nomenclature
namedict = {'datadir': datadir, 'proj': proj, 'subj': subj, 'sess': 'session_{0}'.format(sess), 'modality': mod,
            'niiname': niiname, 'radius': radius,
            'maskname': append2fn(niiname, '_mask'), 'snrmaskname': append2fn(niiname, '_snrmask'),
            'statsfile': statsfile,
            'seedfile': seedfile, 'resultsname': resultsh5}

filloneid = np.array([
       [0,  0,  0],
       [0, -1,  0],
       [0, -1,  1],
       [0,  0,  1],
       [0,  1,  1],
       [0,  1,  0],
       [0,  1, -1],
       [0,  0, -1],
       [0, -1, -1]]).astype(np.int)

filltwoid = np.array([
       [0,  0,  0],
       [0, -1,  0],
       [0, -1,  1],
       [0,  0,  1],
       [0,  1,  1],
       [0,  1,  0],
       [0,  1, -1],
       [0,  0, -1],
       [0, -1, -1],
       [0, -2, -1],
       [0, -2,  0],
       [0, -2,  1],
       [0, -2,  2],
       [0, -1,  2],
       [0,  0,  2],
       [0,  1,  2],
       [0,  2,  2],
       [0,  2,  1],
       [0,  2,  0],
       [0,  2, -1],
       [0,  2, -2],
       [0,  1, -2],
       [0,  0, -2],
       [0, -1, -2],
       [0, -2, -2]])

fillthreeid = np.array([
       [0,  0,  0],
       [0, -1,  0],
       [0, -1,  1],
       [0,  0,  1],
       [0,  1,  1],
       [0,  1,  0],
       [0,  1, -1],
       [0,  0, -1],
       [0, -1, -1],
       [0, -2, -1],
       [0, -2,  0],
       [0, -2,  1],
       [0, -2,  2],
       [0, -1,  2],
       [0,  0,  2],
       [0,  1,  2],
       [0,  2,  2],
       [0,  2,  1],
       [0,  2,  0],
       [0,  2, -1],
       [0,  2, -2],
       [0,  1, -2],
       [0,  0, -2],
       [0, -1, -2],
       [0, -2, -2],
       [0, -3, -3],
       [0, -3, -2],
       [0, -3, -1],
       [0, -3, 0],
       [0, -3, 1],
       [0, -3, 2],
       [0, -3, 3],
       [0, -2, 3],
       [0, -1, 3],
       [0, 0, 3],
       [0, 1, 3],
       [0, 2, 3],
       [0, 3, 3],
       [0, 3, 2],
       [0, 3, 1],
       [0, 3, 0],
       [0, 3, -1],
       [0, 3, -2],
       [0, 3, -3],
       [0, 2, -3],
       [0, 1, -3],
       [0, 0, -3],
       [0, -1, -3],
       [0, -2, -3]])

# get cluster info from zstats file into dataframe
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

# figure out number of breaks along x axis and direction in y (+ve=anterior) and z (+ve=superior) direction
# if central y or z vox coord > left then left is posterior and therefore negative y direction and z is inferior and -ve
if cluster_df.loc['central', coordcols[1]] < cluster_df.loc['left', coordcols[1]]:
    cluster_df.loc['left', 'num_y_breaks'] = np.round(cluster_df.T.loc[coordcols[1], 'central'] - cluster_df.T.loc[
                                                                        coordcols[1], 'left']).astype(np.int64)
elif cluster_df.loc['central', coordcols[1]] > cluster_df.loc['left', coordcols[1]]:
    cluster_df.loc['left', 'num_y_breaks'] = np.round(cluster_df.T.loc[coordcols[1], 'left'] - cluster_df.T.loc[
        coordcols[1], 'central']).astype(np.int64)
else:
    cluster_df.loc['left', 'num_y_breaks'] = 0

if cluster_df.loc['central', coordcols[2]] < cluster_df.loc['left', coordcols[2]]:
    cluster_df.loc['left', 'num_z_breaks'] = np.round(cluster_df.T.loc[coordcols[2], 'central'] - cluster_df.T.loc[
                                                                        coordcols[2], 'left']).astype(np.int64)
elif cluster_df.loc['central', coordcols[2]] > cluster_df.loc['left', coordcols[2]]:
    cluster_df.loc['left', 'num_z_breaks'] = np.round(cluster_df.T.loc[coordcols[2], 'left'] - cluster_df.T.loc[
        coordcols[2], 'central']).astype(np.int64)
else:
    cluster_df.loc['left', 'num_z_breaks'] = 0

# now right side
if cluster_df.loc['central', coordcols[1]] < cluster_df.loc['right', coordcols[1]]:
    cluster_df.loc['right', 'num_y_breaks'] = np.round(cluster_df.T.loc[coordcols[1], 'right'] - cluster_df.T.loc[
                                                                        coordcols[1], 'central']).astype(np.int64)
elif cluster_df.loc['central', coordcols[1]] > cluster_df.loc['right', coordcols[1]]:
    cluster_df.loc['right', 'num_y_breaks'] = np.round(cluster_df.T.loc[coordcols[1], 'central'] - cluster_df.T.loc[
        coordcols[1], 'right']).astype(np.int64)
else:
    cluster_df.loc['right', 'num_y_breaks'] = 0

if cluster_df.loc['central', coordcols[2]] < cluster_df.loc['right', coordcols[2]]:
    cluster_df.loc['right', 'num_z_breaks'] = np.round(cluster_df.T.loc[coordcols[2], 'right'] - cluster_df.T.loc[
                                                                        coordcols[2], 'central']).astype(np.int64)
elif cluster_df.loc['central', coordcols[2]] > cluster_df.loc['right', coordcols[2]]:
    cluster_df.loc['right', 'num_z_breaks'] = np.round(cluster_df.T.loc[coordcols[2], 'central'] - cluster_df.T.loc[
        coordcols[2], 'right']).astype(np.int64)
else:
    cluster_df.loc['right', 'num_z_breaks'] = 0

# set data types
cluster_df_dtypes.update({'dist2central': 'Int64', 'num_y_breaks': 'Int64', 'num_z_breaks': 'Int64',})
cluster_df = cluster_df.round({'dist2central': 0, 'num_y_breaks': 0, 'num_z_breaks': 0})
cluster_df['Cluster Index'] = pd.to_numeric(cluster_df['Cluster Index']).astype('Int64')
cluster_df = cluster_df.astype(cluster_df_dtypes)

# set up for drawing line
cluster_df['radius'] = radius
start_coord = cluster_df.loc['central', coordcols].values.astype(np.int64)
left_end_coord = cluster_df.loc['left', coordcols].values.astype(np.int64)
right_end_coord = cluster_df.loc['right', coordcols].values.astype(np.int64)
cluster_df['y_break_offset'] = cluster_df['dist2central'] // (np.abs(cluster_df['num_y_breaks']) + 1)
cluster_df['z_break_offset'] = cluster_df['dist2central'] // (np.abs(cluster_df['num_z_breaks']) + 1)
lt_y_break_coord, lt_z_break_coord, rt_y_break_coord, rt_z_break_coord = [], [], [], []
# left side we subtract from x
if np.abs(cluster_df.loc['left', 'num_y_breaks']) > 0:
    for y in range(1, np.abs(cluster_df.loc['left', 'num_y_breaks'])+1, 1):
        lt_y_break_coord.append(start_coord[0] - cluster_df.loc['left', 'y_break_offset'])
if np.abs(cluster_df.loc['left', 'num_z_breaks']) > 0:
    for y in range(1, np.abs(cluster_df.loc['left', 'num_z_breaks'])+1, 1):
        lt_z_break_coord.append(start_coord[0] - cluster_df.loc['left', 'z_break_offset'])
# right side we add to x
if np.abs(cluster_df.loc['right', 'num_y_breaks']) > 0:
    for y in range(1, np.abs(cluster_df.loc['right', 'num_y_breaks'])+1, 1):
        rt_y_break_coord.append(start_coord[0] + cluster_df.loc['right', 'y_break_offset'])
if np.abs(cluster_df.loc['right', 'num_z_breaks']) > 0:
    for y in range(1, np.abs(cluster_df.loc['right', 'num_z_breaks'])+1, 1):
        rt_z_break_coord.append(start_coord[0] + cluster_df.loc['right', 'z_break_offset'])

# distance in x direction counters. left descends so negative
left_xrange = range(cluster_df.loc['central', coordcols[0]], cluster_df.loc['left', coordcols[0]] - 1, -1)
right_xrange = range(cluster_df.loc['central', coordcols[0]], cluster_df.loc['right', coordcols[0]] + 1, 1)
left_roirange = range(2, len(left_xrange) + 2)
right_roirange = range(102, len(right_xrange) + 102)
left_coord2roi, right_coord2roi = {}, {}
for k, v in zip(left_xrange, left_roirange):
    left_coord2roi[k] = [v]
for k, v in zip(right_xrange, right_roirange):
    right_coord2roi[k] = [v]

zstat_img = nib.load('{datadir}/{proj}/{subj}/{sess}/stats/{statsfile}'.format(**namedict))
zstat_data = np.asanyarray(zstat_img.dataobj).astype(np.float64)
cyl_mask_data = np.zeros(zstat_img.shape, dtype=np.int64)
left_line, right_line = {}, {}

# left line and cylinder
curr_pos = cluster_df.loc['central', coordcols].values.astype(np.int64)
for x, i in zip(left_xrange, left_roirange):
    curr_pos[0] = x
    if curr_pos[0] in lt_y_break_coord:
        if cluster_df.loc['left', 'num_y_breaks'] > 0:
            curr_pos[1] = curr_pos[1] + 1
        elif cluster_df.loc['left', 'num_y_breaks'] < 0:
            curr_pos[1] = curr_pos[1] - 1
    if curr_pos[0] in lt_z_break_coord:
        if cluster_df.loc['left', 'num_z_breaks'] > 0:
            curr_pos[2] = curr_pos[2] + 1
        elif cluster_df.loc['left', 'num_z_breaks'] < 0:
            curr_pos[2] = curr_pos[2] - 1
    if ip.mopts.verbose:
        print(curr_pos, x, i)
    left_line[str(curr_pos)] = zstat_data[tuple(curr_pos)]
    if radius == 2:
        cyl_mask_data[tuple(zip(*(curr_pos + filloneid)))] = i
    if radius == 3:
        cyl_mask_data[tuple(zip(*(curr_pos + filltwoid)))] = i
    if radius == 4:
        cyl_mask_data[tuple(zip(*(curr_pos + fillthreeid)))] = i
    cyl_mask_data[tuple(curr_pos)] = i
    if radius > 4 or radius < 1:
        raise ValueError("Only radius values between 1 and 4 are permitted")

cluster_df.loc['left', pd.Series(left_line).idxmin()] = pd.Series(left_line).min()
if radius > 1:
    for lt_roi in left_roirange:
        cluster_df.loc['left', lt_roi] = np.median(zstat_data[cyl_mask_data == lt_roi])
cluster_df.loc['left', 'roi_min'] = cluster_df.T.loc[left_roirange,'left'].min()
# now do right side
curr_pos = cluster_df.loc['central', coordcols].values.astype(np.int64)
for x, i in zip(right_xrange, right_roirange):
    curr_pos[0] = x
    if curr_pos[0] in rt_y_break_coord:
        if cluster_df.loc['right', 'num_y_breaks'] > 0:
            curr_pos[1] = curr_pos[1] + 1
        elif cluster_df.loc['right', 'num_y_breaks'] < 0:
            curr_pos[1] = curr_pos[1] - 1
    if curr_pos[0] in rt_z_break_coord:
        if cluster_df.loc['right', 'num_z_breaks'] > 0:
            curr_pos[2] = curr_pos[2] + 1
        elif cluster_df.loc['right', 'num_z_breaks'] < 0:
            curr_pos[2] = curr_pos[2] - 1
    if ip.mopts.verbose:
        print(curr_pos, x, i)
    right_line[str(curr_pos)] = zstat_data[tuple(curr_pos)]
    if radius == 2:
        cyl_mask_data[tuple(zip(*(curr_pos + filloneid)))] = i
    if radius == 3:
        cyl_mask_data[tuple(zip(*(curr_pos + filltwoid)))] = i
    if radius == 4:
        cyl_mask_data[tuple(zip(*(curr_pos + fillthreeid)))] = i
    cyl_mask_data[tuple(curr_pos)] = i
    if radius > 4 or radius < 1:
        raise ValueError("Only radius values between 1 and 4 are permitted")

cluster_df.loc['right', pd.Series(right_line).idxmin()] = pd.Series(right_line).min()
if radius > 1:
    for rt_roi in right_roirange:
        cluster_df.loc['right', rt_roi] = np.median(zstat_data[cyl_mask_data == rt_roi])
cluster_df.loc['right', 'roi_min'] = cluster_df.T.loc[right_roirange,'right'].min()
cluster_df = pd.concat([cluster_df, pd.DataFrame({'line_coords': [left_line, right_line],}, index=['left', 'right'])],
                       axis=1)
# save cylinder mask as nifi file
nib.save(nib.Nifti1Image(cyl_mask_data, zstat_img.affine, zstat_img.header),
         '{datadir}/{proj}/{subj}/{sess}/stats/masktestfile_radius{radius}.nii.gz'.format(**namedict))

# save cluster_df into h5 file
df2h5(cluster_df, '{datadir}/{proj}/{resultsname}'.format(**namedict),
      '/{subj}/{sess}/{modality}/DMN_qc_stats'.format(**namedict), append=False)

#.reset_index(level=0)







####################################################################################################################
tempdf = pd.DataFrame(
    {'y_break_coords': [lt_y_break_coord, rt_y_break_coord], 'z_break_coords': [lt_z_break_coord, rt_z_break_coord]},
    index=['left', 'right'])

cluster_df = pd.concat([cluster_df, tempdf], axis=1)
cluster_df.loc['central', ['y_break_coords', 'z_break_coords']] = 0

"""
left side line has 14 points (dist2central) and 1 break upward because positive at 1/2 way point or 28 - 7 = 21
because we are heading left so decreasing x so subtract.
counters needed: x coord start central and stop (left x) and range count (dist)
y break coords: 
start_coord[0] - (cluster_df.loc['left', 'dist2central'] // (cluster_df.loc['left', 'num_y_breaks'] + 1))
if x counter = 21 = in y_break_coords or z_break_coords
then we must add/subtract from y and z here. left is both lower and more posterior so subtract 1 from both,
update starting coord and continue till end x coord
"""


# make mask to hold line and cylinder
zstat_img = nib.load('{datadir}/{proj}/{subj}/{sess}/stats/{statsfile}'.format(**namedict))
cyl_mask_data = np.zeros(zstat_img.shape, dtype=np.int64)


cyl_mask_data[tuple(zip(*((curr_pos + (-1,0,0)) + filloneid)))] = 2







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





# for i in range(np.abs(cluster_df.loc['left', 'num_y_breaks']).astype('Int64')):
# if cluster_df.loc['left', 'num_y_breaks'] < 2:
#     cluster_df.at['left', 'y_break_coords'] = np.append([np.array([cluster_df.loc['left', 'y_break_coords']])],
#                                                     np.array([- ((cluster_df.T.loc[coordcols[0], 'central']
#                                                                   - cluster_df.T.loc[coordcols[0], 'left']) //
#                                                                  (cluster_df.loc['left', 'num_y_breaks'] + 1)) +
#                                                         cluster_df.T.loc[coordcols[0], 'central']]).astype('Int64'))
