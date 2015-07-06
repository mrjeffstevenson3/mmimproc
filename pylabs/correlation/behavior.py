import os, numpy
from pylabs.utils import Filesystem

class FslMatFile(object):

    def setData(self, data):
        pass


def csv2fslmat(csvfile, selectSubjects=None, demean=True, groupcol=False,
    filesys=Filesystem()):
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
    if demean:
        dmdata = (sdata-means) # demeaned data
    else:
        dmdata = sdata



    filesys.makedirs('matfiles')
    for m, measure in enumerate(measures):



        c = skipCols+m # column for this measure

        indata = numpy.atleast_2d(dmdata[:, c]).T
        if groupcol:
            indata = numpy.hstack((numpy.ones((nsubjects,1)), indata))
        FslMatFile().setData(indata)

        matfname = 'matfiles/c2b{0:0>2d}s{1}d_{2}.mat'.format(m+5,nsubjects,measure)
        content = ''
        content += '/ContrastName1\t{0}\n'.format(measure)
        content += '/NumWaves\t2\n/NumPoints\t{0}\n'.format(nsubjects)
        content += '/PPheights\t\t{0:.8e} {1:.8e}\n'.format(dmdata[:, c].min(),
            dmdata[:, c].max())
        content += '\n/Matrix\n'
        for s in range(nsubjects):
            content += '1.000000e+00	{0:.8e}\t\n'.format(dmdata[s, c])
        filesys.write(matfname, content)
        print(matfname)

