from __future__ import division
import numpy, nibabel, scipy.stats


def correlateWholeBrain(files, variables):
    assert len(files) == variables.shape[0] # ensure equally many subjects
    nsubjects = variables.shape[0]
    nvars = variables.shape[1]
    data = []
    shapes = []
    for f, fpath in enumerate(files):
        print('Loading image {} of {}..'.format(f+1, len(files)))
        img = nibabel.load(fpath)
        sdata = img.get_data()
        shapes.append(sdata.shape)
        data.append(sdata)
    data = numpy.array(data)
    affine = img.get_affine()
    for shape in shapes:
        assert shape==shapes[0] # ensure images have same dimensions
    print('Vectorizing and masking..')
    spatialdims = data.shape[1:]
    nvoxels = numpy.prod(spatialdims)
    data2d = data.reshape((nsubjects, nvoxels))
    mask1d = (data2d>0).all(axis=0)
    mdata2d = data2d[:, mask1d]
    nvalid = mask1d.sum()
    print('{0:.1f}% of voxels in mask.'.format(nvalid/nvoxels*100))

    result2d = numpy.zeros((nvars, nvalid))
    for v, varname in enumerate(variables.columns.values):
        print('Correlating variable {}, {} of {}'.format(varname, v+1, nvars))
        X = mdata2d
        Y = variables[varname].values

        mx = X.mean(axis=0, keepdims=True)
        my = Y.mean(axis=0, keepdims=True)
        xm, ym = X-mx, Y-my
        r_num = (xm.T * ym).mean(axis=1)
        r_den = X.std(axis=0) * Y.std()
        r = r_num / r_den

        result2d[v, :] = r

    x = mdata2d[:,0]
    y = variables.iloc[:,0]
    assert result2d[0,0] == scipy.stats.pearsonr(x,y)[0]

    output2d = numpy.zeros((nvars, nvoxels))
    output2d[:, mask1d] = result2d
   
    print('Unvectorizing and saving to file..')
    output4d = output2d.reshape((nvars,) + spatialdims)
    for v, varname in enumerate(variables.columns.values):
        img = nibabel.Nifti1Image(output4d[v,:,:,:], affine)
        nibabel.save(img, 'corr_{}.nii.gz'.format(varname))




