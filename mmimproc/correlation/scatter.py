import numpy, nibabel, seaborn, pandas
import mmimproc.io.images

def forLowestPvalue(datafiles, variables, statfiles):
    assert len(datafiles) == variables.shape[0] # ensure equally many subjects

    data, affine = mmimproc.io.images.loadStack(datafiles)
    spatialdims = data.shape[1:]

    for varname in variables.columns.values:

        print('Creating scatterplot for '+varname)
        P = nibabel.load(statfiles[varname]['1minp']).get_data()
        R = nibabel.load(statfiles[varname]['r']).get_data()
        voxelIndex = P.argmax()
        voxelCoords = numpy.unravel_index(voxelIndex, spatialdims)
        r =  R.ravel()[voxelIndex]
        braindata = data[(slice(None),)+voxelCoords]
        vardata = variables[varname]
        voxeldata = pandas.DataFrame({'score':variables[varname].values,
                't1':braindata}, index=variables.index.astype(int))

        plot = seaborn.lmplot('score','t1',voxeldata)
        plot.savefig(varname+'.png')


def forClusters(datafiles, variables, clusters, tables):
    assert len(datafiles) == variables.shape[0] # ensure equally many subjects

    data, affine = mmimproc.io.images.loadStack(datafiles)
    spatialdims = data.shape[1:]

    for varname in variables.columns.values:
        vardata = variables[varname]
        for direction in ('pos', 'neg'):
            name = varname+'-'+direction
            labels = tables[name].index.values
            for label in labels:
                pname = '{}__clu{}'.format(name, label)
                print('Creating scatterplot for '+pname)

                braindata = data[slice(None), clusters[name]==label] #nsubjects * nvoxels
                clusterdata =  braindata.mean(axis=1)
                
                clusterframe = pandas.DataFrame({'score':variables[varname].values,
                        't1':clusterdata}, index=variables.index.astype(int))

                plot = seaborn.lmplot('score','t1',clusterframe)
                plot.savefig(pname+'.png')
