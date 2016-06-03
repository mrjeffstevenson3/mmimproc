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

        fpath = statfiles[var]['1minp']
        newfpath = fpath.replace('.nii','_clumin{}.nii'.format(minsize))
        pimg = nibabel.load(fpath)
        pdata = pimg.get_data()
        pdataVector = pdata.ravel()
        pdataVector[pdataVector<thresh1minp] = 0
        affine = pimg.get_affine()

        for direction in ('pos', 'neg'):
            name = var+'-'+direction
            print('Clustering stats for '+name)

            tdirfpath = statfiles[var]['t'+direction]
            tdir = nibabel.load(tdirfpath).get_data()
            sigmask = (pdata>thresh1minp) & (tdir > 0)

            clustertables[name] = pandas.DataFrame(columns = ['k', 'x', 'y', 'z'])
            clusters, _ = measurements.label(sigmask)
            _, firstIndices = numpy.unique(clusters, return_index=True)
            coords = numpy.unravel_index(firstIndices, sigmask.shape)
            for d, dim in enumerate(('x', 'y', 'z')):
                clustertables[name][dim] = coords[d]
            clustertables[name]['k'] = numpy.bincount(clusters.ravel())
            clustertables[name].drop(0, inplace=True) # get rid of background
            tooSmall = clustertables[name][clustertables[name].k<minsize].index
            clustertables[name].drop(tooSmall, inplace=True)
            clustertables[name].sort_values(by='k',ascending=False)
            print('Kept {}, dropped {} clusters.'.format(
                clustertables[name].index.size, tooSmall.size))
            clustertables[name].to_csv('clusters_'+name+'.tsv', sep='\t')
            clustermaps[name] = clusters
            pdataVector[numpy.in1d(clusters.ravel(), tooSmall)] = 0
        maskedData = pdataVector.reshape(pdata.shape)
        nibabel.save(nibabel.Nifti1Image(maskedData, affine), newfpath)
        statfiles[var]['1minp'] = newfpath
    return statfiles, clustertables, clustermaps
