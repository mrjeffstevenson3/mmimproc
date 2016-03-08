import sys, os, shutil
from glob import glob
from os.path import join as pathjoin
import numpy as np
import scipy.ndimage
import nibabel
import nibabel.nifti1 as nifti1
from nipype.interfaces import fsl
from pylabs.utils.paths import getlocaldataroot
from niprov import Context
from pylabs.utils._options import PylabsOptions
opts = PylabsOptions()
prov = Context()
fslbet = fsl.BET()

identity_matrix = np.eye(4)
mni_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -126], [0, 0, 1, -72], [0, 0, 0, 1]])
psl2ras = np.array([[0., 0., -1., 0.], [-1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]])


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
pathtotemplates = pathjoin(fs, 'tadpole/johnrichards/Preschool/Head')
outputdir = pathjoin(fs, 'tadpole/atlases')
templatefiles = set(glob(pathjoin(fs, pathtotemplates, '*_head.nii.gz'))) - set(glob(pathjoin(fs, pathtotemplates, '*_t2w_*')))
templatefiles = list(templatefiles)
if outputdir and not os.path.exists(pathjoin(outputdir, 'tmp')):
    os.makedirs(pathjoin(outputdir, 'tmp'))

for tf in templatefiles:
    tf_age = tf.split('/')[-1].split('_')[-2][4:]
    fslbet.inputs.in_file = tf
    fslbet.inputs.frac = 0.3
    fslbet.inputs.surfaces = True
    fslbet.inputs.out_file = pathjoin(outputdir, 'tmp', tf_age+'_brain.nii.gz')
    fslbet.run()
    shutil.copy2(pathjoin(outputdir, 'tmp', tf_age+'_brain_outskin_mesh.nii.gz'), pathjoin(outputdir, tf_age+'_skin_surf.nii.gz'))
    skin_img = nifti1.load(pathjoin(outputdir, tf_age+'_skin_surf.nii.gz'))
    skin_hdr = skin_img.header
    skin_affine = skin_img.affine
    skin_data = np.array(skin_img.dataobj)
    skin_data_com = scipy.ndimage.measurements.center_of_mass(skin_data)
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

    sphere_img = nibabel.Nifti1Image(spheredata, skin_affine)
    nibabel.save(sphere_img,pathjoin(outputdir, tf_age+'_d'+ str(2 * r) +'mm_sphere.nii.gz'))




