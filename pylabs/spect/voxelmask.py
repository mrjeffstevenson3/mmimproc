from nipype.interfaces import fsl
import nibabel
import matplotlib.pyplot as plt


coordsfile = 'pylabs/spect/coords.txt'
basefile = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')

coords = []
with open(coordsfile) as cfile:
    lines = cfile.readlines()
    for line in lines:
        coords.append([float(n) for n in line.split()[0:3]])
coords = numpy.round(coords).astype(int)

raise ValueError

sides = [
(0,1),
(1,2),
(2,3),
(4,5),
(5,6),
(6,7),
(0,4),
(1,5),
(2,6),
(3,7),
(0,3),
(4,7),
]
nsides = len(sides)

img = nibabel.load(basefile)
data = img.get_data()
bright = data.max()
dims = data.shape

for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
            sideResults = []
            for side in sides:
                sideVector = coords[side[0]] - coords[side[1]]
                pointVector = coords[side[0]] - numpy.array((x,y,z))
                sideResults.append(0 < numpy.cross(sideVector,pointVector))
            if sum(sideResults) == nsides:
                data[x,y] = bright


plt.imshow(data[:,100,:])
plt.show()


#In  my coordinate system, 
#X is A/P, 0 at back of brain
#Y is L/R, 0 at right of brain
#Z is slice direction, 0 at bottom of brain



