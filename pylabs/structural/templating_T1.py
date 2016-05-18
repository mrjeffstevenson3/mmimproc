import glob, os, pandas, numpy, niprov, nibabel, cPickle
from os.path import join
from pylabs.utils.paths import getnetworkdataroot
provenance = niprov.Context()

fs = getnetworkdataroot()
project = 'roots_of_empathy'
subjects = ['sub-2013-C028', 'sub-2013-C029', 'sub-2013-C030', 'sub-2013-C037', 'sub-2013-C053', 'sub-2013-C065']

with open(join(fs, project, 'all_5yo_subj_conversion_dict_may17_clouddumps.pickle'), 'rb') as f:
    niftiDict = cPickle.load(f)
