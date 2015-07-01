import os, numpy


def csv2fslmat(csvfile, selectSubjects=None):
    # Create FSL matrix files for correlation from behavioral data in a csv file

    skipCols = 4
    with open(csvfile) as csv:
        lines = csv.readlines()
    data = numpy.loadtxt(csvfile, skiprows=2)
    measures = lines[1].split()[skipCols:]

    if selectSubjects is not None:
        allsubjects = data[:,0].astype(int)
        selection = numpy.array([s in selectSubjects for s in allsubjects])
        data = data[selection,:]
    nsubjects = data.shape[0]

    sdata = data[data[:,0].argsort()] #sort order of subjects
    means = sdata.mean(axis=0) #per-measure average
    dmdata = (sdata-means) # demeaned data

    os.makedirs('matfiles')
    for m, measure in enumerate(measures):
        c = skipCols+m # column for this measure
        matfname = 'matfiles/{0}.mat'.format(measure)
        with open(matfname, 'w') as matfile:
            matfile.write('/ContrastName1\t{0}\n'.format(measure))
            matfile.write('/NumWaves\t2\n/NumPoints\t{0}\n'.format(nsubjects))
            matfile.write('/PPheights\t\t{0:.8e} {1:.8e}\n'.format(dmdata[:, c].min(),
                dmdata[:, c].max()))
            matfile.write('\n/Matrix\n')
            for s in range(nsubjects):
                matfile.write('1.000000e+00	{0:.8e}\t\n'.format(dmdata[s, c]))
        print(matfname)

