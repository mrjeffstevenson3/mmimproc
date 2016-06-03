from __future__ import division
import pandas, numpy, nibabel
import scipy.ndimage.measurements as measurements

"""
Reports on and masks clusters of voxels over a certain size.
"""

def clusterminsize(statfiles, pcorr, minsize=0):
    thresh1minp = 1-pcorr
    varnames = statfiles.keys()
    clustertables = {}
    clustermaps = {}
    for var in varnames:
        print('Clustering stats for '+var)
        clustertables[var] = pandas.DataFrame(columns = ['k', 'x', 'y', 'z'])
        fpath = statfiles[var]['2minp']
        newfpath = fpath.replace('.nii','_clumin{}.nii'.format(minsize))
        pimg = nibabel.load(fpath)
        pdata = pimg.get_data()
        affine = pimg.get_affine()
        clusters, _ = measurements.label(pdata>thresh1minp)
        _, firstIndices = numpy.unique(clusters, return_index=True)
        coords = numpy.unravel_index(firstIndices, pdata.shape)
        for d, dim in enumerate(('x', 'y', 'z')):
            clustertables[var][dim] = coords[d]
        clustertables[var]['k'] = numpy.bincount(clusters.ravel())
        clustertables[var].drop(0, inplace=True) # get rid of background
        tooSmall = clustertables[var][clustertables[var].k<minsize].index
        clustertables[var].drop(tooSmall, inplace=True)
        clustertables[var].sort_values(by='k',ascending=False)
        print('Kept {}, dropped {} clusters.'.format(
            clustertables[var].index.size, tooSmall.size))
        clustertables[var].to_csv('clusters_'+var+'.tsv', sep='\t')
        pdataVector = pdata.ravel()
        pdataVector[numpy.in1d(pdataVector, tooSmall)] = 0
        maskedData = pdataVector.reshape(pdata.shape)
        nibabel.save(nibabel.Nifti1Image(maskedData, affine), newfpath)
        statfiles[var]['2minp'] = newfpath
        clustermaps[var] = clusters
    return statfiles, clustertables, clustermaps
