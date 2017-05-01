from __future__ import division
from pathlib import *
import pandas, numpy, nibabel
import scipy.ndimage.measurements as measurements
from pylabs.correlation.atlas import mori_region_labels, JHUtracts_region_labels
from pylabs.utils.paths import getnetworkdataroot
fs = Path(getnetworkdataroot())
"""
Reports on and masks clusters of voxels over a certain size.
"""
project = 'bbc'
cluster_report_fname = 'cluster_report.csv'
stats_results_fname = 'stats_results.txt'
# define atlases for labeling
atlases_in_templ_sp_dir = fs/project/'reg'/'atlases_in_template_space'
mori_atlas_vbm = atlases_in_templ_sp_dir/'mori_atlas_reg2template.nii.gz'
JHUtracts_atlas_vbm = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template.nii.gz'
mori_atlas_dwi = atlases_in_templ_sp_dir/'mori_atlas_reg2template_resamp2dwi.nii.gz'
JHUtracts_atlas_dwi = atlases_in_templ_sp_dir/'ilabsJHUtracts0_atlas_reg2template_resamp2dwi.nii.gz'
mori_atlas_vbm_shape = nibabel.load(str(mori_atlas_dwi)).get_data().shape
JHUtracts_atlas_vbm_shape = nibabel.load(str(JHUtracts_atlas_vbm)).get_data().shape
mori_atlas_dwi_shape = nibabel.load(str(mori_atlas_dwi)).get_data().shape
JHUtracts_atlas_dwi_shape = nibabel.load(str(JHUtracts_atlas_dwi)).get_data().shape
mori_atlas_vbm_data = nibabel.load(str(mori_atlas_vbm)).get_data()
JHUtracts_atlas_vbm_data = nibabel.load(str(JHUtracts_atlas_vbm)).get_data()
mori_atlas_dwi_data = nibabel.load(str(mori_atlas_dwi)).get_data()
JHUtracts_atlas_dwi_data = nibabel.load(str(JHUtracts_atlas_dwi)).get_data()

cols = ['k', 'x', 'y', 'z', 'name', 'mori', 'JHU-tracts']

def clusterminsize(statfiles, pcorr, minsize=0):
    """
    statfiles is a dict of behavior variable name and stats eg:  
            stats = {'r': r,
                    'tneg': tneg,
                    'tpos': tpos,
                    '1minp': 1-p, }
            statfiles[behav_var][stats] = ''.format(file_template)
    pcorr is the desired fdr corrected pvalue threshold eg p=0.05
    """

    thresh1minp = 1-pcorr
    varnames = statfiles.keys()
    clustertables = {}
    clustermaps = {}
    for var in varnames:
        fpath = statfiles[var]['1minp']
        newfpath = fpath.replace('.nii','_clumin{}.nii'.format(minsize))
        #bbc specific hooks
        mod = ''
        pool = ''
        if (Path(newfpath).name).split('_')[0] == 'foster' or (Path(newfpath).name).split('_')[0] == 'control':
            pool = (Path(newfpath).name).split('_')[0]
            mod = (Path(newfpath).name).split('_')[1]
        pimg = nibabel.load(fpath)
        pdata = pimg.get_data()
        pdataVector = pdata.ravel()
        pdataVector[pdataVector<thresh1minp] = 0
        affine = pimg.affine

        for direction in ('pos', 'neg'):
            name = var+'-'+direction
            if (Path(newfpath).name).split('_')[0] == 'foster' or (Path(newfpath).name).split('_')[0] == 'control':
                name += '-'+pool+'-'+mod
            print('Clustering stats for '+name)

            tdirfpath = statfiles[var]['t'+direction]
            tdir = nibabel.load(tdirfpath).get_data()
            sigmask = (pdata>thresh1minp) & (tdir > 0)   # boolian of sig voxels

            clustertables[name] = pandas.DataFrame(columns=cols)
            clustertables[name].index.name = name
            clusters, _ = measurements.label(sigmask)
            _, firstIndices = numpy.unique(clusters, return_index=True)
            coords = numpy.unravel_index(firstIndices, sigmask.shape)
            for d, dim in enumerate(('x', 'y', 'z')):
                clustertables[name][dim] = coords[d]
            clustertables[name]['k'] = numpy.bincount(clusters.ravel())
            clustertables[name].drop(0, inplace=True) # get rid of background
            tooSmall = clustertables[name][clustertables[name].k<minsize].index
            clustertables[name].drop(tooSmall, inplace=True)
            clustertables[name].sort_values(by='k',ascending=False, inplace=True)
            clustertables[name]['name'] = name
            clustertables[name].index.name = 'cluster index'
            # atlas regions here
            for idx, row in clustertables[name].iterrows():
                coord = (int(round(row['x'],0)), int(round(row['y'],0)), int(round(row['z'],0)))
                if clusters.shape == mori_atlas_dwi_shape and clusters.shape == JHUtracts_atlas_dwi_shape:
                    clustertables[name].set_value(idx, 'mori', mori_region_labels[int(round(mori_atlas_dwi_data[coord], 0))])
                    clustertables[name].set_value(idx, 'JHU-tracts', JHUtracts_region_labels[int(round(JHUtracts_atlas_dwi_data[coord], 0))])
                elif clusters.shape == mori_atlas_vbm_shape and clusters.shape == JHUtracts_atlas_vbm_shape:
                    clustertables[name].set_value(idx, 'mori', mori_region_labels[int(round(mori_atlas_vbm_data[coord], 0))])
                    clustertables[name].set_value(idx, 'JHU-tracts', JHUtracts_region_labels[int(round(JHUtracts_atlas_vbm_data[coord], 0))])
                else:
                    clustertables[name].set_value(idx, 'mori', 'unknown shape')
                    clustertables[name].set_value(idx, 'JHU-tracts', 'unknown shape')

            print('Kept {}, dropped {} clusters.'.format(clustertables[name].index.size, tooSmall.size)+' in '+direction+' direction for '+pool+' '+var+' '+mod+'\n')
            with open(str(Path(newfpath).parent / stats_results_fname), 'a') as s:
                s.write('Kept {}, dropped {} clusters.'.format(clustertables[name].index.size, tooSmall.size)+' in '+direction+' direction for '+pool+' '+var+' '+mod+'\n')
                if not clustertables[name].empty:
                    clustertables[name].to_csv(str(Path(newfpath).parent / stats_results_fname), columns=cols, mode='a')
            if not clustertables[name].empty:
                with open(str(Path(newfpath).parent / cluster_report_fname), mode='a') as f:
                    clustertables[name].to_csv(str(Path(newfpath).parent / cluster_report_fname), columns=cols, mode='a', header=False)
                tdir_clust = numpy.zeros(len(clusters.ravel()))
                tdir_clust[:] = clusters.ravel()
                tdir_clust[numpy.in1d(clusters.ravel(), tooSmall)] = 0
                tdir_clust = tdir_clust.reshape(clusters.shape)
                tdir_img = nibabel.Nifti1Image(tdir_clust, affine)
                nibabel.save(tdir_img, statfiles[var]['t'+direction].replace('.nii.gz', '_cluster_index.nii.gz'))
            clustermaps[name] = clusters
            pdataVector[numpy.in1d(clusters.ravel(), tooSmall)] = 0
        maskedData = pdataVector.reshape(pdata.shape)
        if 'pos' in name and not clustertables[name].empty or not clustertables[name.replace('pos', 'neg')].empty:
            nibabel.save(nibabel.Nifti1Image(maskedData, affine), newfpath)
            statfiles[var]['1minp'] = newfpath
        elif 'neg' in name and not clustertables[name].empty or not clustertables[name.replace('neg', 'pos')].empty:
            nibabel.save(nibabel.Nifti1Image(maskedData, affine), newfpath)
            statfiles[var]['1minp'] = newfpath
    return statfiles, clustertables, clustermaps
