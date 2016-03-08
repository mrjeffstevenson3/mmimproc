import nibabel, numpy
from os.path import join
from pylabs.geometry.box import createBoxMask


# no rounding of coords?
# two functions, one with array coords, one with filename


#In  my coordinate system, 
#X is A/P, 0 at back of brain
#Y is L/R, 0 at right of brain
#Z is slice direction, 0 at bottom of brain


spgrpath = '/diskArray/mirror/js/tadpole/tadpole/sub-901/anat'
spgrname = 't1_spgr_7-10-15-20-30_b1corr.nii.gz'
referenceFilepath = join(spgrpath, spgrname)
coordsfile = 'pylabs/mrs/coords.txt'


coords = []
with open(coordsfile) as cfile:
    lines = cfile.readlines()
    for line in lines:
        coords.append([float(n) for n in line.split()[0:3]])
#coords = numpy.round(coords).astype(int)
vertexReOrder = [7, 6, 2, 3, 4, 5, 1, 0] #reorders coords in Neva's order to 
# mine (start top left, front clockwise, back clockwise)
coords = coords[vertexReOrder]
coords = coords[:,[1,0,2]] # switch XY

createBoxMask(coords, referenceFilepath)
