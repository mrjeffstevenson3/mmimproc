from pathlib import *
import nibabel
import numpy as np
from scipy.ndimage.measurements import center_of_mass as com
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.utils.paths import getnetworkdataroot
provenance = ProvenanceWrapper()
#setup paths and files
fs = Path(getnetworkdataroot())
project = 'bbc'
tf = fs / project / 'reg' / 'meg_spheres_in_template_space' / 'bbc_pairedLH_template_reg2pol.nii.gz'
#load pre-rotated brain only template file (tf)
tf_img = nibabel.load(str(tf))
tf_data = tf_img.get_data()
#get center of mass of template
tf_data_com = np.rint(com(tf_data)).astype(int)
#isolate xdim of com
sphere_xrow = tf_data[:,tf_data_com[1], tf_data_com[2]]
#find radius in vox by marching out from center to value near 0
for x, xval in enumerate(sphere_xrow[tf_data_com[0]:]):
    if xval < 0.1:
        break
#add 5 vox for missing scalp and convert to mm
rx = int((x + 5) * tf_img.header.get_zooms()[0])
#build sphere
spheredata = np.zeros(tf_data.shape)
for x in range(spheredata.shape[0]):
    for y in range(spheredata.shape[1]):
        for z in range(spheredata.shape[2]):
            #calculate radius in mm on xyz coordinate
            dist = np.sqrt(np.sum(np.square((np.array([x, y, z]) - tf_data_com) * tf_img.header.get_zooms())))
            if (dist > (rx - 1)) and (dist < (rx + 1)):
                spheredata[x, y, z] = 1
#set path/out file name
outf = fs / project / 'reg' / 'meg_spheres_in_template_space' / str('bbc_pairedLH_template_reg2pol_sphere-r'+str(rx)+'.nii')
#set qform offsets to center of sphere eg. com
sphere_affine = np.diag(list(tf_img.header.get_zooms()) +[1]) * (-1,1,1,1,)
sphere_affine[:3,3] = tf_data_com * tf_img.header.get_zooms() * (1,-1,-1)
#create nifti image, edit header and save
sphere_img = nibabel.Nifti1Image(spheredata, sphere_affine)
sphere_img.set_qform(sphere_affine, code=2)
sphere_img.set_sform(sphere_affine, code=2)
sphere_img.header['cal_max'] = 1.0
nibabel.save(sphere_img, str(outf))
params = {}
params['radius in mm'] = rx
params['affine'] = sphere_affine
params['com'] = tf_data_com
#provenance.log(str(outf), 'make sphere for xfit MEG dipole localization', str(tf), script=__file__, provenance=params)