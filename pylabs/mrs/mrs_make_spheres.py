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
import mne
from mne.bem import _fit_sphere
from six import string_types
import nibabel
import nibabel.nifti1 as nifti1
from nipype.interfaces import fsl
from pylabs.utils.paths import getlocaldataroot
import niprov
from niprov import Context as ProvenanceContext
from pylabs.utils._options import PylabsOptions
from decimal import *
getcontext().prec = 8
opts = PylabsOptions()
prov = ProvenanceContext()
prov.dryrun = False
prov.verbosity = 'info'
verbose = True
fslbet = fsl.BET()

#reference image dims and origin all others will be centered on
ref_img = 'xxxxMNI152adult_T1_1mm_head.nii.gz'
#vox dims or shape of ref_img
ref_targetdims = (182, 218, 200)
#distance to meg origin from com for ref_img
ref_meg_origin2com = (0, -19, -47)
#double target dims
paddims = tuple([x * 2 for x in ref_targetdims])
#resulting meg origin of ref_img after rot and crop
megaxis_vox_origin_mni = (90, 90, 52)
#center of mass of ref_img in ref_targetdims after rot and crop
megaxis_vox_mni_com = (91, 108, 100)
mni_crop_range = [(x/2, x + x/2) for x in ref_targetdims]
#target_translation = (90, -90, -52)
meg_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -90], [0, 0, 1, -52], [0, 0, 0, 1]])
meg_affinex2 = meg_affine
meg_affinex2[:3,3] = [x * 2 for x in meg_affine[:3,3]]
identity_matrix = np.eye(4)
mni_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -126], [0, 0, 1, -72], [0, 0, 0, 1]])
psl2ras = np.array([[0., 0., -1., 0.], [-1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]])
imgdict = defaultdict(lambda: defaultdict(list))

a = [(ref_img, {'zcutoff': 8, 'ztrans': 0, 'meg_vox_origin': (90, 104, 30), 'xrot': -18, 'origdims': (182, 218, 182)}),
     ('ANTS6-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 48, 'meg_vox_origin': (71, 80, 60), 'xrot': -16, 'origdims': (147, 170, 176)}),
     ('ANTS12-0Months3T_head_bias_corrected.nii.gz', {'zcutoff': 50, 'meg_vox_origin': (74, 93, 68), 'xrot': -22, 'origdims': (149, 178, 190)}),
     ('K13714-0Months_301_WIP_QUIET_MPRAGE_ti1450_head.nii.gz', {'zcutoff': 70, 'meg_vox_origin': (73, 93, 66), 'xrot': -22, 'origdims': (150, 256, 256)}),
     ('ANTS15-0Months_head_bias_corrected.nii.gz', {'zcutoff': 20, 'meg_vox_origin': (80, 90, 41), 'xrot': -22, 'origdims': (150, 180, 155)}),
     ('ANTS18-0Months_head_bias_corrected.nii.gz', {'zcutoff': 19, 'meg_vox_origin': (80, 92, 40), 'xrot': -26, 'origdims': (150, 256, 256)}),
     ('ANTS2-0Years_head_bias_corrected.nii.gz', {'zcutoff': 13, 'meg_vox_origin': (72, 88, 32), 'xrot': -24, 'origdims': (150, 256, 256)}),
     ('ANTS2-5Years_head_bias_corrected.nii.gz', {'zcutoff': 19, 'meg_vox_origin': (75, 87, 38), 'xrot': -18, 'origdims': (150, 256, 256)}),
     ('ANTS3-0Years_head_bias_corrected.nii.gz', {'zcutoff': 22, 'meg_vox_origin': (80, 95, 44), 'xrot': -22, 'origdims': (150, 256, 256)}),
     ('ANTS4-0Years_head_bias_corrected.nii.gz', {'zcutoff': 18, 'meg_vox_origin': (75, 83, 37), 'xrot': -14, 'origdims': (150, 256, 256)}),
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

def substring_i(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

#defaults
verbose = True
prov.dryrun = False

fs = getlocaldataroot()
pathtotemplates = pathjoin(fs, 'tadpole/sphere_sources')
outputdir = pathjoin(fs, 'tadpole/meg_sphere_templates')
templatefiles = set(glob(pathjoin(fs, pathtotemplates, '*_head*.nii.gz'))) - set(glob(pathjoin(fs, pathtotemplates, '*_t2w_*.nii.gz')))
templatefiles = list(templatefiles)
if outputdir and not os.path.exists(pathjoin(outputdir, 'tmp')):
    os.makedirs(pathjoin(outputdir, 'tmp'))
[niprov.add(img) for img in templatefiles]

#tf = templatefiles[2]
#tf = templatefiles[substring_i(templatefiles, ref_img)]

for tf in templatefiles:
    tfname = tf.split('/')[-1]
    tf_age = tfname.split('_')[0][4:]
    tf_img = nibabel.load(tf)
    tf_hdr = tf_img.header
    tf_data = np.array(tf_img.dataobj)
    tf_data_com = com(tf_data)
    #if image not 1mm3 res. must adj zoom
    if all(x != 1.0 for x in tf_hdr.get_zooms()):
        tf_data = scipy.ndimage.zoom(tf_data, list(tf_hdr.get_zooms()), order=0)
        imgdict[tfname]['zcutoff'] = int(round(imgdict[tfname]['zcutoff'] * list(tf_hdr.get_zooms())[2]))
    tf_data_zcrop = tf_data
    tf_data_zcrop[:,:,0:imgdict[tfname]['zcutoff']] = 0
    tf_data_zcrop_com = com(tf_data_zcrop)
    padX, padY, padZ = [int(x-y) for x, y in zip(ref_targetdims, imgdict[tfname]['meg_vox_origin'])]
    tf_data_zcropP = np.zeros(paddims)
    tf_data_zcropP[padX:padX+tf_data_zcrop.shape[0], padY:padY+tf_data_zcrop.shape[1],padZ:padZ+tf_data_zcrop.shape[2]] = tf_data_zcrop
    tf_data_rot = rot(tf_data_zcropP, imgdict[tfname]['xrot'],  axes=(2, 1), reshape=False)
    tf_data_rot_com = np.round(com(tf_data_rot)).astype(int)
    meg_origin2com = [x - y for x, y in zip(ref_targetdims, tf_data_rot_com)]
    img_origin_offset_fm_com = [x/2. + y for x, y in zip(ref_targetdims, meg_origin2com)]
    roll_offset = [int(round(x-y)) for x, y in zip(img_origin_offset_fm_com, megaxis_vox_origin_mni)]
    lx = tf_data_rot_com[0] - int(round(ref_targetdims[0]/2.))
    ux = lx + ref_targetdims[0]
    ly = tf_data_rot_com[1] - int(round(ref_targetdims[1]/2.))
    uy = ly + ref_targetdims[1]
    lz = tf_data_rot_com[2] - int(round(ref_targetdims[2]/2.))
    uz = lz + ref_targetdims[2]
    mni_array = tf_data_rot[lx:ux,ly:uy,lz:uz]
    if any(v != 0 for v in roll_offset):
        for i, offset in enumerate(roll_offset):
            if offset > 0:
                mni_array = np.roll(mni_array, ref_targetdims[i] - offset, i)
            elif offset < 0:
                mni_array = np.roll(mni_array, offset, i)
    mni_array_com = np.round(com(mni_array)).astype(int)
    com2meg_vox_origin_offset = [int(round(x/2. - y)) for x, y in zip(tf_data_rot_com, mni_array_com)]
    tf_hdr = tf_img.header
    meg_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -90], [0, 0, 1, -52], [0, 0, 0, 1]])
    tf_img.set_qform(meg_affine, code='scanner')
    tf_img.set_sform(meg_affine, code='scanner')
    tf_hdr = tf_img.header
    nimg_tf = nifti1.Nifti1Image(mni_array, meg_affine, tf_hdr)
    nibabel.save(nimg_tf, pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii'))
    prov.log(pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii'), 'rotate2meg origin+set shape to MNI', tf, script=__file__)
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


    sphere_img = nibabel.Nifti1Image(spheredata, q, skin_hdr)
    sphere_hrd = sphere_img.header
    sphere_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_r'+ str(r) +'mm_sphere.nii.gz')
    nibabel.save(sphere_img, sphere_fpath)
    prov.log(sphere_fpath, 'meg sphere of radius '+str(r)+'mm and center of mass origin derived fm fsl bet skin surface of parent with resultant meg origin coord and MNI shape.',
                        pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii'), script=__file__)
    skin_dome = skin_data
    skin_dome[:,:,0:skin_data_com[2]] = 0
    skin_dome_img = nibabel.Nifti1Image(skin_dome, meg_affine, skin_hdr)
    skin_dome_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_r'+ str(r) +'mm_skin_dome.nii.gz')
    nibabel.save(skin_dome_img, skin_dome_fpath)

    dome_coord = np.array(np.nonzero(skin_dome))
    for i, offset in enumerate(megaxis_vox_origin_mni):
        dome_coord[i,:] = dome_coord[i,:] - offset

    dome_radius, dome_origin = _fit_sphere(dome_coord.T, disp=False)
    dome_sphere_orig = [x + y for x, y in zip(dome_origin, megaxis_vox_origin_mni)]
    domespheredata = np.zeros(skin_data.shape)
    for x in range(domespheredata.shape[0]):
        for y in range(domespheredata.shape[1]):
            for z in range(domespheredata.shape[2]):
                dist = np.sqrt(np.sum(np.square(np.array([x,y,z])-dome_sphere_orig)))
                if (dist > (dome_radius - 1)) and (dist < (dome_radius + 1)):
                        domespheredata[x,y,z] = 1
    domespheredata_com = np.round(com(domespheredata), decimals=2)
    domesphere_affine = np.array([[-1, 0, 0, domespheredata_com[0]], [0, 1, 0, -domespheredata_com[1]], [0, 0, 1, -domespheredata_com[2]], [0, 0, 0, 1]])
    skin_img.set_qform(domesphere_affine, code='scanner')
    skin_img.set_sform(domesphere_affine, code='scanner')
    skin_hdr = skin_img.header

    domesphere_img = nibabel.Nifti1Image(domespheredata, domesphere_affine, skin_hdr)
    domesphere_fpath = pathjoin(outputdir, 'mnimegaxis_'+tf_age+'_r'+ str(int(round(dome_radius))) +'mm_dome_sphere.nii.gz')
    nibabel.save(domesphere_img, domesphere_fpath)
    prov.log(domesphere_fpath, 'analogue to meg polhemus cloud sphere using mne _fit_sphere of radius '+str(dome_radius)+'mm and origin '+str(dome_sphere_orig)+' derived fm upper dome of skin surface of parent in MNI space',
                        pathjoin(outputdir, 'mnimegaxis_'+tf_age+'.nii'), script=__file__)
