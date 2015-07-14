import os, numpy
from pylabs.utils import Filesystem


class FslMatFile(object):
    # Fsl Matrix (.mat) file.

    def __init__(self, filesys=Filesystem()):
        self.filesys = filesys

    def setData(self, data):
        # Data to write to the file as a numpy array. Must be 2d.
        self.data = data

    def saveAs(self, fname):
        content = ''
        #content += '/ContrastName1\t{0}\n'.format(measure)
        (w,p) = self.data.shape
        content += '/NumWaves\t{1}\n/NumPoints\t{0}\n'.format(w,p)
        content += '/PPheights\t\t{0:.6e} {1:.6e}\n'.format(
            self.data.min(), self.data.max())
        content += '/Matrix\n'
        for r in range(self.data.shape[0]):
            for c in range(self.data[r,:].size):
                content += '{0:.6e}\t'.format(self.data[r, c])
            content += '\n'
        self.filesys.write(fname, content)
        print(fname)


def csv2fslmat(csvfile, selectSubjects=None, demean=True, groupcol=False,
    cols=None, covarcols=None, filesys=Filesystem()):
    """Create FSL matrix files from behavioral data in a csv file

    Args:
        csvfile (str): Path to space separated behavioral data file 
        selectSubjects (list): List of subject indices to include (order of no
            consequence). Defaults to all subjects.
        demean (bool): Subtract mean from behavior data. Defaults to True. 
        groupcol (bool): Whether to prepend a column of 1s. Defaults to False.
        cols (list) : Select columns to to create mat files for
        covarcols (list) : Select columns to covary. All of these are included 
            in each matfile created.
        filesys (pylabs.utils.Filesystem): Pass a mock here for testing purpose.

    Returns:
        list: List of mat files created
    """


    with open(csvfile) as csv:
        lines = csv.readlines()
    data = numpy.loadtxt(csvfile, skiprows=2)
    measures = lines[1].split()

    if cols is None:
        # if no columns specified, skip 4 and take all others.
        cols = range(4, len(measures)+1) 

    if selectSubjects is not None:
        allsubjects = data[:,0].astype(int)
        selection = numpy.array([s in selectSubjects for s in allsubjects])
        data = data[selection,:]
    nsubjects = data.shape[0]

    data = data[data[:,0].argsort()] #sort order of subjects

    if demean:
        means = data.mean(axis=0) #per-measure average
        data = (data-means) # demeaned data

    fnames = []
    filesys.makedirs('matfiles')
    for c in cols:
        indata = numpy.atleast_2d(data[:, c-1]).T
        if groupcol:
            indata = numpy.hstack((numpy.ones((nsubjects,1)), indata))
        if covarcols:
            covars = data[:, [cv-1 for cv in covarcols]]
            indata = numpy.hstack((indata, covars))
        mat = FslMatFile(filesys=filesys)
        mat.setData(indata)
        matfname = 'matfiles/c{3}b{0:0>2d}s{1}d_{2}.mat'.format(c,
            nsubjects,measures[c-1], indata.shape[1])
        fnames.append(matfname)
        mat.saveAs(matfname)
        print(matfname)
    return fnames

