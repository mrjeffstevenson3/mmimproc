import nibabel, seaborn
import pylabs.io.images

def forLowestPvalue(datafiles, variables, statfiles):
    assert len(datafiles) == variables.shape[0] # ensure equally many subjects

    data, affine = pylabs.io.images.loadStack(datafiles)
    spatialdims = data.shape[1:]

    for varname in variables.columns.values:

        print('Creating scatterplot for '+varname)
        P = nibabel.load(statfiles[varname]['2minp']).get_data()
        R = nibabel.load(statfiles[varname]['r']).get_data()
        voxelIndex = P.argmax()
        voxelCoords = numpy.unravel_index(voxelIndex, spatialdims)
        r =  R.ravel()[pmax]
        braindata = data[(slice(None),)+voxelCoords]
        vardata = variables[varname]
        voxeldata = pandas.DataFrame({'score':variables[varname].values,
                't1':braindata}, index=variables.index.astype(int))

        plot = seaborn.lmplot('score','t1',voxeldata)
        plot.savefig(varname+'.png')
