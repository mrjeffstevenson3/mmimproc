from pathlib import *
import numpy as np
import nibabel as nib
from nibabel.orientations import (io_orientation, inv_ornt_aff, apply_orientation)
import nrrd
from pylabs.utils import *
provenance = ProvenanceWrapper()

# need to fix multishell gradient handling. grads are proportional to sqrt(bval/bval_largest)
# 1st find largest b value, write those vectors unchanged, smaller b value vecs are uniformly scaled as above and written per usual.
# see web page :  https://na-mic.org/wiki/NAMIC_Wiki:DTI:Nrrd_format#Key.2FValue_pair_convention_for_DWI
def nii2nrrd(niftifile, nrrd_fname, bvalsf=None, bvecsf=None, istensor=False, ismask=False):
    '''
    This function converts nifti files to nrrd.
    '''
    # test consistency
    if Path(nrrd_fname).suffix is not 'nhdr':
        print('nrrd files no longer compatible with Slicer. switching to .nhdr extension.')
        nrrd_fname = replacesuffix(nrrd_fname, '.nhdr')
    if istensor + ismask > 1:
        raise ValueError("Only one can be True. istensor= "+istensor+", ismask= "+ismask)

    if (bvalsf is not None and bvecsf is None) or (bvalsf is None and bvecsf is not None):
        raise ValueError("Either both bvals and bvecs files must be defined or None. bvalsf= " + bvalsf + ", bvecsf= " + bvecsf)

    if bvalsf is not None and not Path(bvalsf).is_file():
        raise IOError( str(bvalsf) + " bvals File Doesn't Exist. Please check.")

    if bvecsf is not None and not Path(bvecsf).is_file():
        raise IOError( str(bvecsf) + " bvecs File Doesn't Exist. Please check.")

    if not Path(niftifile).is_file():
        raise IOError( str(niftifile) + " nifti file File Doesn't Exist. Please check.")
    #load data
    options = {}
    if bvalsf is not None: bvals = np.loadtxt(str(bvalsf))
    if bvecsf is not None: bvecs = np.loadtxt(str(bvecsf))
    if bvecsf is not None and bvalsf is not None:
        options[u'keyvaluepairs'] = {u'modality': u'DWMRI', u'DWMRI_b-value': np.max(bvals).astype(unicode)}
        if len(np.unique(np.loadtxt(str(bvalsf)))) == 2:
            for i, x in enumerate(bvecs.T):
                if u'DWMRI_gradient_'+unicode(i).zfill(4) in options[u'keyvaluepairs']:
                    options[u'keyvaluepairs'][u'DWMRI_gradient_'+unicode(i).zfill(4)].update(' '.join(map(unicode, x)))
                else:
                    options[u'keyvaluepairs'][u'DWMRI_gradient_' + unicode(i).zfill(4)] = ' '.join(map(unicode, x))
        elif len(np.unique(bvals)) == 3:
            ubvals = np.unique(bvals)[::-1]
            ubvals = np.delete(ubvals, -1)
            vec_scaling = ubvals[1]/ubvals[0]                          # wrong for norm vecs: np.sqrt(ubvals[1]/ubvals[0])
            for i, (x, b) in enumerate(zip(bvecs.T, bvals)):
                if b == np.max(bvals):
                    if u'DWMRI_gradient_'+unicode(i).zfill(4) in options[u'keyvaluepairs']:
                        options[u'keyvaluepairs'][u'DWMRI_gradient_'+unicode(i).zfill(4)].update(' '.join(map(unicode, x)))
                    else:
                        options[u'keyvaluepairs'][u'DWMRI_gradient_' + unicode(i).zfill(4)] = ' '.join(map(unicode, x))
                if b < np.max(bvals):
                    if u'DWMRI_gradient_'+unicode(i).zfill(4) in options[u'keyvaluepairs']:
                        options[u'keyvaluepairs'][u'DWMRI_gradient_'+unicode(i).zfill(4)].update(' '.join(map(unicode, x*vec_scaling)))
                    else:
                        options[u'keyvaluepairs'][u'DWMRI_gradient_' + unicode(i).zfill(4)] = ' '.join(map(unicode, x*vec_scaling))
        elif len(np.unique(bvals)) > 3:
            raise ValueError("Only 3 shell dwi can be properly converted with scaled vectors at this time.")
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
    if ismask:
        img_data = np.int16(img_data)
    else:
        img_data = np.float32(img_data)
    options[u'dimension'] = unicode(len(img_data.shape))
    options[u'measurement frame'] = [['-1', '0', '0'], ['0', '1', '0'], ['0', '0', '1']]
    options[u'sizes'] = list(img_data.shape)
    options[u'type'] = unicode(img_data.dtype.str[1:])
    if istensor:
        options[u'kinds'] = [u'space', u'space', u'space', u'3D-symmetric-matrix']
    elif len(img_data.shape) == 4:
        options[u'kinds'] =  [u'space', u'space', u'space', u'list']
    else:
        options[u'kinds'] =  [u'space', u'space', u'space']
    options[u'space'] = u'right-anterior-superior'
    if len(img_data.shape) == 4:
        options[u'space directions'] = [list(x) for x in affine[:3,:3].astype(str)] + [u'none']
        options[u'thicknesses'] = ['NaN', 'NaN', str(hdr['pixdim'][3]), 'NaN']
    else:
        options[u'space directions'] = [list(x) for x in affine[:3,:3].astype(str)]
        options[u'thicknesses'] = ['NaN', 'NaN', str(hdr['pixdim'][3])]
    options[ u'space origin'] = [x for x in affine[:3,3].astype(str)]

    nrrd.write(str(nrrd_fname), img_data, options=options)
    with open(str(nrrd_fname), 'r') as orig_nhdr:
        bad_nhdr = orig_nhdr.read()
    good_nhdr = ''
    for line in bad_nhdr.splitlines():
        if '(n,o,n,e)' in line:
            good_nhdr += line.replace('(n,o,n,e)', 'none') + '\n'
        elif 'data file:' in line:
            good_nhdr += 'data file: ' + Path(line.replace('data file:', '')).name + '\n'
        else:
            good_nhdr += line + '\n'
    with open(str(nrrd_fname), 'w') as fixed_nhdr:
        fixed_nhdr.write(good_nhdr)
    provenance.log(str(nrrd_fname), 'convert nii to nrrd using pynrrd', str(niftifile), script=__file__, provenance=options)
    return nrrd_fname

def array2nrrd(data, affine, nrrd_fname, bvalsf=None, bvecsf=None, istensor=False, ismask=False):
    if istensor + ismask > 1:
        raise ValueError("Only one can be True. istensor= "+istensor+", ismask= "+ismask)
    options = {}
    if bvalsf is not None: bvalsf = Path(bvalsf)
    if bvecsf is not None: bvecsf = Path(bvecsf)
    if bvalsf is not None and not bvalsf.is_file():
        raise IOError( str(bvalsf) + " bvals File Doesn't Exist. Please check.")

    if bvecsf is not None and not bvecsf.is_file():
        raise IOError( str(bvecsf) + " bvecs File Doesn't Exist. Please check.")

    #load data
    if bvalsf is not None: bvals = np.loadtxt(str(bvalsf))
    if bvecsf is not None: bvecs = np.loadtxt(str(bvecsf))
    if bvecsf is not None and bvalsf is not None:
        options[u'keyvaluepairs'] = {u'modality': u'DWMRI', u'DWMRI_b-value': np.max(bvals).astype(unicode)}
        for i, x in enumerate(bvecs.T):
            if u'DWMRI_gradient_'+unicode(i).zfill(4) in options[u'keyvaluepairs']:
                options[u'keyvaluepairs'][u'DWMRI_gradient_'+unicode(i).zfill(4)].update(' '.join(map(unicode, x)))
            else:
                options[u'keyvaluepairs'][u'DWMRI_gradient_' + unicode(i).zfill(4)] = ' '.join(map(unicode, x))
    # Reorient data block to RAS+ if necessary
    ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(affine))
    if np.all(ornt == [[0, 1],
                       [1, 1],
                       [2, 1]]):  # already in LPS+
        t_aff = np.eye(4)
    else:  # Not in RAS+. fix affine and apply correct orientation
        t_aff = inv_ornt_aff(ornt, data.shape)
        affine = np.dot(affine, t_aff)
        data = apply_orientation(data, ornt)

    if ismask:
        data = np.int16(data)
    else:
        data = np.float32(data)
    options[u'dimension'] = unicode(len(data.shape))
    options[u'measurement frame'] = [['-1', '0', '0'], ['0', '1', '0'], ['0', '0', '1']]
    options[u'sizes'] = list(data.shape)
    options[u'type'] = unicode(data.dtype.str[1:])
    if istensor:
        options[u'kinds'] = [u'space', u'space', u'space', u'3D-symmetric-matrix']
    elif len(data.shape) == 4:
        options[u'kinds'] =  [u'space', u'space', u'space', u'vector']
    else:
        options[u'kinds'] =  [u'space', u'space', u'space']
    options[u'space'] = u'right-anterior-superior'
    if len(data.shape) == 4:
        options[u'space directions'] = [list(x) for x in affine[:3,:3].astype(str)] + [u'none']
        options[u'thicknesses'] = ['nan', 'nan', affine[2, 2].astype(str), 'nan']
    else:
        options[u'space directions'] = [list(x) for x in affine[:3,:3].astype(str)]
        options[u'thicknesses'] = ['nan', 'nan', affine[2, 2].astype(str)]
    options[ u'space origin'] = [x for x in affine[:3,3].astype(str)]
    nrrd.write(str(nrrd_fname), data, options=options)
#    provenance.log(str(nrrd_fname), 'convert nii to nrrd using pynrrd', str(niftifile), script=__file__, provenance=options)
    return
