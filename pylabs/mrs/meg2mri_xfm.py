import numpy as np
from os import path as op
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mne
from mne.bem import (_fit_sphere, fit_sphere_to_headshape)

def transform(loc_headcoord_subj, ctr_sphere_headcoord_subj, rad_template,
              ctr_sphere_headcoord_template, rad_subj):
    # remove offset to sphere from head coordinates (+RAS)
    loc_sphere_subj = loc_headcoord_subj - ctr_sphere_headcoord_subj
    # dipole in head coordinates scaled to template
    loc_sphere_template = np.array(loc_sphere_subj) * rad_template / rad_subj
    # scaled dipole location offset to MRI sphere in head coordinates
    return loc_sphere_template + ctr_sphere_headcoord_template

# Radius and center (mm) of best fit sphere to Polhemus digitized headshape points
rad, ctr = mne.bem.fit_sphere_to_headshape(mne.io.read_info
                                           (op.join(workdir, 'All_30-sss_eq_kubi_td118-ave.fif')),
                                           units='mm', verbose=True)[:2]

cannonical_pts = np.array([[rad, 0, 0], [-rad, 0, 0],
                           [0, rad, 0], [0, -rad, 0],
                           [0, 0, rad], [0, 0, -rad]])
cannonical_pts += ctr
fig = plt.figure()
ax = Axes3D(fig)
ax.scatter3D(cannonical_pts[:,0],
             cannonical_pts[:,1],
             cannonical_pts[:,2], marker='*', color='r')
ax.set_xlabel('LR (mm)')
ax.set_ylabel('AP')
ax.set_zlabel('IS')

cannonical_pts_in_mri_ras = np.zeros(cannonical_pts.shape)
ref_rad = 67. # mri sphere radius
ref_ctr = np.array([0, 10, 25]) # origin of sphere in mri head coordinates
for si in range(cannonical_pts.shape[0]):
    dipolexyz = cannonical_pts[si]
    cannonical_pts_in_mri_ras[si] = transform(loc_headcoord_subj=dipolexyz, ctr_sphere_headcoord_subj=ctr,
                                             rad_subj=rad, rad_template=ref_rad,
                                             ctr_sphere_headcoord_template=ref_ctr)

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter3D(cannonical_pts_in_mri_ras[:,0],
             cannonical_pts_in_mri_ras[:,1],
             cannonical_pts_in_mri_ras[:,2], marker='*', color='b')
ax.set_xlabel('LR (mm)')
ax.set_ylabel('AP')
ax.set_zlabel('IS')