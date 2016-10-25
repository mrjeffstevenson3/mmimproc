import os, inspect
from pathlib import *
from os.path import join, basename, dirname, isfile, isdir, split
import numpy as np
import nibabel as nib
import nrrd
import niprov, pylabs
from pylabs.utils import run_subprocess, WorkingContext

def nii2nrrd(niftifile, nrrd_fname, bvalsf=None, bvecsf=None):
    options = {}
    if bvalsf != None: bvalsf = Path(bvalsf)
    if bvecsf !=None: bvecsf = Path(bvecsf)
    niftifile = Path(niftifile)
    if bvalsf != None and not bvalsf.is_file():
        raise IOError( str(bvalsf) + " bvals File Doesn't Exist. Please check.")

    if bvecsf !=None and not bvecsf.is_file():
        raise IOError( str(bvecsf) + " bvecs File Doesn't Exist. Please check.")

    if not niftifile.is_file():
        raise IOError( str(niftifile) + " nifti file File Doesn't Exist. Please check.")
    #load data
    if bvalsf != None: bvals = np.loadtxt(str(bvalsf))
    if bvecsf !=None: bvecs = np.loadtxt(str(bvecsf))
    if bvecsf !=None and bvalsf != None:
        options.update({u'keyvaluepairs': {u'modality': u'DWMRI', u'DWMRI_b-value': np.max(bvals).astype(unicode)}})
        for i, x in enumerate(bvecs.T):
            if i < 10:
                for k, v in options.iteritems():
                    if u'DWMRI_gradient_000'+unicode(i) in options['keyvaluepairs']:
                        options[u'keyvaluepairs'][u'DWMRI_gradient_000'+unicode(i)].update(' '.join(map(unicode, x)))
                    else:

            else:
                options.update({u'keyvaluepairs': {u'DWMRI_gradient_00' + unicode(i): ' '.join(map(unicode, x))}})
    img = nib.load(str(niftifile))
    hdr = img.header
    img_data = img.get_data()
    nrrd.write(nrrd_fname, img_data, **options)
    return