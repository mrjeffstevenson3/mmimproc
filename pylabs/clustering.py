from __future__ import division
from pathlib import *
import pandas, numpy, nibabel
import scipy.ndimage.measurements as measurements

"""
Reports on and masks clusters of voxels over a certain size.
"""

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
        affine = pimg.affine()

        for direction in ('pos', 'neg'):
            name = var+'-'+direction
            if (Path(newfpath).name).split('_')[0] == 'foster' or (Path(newfpath).name).split('_')[0] == 'control':
                name += '-'+pool+'-'+mod
            print('Clustering stats for '+name)

            tdirfpath = statfiles[var]['t'+direction]
            tdir = nibabel.load(tdirfpath).get_data()
            sigmask = (pdata>thresh1minp) & (tdir > 0)

            clustertables[name] = pandas.DataFrame(columns = ['k', 'x', 'y', 'z'])
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
            print('Kept {}, dropped {} clusters.'.format(clustertables[name].index.size, tooSmall.size)+' for '+pool+' '+var+' '+mod+'\n')
            with open(str(Path(newfpath).parent / 'stats_results.txt'), 'a') as f:
                f.write('Kept {}, dropped {} clusters.'.format(clustertables[name].index.size, tooSmall.size)+' for '+pool+' '+var+' '+mod+'\n')
            clustertables[name].to_csv(str(Path(newfpath).parent / str('clusters_results.csv')), mode='a', header=False)
            clustermaps[name] = clusters
            pdataVector[numpy.in1d(clusters.ravel(), tooSmall)] = 0
        maskedData = pdataVector.reshape(pdata.shape)
        nibabel.save(nibabel.Nifti1Image(maskedData, affine), newfpath)
        statfiles[var]['1minp'] = newfpath
    return statfiles, clustertables, clustermaps
