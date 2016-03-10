from pylabs.conversion.phantom_conv import (phantom_midslice_par2mni, 
                                        phantom_B1_midslice_par2mni)
from pylabs.utils.files import sortedParGlob
import collections, itertools, os
from os.path import join


def convertSubjectParfiles(subj, subjectdir):
    """ Converts all compatible .PAR files in the source_parrec directory under
        the subject directory passed to this function.
    """

    niftiDict = collections.defaultdict(list)
    parfiles = sortedParGlob(join(subjectdir, 'source_parrec/*.PAR'))
    for parfile in parfiles:
        args = {}
        fname = os.path.basename(parfile)
        if 'SPGR' in parfile or 'IRTSE' in parfile:
            if 'SPGR' in parfile:
                method = 'orig_spgr'
            else:
                method = 'tseir'
            args['scaling'] = 'fp'
            args['method'] = method
            args['outdir'] = join(subjectdir, 'anat')
            par2mni = phantom_midslice_par2mni
        elif 'B1' in parfile:
            method = 'b1map'
            args['scaling'] = 'dv'
            args['outdir'] = join(subjectdir, 'fmap')
            par2mni = phantom_B1_midslice_par2mni
        else: 
            continue
        args['parfile'] = parfile
        args['datadict'] = niftiDict
        args['flipexception'] = ['']
        args['protoexception'] = ['']
        args['outfilename'] = subj+'_'+method

        msg = 'Converting PAR. Method: [{0}] filename: {0}'
        print(msg.format(method, fname))

        key, val = par2mni(**args)

        for k, v in zip(key, val):
            niftiDict[k].append(v)

    return niftiDict
