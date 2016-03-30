import sys, os, shutil
from glob import glob
from os.path import join as pathjoin
from collections import defaultdict
import dill #to use as pickle replacement of lambda dict
import numpy as np
import scipy.ndimage
import nibabel
import nibabel.nifti1 as nifti1
from nipype.interfaces import fsl
from pylabs.utils.paths import getlocaldataroot
from niprov import Context
from pylabs.utils._options import PylabsOptions
from decimal import *
getcontext().prec = 8
opts = PylabsOptions()
prov = Context()
fslbet = fsl.BET()
fslmaths = fsl.BinaryMaths()

targetdims = (182, 218, 200)
target_translation = (90, -93, -57)
megaffine = np.array([[-1, 0, 0, 90], [0, 1, 0, -93], [0, 0, 1, -57], [0, 0, 0, 1]])
identity_matrix = np.eye(4)
mni_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -126], [0, 0, 1, -72], [0, 0, 0, 1]])
psl2ras = np.array([[0., 0., -1., 0.], [-1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]])
templatedict = defaultdict(lambda: defaultdict(list))

a = [('ANTS12-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 14, 'ztrans': 0, 'xrot': -22, 'origdims': (141, 178, 144)}),
     ('ANTS6-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 41, 'ztrans': 26.5, 'xrot': -16, 'zroll': -20, 'xroll': 3, 'origdims': (147, 170, 176)}),
     ('ANTS15-0Months_head_bias_corrected.nii.gz', {'zcutoff': 19, 'ztrans': -4, 'xrot': -26, 'origdims': (150, 180, 155)}),
     ('K13714-0Months_301_WIP_QUIET_MPRAGE_ti1450_ras.nii.gz', {'zcutoff': 70, 'ztrans': 0, 'xrot': -12, 'zroll': 0, 'xroll': 0, 'origdims': (150, 256, 256)}),
      ]
for i in a:
    templatedict[i[0]] = i[1]

def printmessage(msg, indent=0):
    if verbose:
        print("%s%s" % (' ' * indent, msg))

def error(msg, exit_code):
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)
#defaults
verbose = True
prov.dryrun = True

fs = getlocaldataroot()
pathtotemplates = pathjoin(fs, 'tadpole/sphere_sources')
outputdir = pathjoin(fs, 'tadpole/atlases2')
templatefiles = set(glob(pathjoin(fs, pathtotemplates, '*_head_bias_corrected.nii.gz'))) - set(glob(pathjoin(fs, pathtotemplates, '*_t2w_*.nii.gz')))
templatefiles = list(templatefiles)
templatefiles += glob(pathjoin(fs, pathtotemplates, '*_ras.nii.gz'))
if outputdir and not os.path.exists(pathjoin(outputdir, 'tmp')):
    os.makedirs(pathjoin(outputdir, 'tmp'))

#tf = templatefiles[1]

for tf in templatefiles:
    tfname = tf.split('/')[-1]
    tf_age = tfname.split('_')[0][4:]
    tf_img = nibabel.load(tf)
    tf_hdr = tf_img.header
    tf_data = np.array(tf_img.dataobj)
    if all(x != 1.0 for x in tf_hdr.get_zooms()): #image not 1mm3 res. must adj
        tf_data = scipy.ndimage.zoom(tf_data, list(tf_hdr.get_zooms()), order=0)
        templatedict[tfname]['zcutoff'] = round(templatedict[tfname]['zcutoff'] * list(tf_hdr.get_zooms())[2])
    tf_data_zcrop = tf_data
    tf_data_zcrop[:,:,0:templatedict[tfname]['zcutoff']] = 0
    tf_data_rot = scipy.ndimage.interpolation.rotate(tf_data_zcrop, templatedict[tfname]['xrot'],  axes=(2, 1))
    shape_diff = [int(round((a - b)/2)) for a, b in zip(list(targetdims), list(tf_data_rot.shape))]
    if not any(x < 0 for x in shape_diff):
        #new xyz shape smaller than target
        xl = shape_diff[0]
        xu = targetdims[0] - shape_diff[0]-1
        yl = shape_diff[1]
        yu = targetdims[1] - shape_diff[1]
        zl = shape_diff[2]
        zu = targetdims[2] - shape_diff[2]
        mni_array = np.zeros(targetdims)
        mni_array[xl:xu, yl:yu, zl:zu] = tf_data_rot
    elif shape_diff[2] < 0 and abs(shape_diff[2]*2) <= templatedict[tfname]['zcutoff']:
        #new z shape bigger than target but small enough to lop off entirely
        xl = shape_diff[0]
        xu = targetdims[0] - shape_diff[0]-1
        yl = shape_diff[1]
        yu = targetdims[1] - shape_diff[1]
        mni_array = np.zeros(targetdims)
        temp = tf_data_rot[:,:,abs(shape_diff[2]*2):]
        mni_array[xl:xu, yl:yu,:] = temp
    elif shape_diff[2] < 0 and abs(shape_diff[2]*2) > templatedict[tfname]['zcutoff']:
        #new z shape bigger than target but too big to lop off entirely
        xl = shape_diff[0]
        xu = targetdims[0] - shape_diff[0]
        yl = shape_diff[1]
        yu = targetdims[1] - shape_diff[1]
        mni_array = np.zeros(targetdims)
        temp = tf_data_rot[:,:, templatedict[tfname]['zcutoff']:templatedict[tfname]['zcutoff']-abs(shape_diff[2]*2)+1]
        mni_array[xl:xu, yl:yu,:] = temp

    if templatedict[tfname]['xroll'] < 0:
        mni_array = np.roll(mni_array, targetdims[0] + templatedict[tfname]['xroll'], 0)
    elif templatedict[tfname]['xroll'] > 0:
        mni_array = np.roll(mni_array, templatedict[tfname]['xroll'], 0)

    if templatedict[tfname]['zroll'] < 0:
        mni_array = np.roll(mni_array, targetdims[2] + templatedict[tfname]['zroll'], 2)
    elif templatedict[tfname]['zroll'] > 0:
        mni_array = np.roll(mni_array, templatedict[tfname]['zroll'], 2)

    tf_img.set_qform(megaffine, code='scanner')
    tf_img.set_sform(megaffine, code='scanner')
    tf_hdr = tf_img.header
    nimg_tf = nifti1.Nifti1Image(mni_array, megaffine, tf_hdr)
    nibabel.save(nimg_tf, pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii'))

    fslbet.inputs.in_file = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii')
    fslbet.inputs.frac = 0.3
    fslbet.inputs.surfaces = True
    fslbet.inputs.out_file = pathjoin(outputdir, 'tmp', 'mnimegaxis_'+tf_age+'_brain.nii.gz')
    fslbet.run()
    skin_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_skin_surf.nii.gz')
    shutil.copy2(pathjoin(outputdir, 'tmp', 'mnimegaxis_'+tf_age+'_brain_outskin_mesh.nii.gz'), skin_fpath)
    skin_img = nifti1.load(skin_fpath)
    skin_affine = skin_img.affine
    skin_data = np.array(skin_img.dataobj)
    skin_data_com = scipy.ndimage.measurements.center_of_mass(skin_data)
    x0, y0, z0 = [d for d in skin_data_com]
    q = skin_img.get_qform()
    q[1,3] = -y0
    q[2,3] = -z0
    skin_img.set_qform(q, code='scanner')
    skin_img.set_sform(q, code='scanner')
    skin_hdr = skin_img.header
    skin_data_com = np.round(skin_data_com).astype(int)
    skin_xrow = skin_data[:,skin_data_com[1], skin_data_com[2]]
    for x, xval in enumerate(skin_xrow[skin_data_com[0]:]):
        if xval > 0:
            break
    r = x
    spheredata = np.zeros(skin_data.shape)
    for x in range(spheredata.shape[0]):
        for y in range(spheredata.shape[1]):
            for z in range(spheredata.shape[2]):
                dist = np.sqrt(np.sum(np.square(np.array([x,y,z])-skin_data_com)))
                if (dist > (r - 1)) and (dist < (r + 1)):
                        spheredata[x,y,z] = 1


    sphere_img = nibabel.Nifti1Image(spheredata, skin_affine, skin_hdr)
    sphere_hrd = sphere_img.header
    sphere_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_r'+ str(r) +'mm_sphere.nii.gz')
    nibabel.save(sphere_img, sphere_fpath)

