import os, numpy
from mmimproc.utils import Filesystem, PylabsOptions
from mmimproc.correlation.fslmatfile import FslMatFile
from mmimproc.utils.provenance import ProvenanceWrapper


def csv2fslmat(csvfile, selectSubjects=None, demean=True, groupcol=False,
    cols=None, covarcols=None, outdir=os.getcwd(), provenance=ProvenanceWrapper(), 
    filesys=Filesystem()):
    """Create FSL matrix files from behavioral data in a csv file

    Args:
        csvfile (str): Path to space separated behavioral data file 
        selectSubjects (list): List of subject indices to include (order of no
            consequence). Defaults to all subjects.
        demean (bool): Subtract mean from behavior data. Defaults to True. 
        groupcol (bool): Whether to prepend a column of 1s. Defaults to False.
        cols (list): Select columns to to create mat files for
        covarcols (list): Select columns to covary. All of these are included 
            in each matfile created.
        outdir (str): Directory in which to create matfiles. Defaults 
            to current directory.
        provenance (ProvenanceWrapper or niprov.ProvenanceContext): Provenance context
        filesys (getmmimprocpath.utils.Filesystem): Pass a mock here for testing purpose.

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

    demeanflag = ''
    if demean:
        means = data.mean(axis=0) #per-measure average
        data = (data-means) # demeaned data
        demeanflag = 'd'

    fnames = []
    filesys.makedirs(outdir)
    for c in cols:
        indata = numpy.atleast_2d(data[:, c-1]).T
        if groupcol:
            indata = numpy.hstack((numpy.ones((nsubjects,1)), indata))
        if covarcols:
            covars = data[:, [cv-1 for cv in covarcols]]
            indata = numpy.hstack((indata, covars))
        mat = FslMatFile(filesys=filesys)
        mat.setData(indata)
        matfname = os.path.join(outdir, 'c{0}b{1:0>2d}s{2}{3}_{4}.mat'.format(
            indata.shape[1], c, nsubjects, demeanflag, measures[c-1]))
        fnames.append(matfname)
        mat.saveAs(matfname)
        provenance.log(matfname, 'csv2fslmat', csvfile, script=__file__)
    return fnames

