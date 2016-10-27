import os, inspect
from pathlib import *
from os.path import join, basename, dirname, isfile, isdir, split
import numpy as np
import nibabel as nib
from nibabel.orientations import (io_orientation, inv_ornt_aff, apply_orientation)
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
        options[u'keyvaluepairs'] = {u'modality': u'DWMRI', u'DWMRI_b-value': np.max(bvals).astype(unicode)}
        for i, x in enumerate(bvecs.T):
            if u'DWMRI_gradient_'+unicode(i).zfill(4) in options[u'keyvaluepairs']:
                options[u'keyvaluepairs'][u'DWMRI_gradient_'+unicode(i).zfill(4)].update(' '.join(map(unicode, x)))
            else:
                options[u'keyvaluepairs'][u'DWMRI_gradient_' + unicode(i).zfill(4)] = ' '.join(map(unicode, x))
    img = nib.load(str(niftifile))
    hdr = img.header
    img_data = img.get_data()
    # Reorient data block to RAS+ if necessary
    ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(img.affine))
    if np.all(ornt == [[0, 1],
                       [1, 1],
                       [2, 1]]):  # already in LPS+
        t_aff = np.eye(4)
        affine = img.affine
    else:  # Not in RAS+. fix affine and apply correct orientation
        t_aff = inv_ornt_aff(ornt, img.shape)
        affine = np.dot(img.affine, t_aff)
        img_data = apply_orientation(img_data, ornt)
    options[u'dimension'] = unicode(len(img_data.shape) + 1)
    options[u'measurement frame'] = [['-1', '0', '0'], ['0', '1', '0'], ['0', '0', '1']]
    options[u'sizes'] = list(img_data.shape)
    options[u'kinds'] =  ['space', 'space', 'space', 'vector']
    options[u'space'] = 'right-anterior-superior'
    options[u'space directions'] = [list(x) for x in affine[:3,:3].astype(str)] + [u'none']
    options[ u'space origin'] = [x for x in affine[:3,3].astype(str)]
    options[u'thicknesses'] = ['nan', 'nan', affine[2,2].astype(str), 'nan']
    nrrd.write(nrrd_fname, img_data, options=options)
    return