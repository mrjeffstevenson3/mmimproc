megaxis_vox_origin_mni = (90, 90, 52)

for i, offset in enumerate(megaxis_vox_origin_mni):
    dome_coord[i,:] = dome_coord[i,:] - offset