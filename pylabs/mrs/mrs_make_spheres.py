import sys, os, shutil
import tempfile
from glob import glob
from os.path import join as pathjoin
from collections import defaultdict
import dill #to use as pickle replacement of lambda dict
import numpy as np
import scipy.ndimage
from scipy.ndimage.interpolation import shift
from scipy.ndimage.interpolation import rotate as rot
from scipy.ndimage.measurements import center_of_mass as com
import nibabel
import nibabel.nifti1 as nifti1
from nipype.interfaces import fsl
from pylabs.utils.paths import getlocaldataroot
import niprov
from niprov import Context
from pylabs.utils._options import PylabsOptions
from decimal import *
getcontext().prec = 8
opts = PylabsOptions()
prov = Context()
prov.dryrun = False
prov.verbosity = 'info'
verbose = True
fslbet = fsl.BET()

targetdims = (182, 218, 200)
paddims = tuple([x * 2 for x in targetdims])
target_translation = (90, -93, -57)
meg_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -102], [0, 0, 1, -30], [0, 0, 0, 1]])
meg_affinex2 = np.array([[-1, 0, 0, 180], [0, 1, 0, -204], [0, 0, 1, -60], [0, 0, 0, 1]])
identity_matrix = np.eye(4)
mni_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -126], [0, 0, 1, -72], [0, 0, 0, 1]])
psl2ras = np.array([[0., 0., -1., 0.], [-1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]])
imgdict = defaultdict(lambda: defaultdict(list))

a = [('xxxxMNI152adult_T1_1mm_head.nii.gz', {'zcutoff': 8, 'ztrans': 0, 'meg_origin': (90, -102, -30), 'xrot': -18, 'zroll': 0, 'xroll': 0, 'origdims': (182, 218, 182)}),
     ('ANTS12-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 14, 'ztrans': 0, 'xrot': -22, 'origdims': (141, 178, 144)}),
     ('ANTS6-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 41, 'ztrans': 26.5, 'xrot': -16, 'zroll': -20, 'xroll': 3, 'origdims': (147, 170, 176)}),
     ('ANTS15-0Months_head_bias_corrected.nii.gz', {'zcutoff': 19, 'ztrans': -4, 'xrot': -26, 'origdims': (150, 180, 155)}),
     ('K13714-0Months_301_WIP_QUIET_MPRAGE_ti1450_ras.nii.gz', {'zcutoff': 70, 'ztrans': 0, 'xrot': -12, 'zroll': 0, 'xroll': 0, 'origdims': (150, 256, 256)}),
     ('ANTS18-0Months_head_bias_corrected.nii.gz', {'zcutoff': 17, 'ztrans': 0, 'xrot': -30, 'zroll': 0, 'xroll': 0, 'origdims': (150, 256, 256)}),
     ('ANTS2-5Years_head_bias_corrected.nii.gz', {'zcutoff': 70, 'ztrans': 0, 'xrot': -12, 'zroll': 0, 'xroll': 0, 'origdims': (150, 256, 256)}),
     ('ANTS3-0Years_head_bias_corrected.nii.gz', {'zcutoff': 70, 'ztrans': 0, 'xrot': -12, 'zroll': 0, 'xroll': 0, 'origdims': (150, 256, 256)}),
     ('ANTS4-0Years_head_bias_corrected.nii.gz', {'zcutoff': 70, 'ztrans': 0, 'xrot': -12, 'zroll': 0, 'xroll': 0, 'origdims': (150, 256, 256)}),
      ]
for i in a:
    imgdict[i[0]] = i[1]

def printmessage(msg, indent=0):
    if verbose:
        print("%s%s" % (' ' * indent, msg))

def error(msg, exit_code):
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)

def set_affine_offsets(affine, newoffsets):
    for i, a in enumerate(newoffsets):
        affine[i,3] = a
    return affine

#defaults
verbose = True
prov.dryrun = True

fs = getlocaldataroot()
pathtotemplates = pathjoin(fs, 'tadpole/sphere_sources')
outputdir = pathjoin(fs, 'tadpole/atlases2')
templatefiles = set(glob(pathjoin(fs, pathtotemplates, '*_head*.nii.gz'))) - set(glob(pathjoin(fs, pathtotemplates, '*_t2w_*.nii.gz')))
templatefiles = list(templatefiles)
if outputdir and not os.path.exists(pathjoin(outputdir, 'tmp3')):
    os.makedirs(pathjoin(outputdir, 'tmp3'))
[niprov.add(img) for img in templatefiles]

tf = templatefiles[1]

for tf in templatefiles:
    tfname = tf.split('/')[-1]
    tf_age = tfname.split('_')[0][4:]
    tf_img = nibabel.load(tf)
    tf_hdr = tf_img.header
    tf_data = np.array(tf_img.dataobj)
    #if image not 1mm3 res. must adj zoom
    if all(x != 1.0 for x in tf_hdr.get_zooms()):
        tf_data = scipy.ndimage.zoom(tf_data, list(tf_hdr.get_zooms()), order=0)
        imgdict[tfname]['zcutoff'] = int(round(imgdict[tfname]['zcutoff'] * list(tf_hdr.get_zooms())[2]))
    tf_data_zcrop = tf_data
    tf_data_zcrop[:,:,0:imgdict[tfname]['zcutoff']] = 0
    tf_data_zcrop_com = com(tf_data_zcrop)
    padX = [tf_data_zcrop.shape[0] - abs(imgdict[tfname]['meg_origin'][0]), abs(imgdict[tfname]['meg_origin'][0])]
    padY = [tf_data_zcrop.shape[1] - abs(imgdict[tfname]['meg_origin'][1]), abs(imgdict[tfname]['meg_origin'][1])]
    padZ = [tf_data_zcrop.shape[2] - abs(imgdict[tfname]['meg_origin'][2]), abs(imgdict[tfname]['meg_origin'][2])]
    tf_data_zcropP = np.pad(tf_data_zcrop, [padX, padY, padZ], 'constant')
    tf_data_zcropP_hdr = tf_hdr
    tf_data_zcropP_hdr.set_qform(meg_affinex2, code='scanner')
    tf_data_zcropP_hdr.set_sform(meg_affinex2, code='scanner')
    nimg_tf_data_zcropP = nifti1.Nifti1Image(tf_data_zcropP, meg_affinex2, tf_data_zcropP_hdr)
    nibabel.save(nimg_tf_data_zcropP, pathjoin(outputdir, 'preangle_'+tf_age+'.nii'))
    tf_data_rot = rot(tf_data_zcropP, imgdict[tfname]['xrot'],  axes=(2, 1), reshape=False)
    tf_data_rot_com = np.round(com(tf_data_rot)).astype(int)
    lx = tf_data_rot_com[0] - int(round(targetdims[0]/2.))
    ux = lx + targetdims[0]
    ly = tf_data_rot_com[1] - int(round(targetdims[1]/2.))
    uy = ly + targetdims[1]
    lz = tf_data_rot_com[2] - int(round(targetdims[2]/2.))
    uz = lz + targetdims[2]
    mni_array = tf_data_rot[lx:ux,ly:uy,lz:uz]
    #offset_due2rot = [int(round(x/2. - y)) for x, y in zip(tf_data_rot_com, tf_data_zcrop_com)]
    #rolldata = shift(tf_data_rot, [x*-2 for x in offset_due2rot], order=0)
    #shape_diff = [int(round((a - b)/2)) for a, b in zip(list(targetdims), list(tf_data_rot.shape))]

    # if not any(x < 0 for x in shape_diff):
    #     #new xyz shape smaller than target
    #     xl = shape_diff[0]
    #     xu = targetdims[0] - shape_diff[0]-1
    #     yl = shape_diff[1]
    #     yu = targetdims[1] - shape_diff[1]
    #     zl = shape_diff[2]
    #     zu = targetdims[2] - shape_diff[2]
    #     mni_array = np.zeros(targetdims)
    #     mni_array[xl:xu, yl:yu, zl:zu] = tf_data_rot
    # elif shape_diff[1] < 0 and shape_diff[2] < 0 and abs(shape_diff[2]*2) <= imgdict[tfname]['zcutoff']:
    #     #new y and z shape bigger than target but small enough to lop off entirely
    #     xl = shape_diff[0]
    #     xu = targetdims[0] - shape_diff[0]-1
    #     mni_array = np.zeros(targetdims)
    #     temp = tf_data_rot[:,abs(shape_diff[1]):,abs(shape_diff[2]*2):]
    #     mni_array[xl:xu,:,:] = temp
    # elif shape_diff[1] < 0 and shape_diff[2] < 0 and abs(shape_diff[2]*2) > imgdict[tfname]['zcutoff']:
    #     #new y and z shape bigger than target and z too big to lop off entirely
    #     xl = shape_diff[0]
    #     xu = targetdims[0] - shape_diff[0]
    #     mni_array = np.zeros(targetdims)
    #     temp = tf_data_rot[:,abs(shape_diff[1]):targetdims[1] - shape_diff[1], imgdict[tfname]['zcutoff']:imgdict[tfname]['zcutoff']-abs(shape_diff[2]*2)+1]
    #     mni_array[xl:xu,:,:] = temp
    # elif shape_diff[2] < 0 and abs(shape_diff[2]*2) <= imgdict[tfname]['zcutoff']:
    #     #new z shape bigger than target but small enough to lop off entirely
    #     xl = shape_diff[0]
    #     xu = targetdims[0] - shape_diff[0]-1
    #     yl = shape_diff[1]
    #     yu = targetdims[1] - shape_diff[1]
    #     mni_array = np.zeros(targetdims)
    #     temp = tf_data_rot[:,:,abs(shape_diff[2]*2):]
    #     mni_array[xl:xu, yl:yu,:] = temp
    # elif shape_diff[2] < 0 and abs(shape_diff[2]*2) > imgdict[tfname]['zcutoff']:
    #     #new z shape bigger than target but too big to lop off entirely
    #     xl = shape_diff[0]
    #     xu = targetdims[0] - shape_diff[0]
    #     yl = shape_diff[1]
    #     yu = targetdims[1] - shape_diff[1]
    #     mni_array = np.zeros(targetdims)
    #     temp = tf_data_rot[:,:, imgdict[tfname]['zcutoff']:imgdict[tfname]['zcutoff']-abs(shape_diff[2]*2)+1]
    #     mni_array[xl:xu, yl:yu,:] = temp

    if imgdict[tfname]['xroll'] < 0:
        mni_array = np.roll(mni_array, targetdims[0] + imgdict[tfname]['xroll'], 0)
    elif imgdict[tfname]['xroll'] > 0:
        mni_array = np.roll(mni_array, imgdict[tfname]['xroll'], 0)

    if imgdict[tfname]['zroll'] < 0:
        mni_array = np.roll(mni_array, targetdims[2] + imgdict[tfname]['zroll'], 2)
    elif imgdict[tfname]['zroll'] > 0:
        mni_array = np.roll(mni_array, imgdict[tfname]['zroll'], 2)

    tf_img.set_qform(meg_affine, code='scanner')
    tf_img.set_sform(meg_affine, code='scanner')
    tf_hdr = tf_img.header
    nimg_tf = nifti1.Nifti1Image(mni_array, meg_affine, tf_hdr)
    nibabel.save(nimg_tf, pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii'))

    fslbet.inputs.in_file = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii')
    fslbet.inputs.frac = 0.3
    fslbet.inputs.surfaces = True
    fslbet.inputs.out_file = pathjoin(outputdir, 'tmp3', 'mnimegaxis_'+tf_age+'_brain.nii.gz')
    fslbet.run()
    skin_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_skin_surf.nii.gz')
    shutil.copy2(pathjoin(outputdir, 'tmp3', 'mnimegaxis_'+tf_age+'_brain_outskin_mesh.nii.gz'), skin_fpath)
    skin_img = nifti1.load(skin_fpath)
    skin_affine = skin_img.affine
    skin_data = np.array(skin_img.dataobj)
    skin_data_com = com(skin_data)
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
    skin_dome = skin_data
    skin_dome[:,:,0:skin_data_com[2]] = 0
    skin_dome_img = nibabel.Nifti1Image(skin_dome, skin_affine, skin_hdr)
    skin_dome_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_r'+ str(r) +'mm_skin_dome.nii.gz')
    nibabel.save(skin_dome_img, skin_dome_fpath)

