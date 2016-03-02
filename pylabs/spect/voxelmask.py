from nipype.interfaces import fsl
import nibabel, numpy
from numpy import mean, sqrt, square
import matplotlib.pyplot as plt

# http://math.stackexchange.com/questions/1472049/check-if-a-point-is-inside-a-rectangular-shaped-area-3d
# http://math.stackexchange.com/questions/190111/how-to-check-if-a-point-is-inside-a-rectangle?lq=1
# http://www.mathopenref.com/pyramidvolume.html


coordsfile = 'pylabs/spect/coords.txt'
basefile = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')
nvertices = 8

coords = []
with open(coordsfile) as cfile:
    lines = cfile.readlines()
    for line in lines:
        coords.append([float(n) for n in line.split()[0:3]])
coords = numpy.round(coords).astype(int)
vertexReOrder = [7, 6, 2, 3, 4, 5, 1, 0] #reorders coords in Neva's order to 
# mine (start top left, front clockwise, back clockwise)
coords = coords[vertexReOrder]

edges = [(0,1),(1,2),(2,3),(3,0), #front
         (4,5),(5,6),(6,7),(7,4), #back
         (0,4),(1,5),(2,6),(3,7)] #sides
nedges = len(edges)
sides = [(0,1,2,3),(4,5,6,7),   # front, back
         (8,7,11,3),(9,5,10,1), # left, right, 
         (8,4,9,0),(11,6,10,2)] # top, bottom
nsides = len(sides)
widthEdges = [0,2,4,6]
heightEdges = [1,3,5,7]
LengthEdges = [8,9,10,11]

edgeLengths = numpy.zeros((nedges,))
for e, edge in enumerate(edges):
    v1,v2 = [coords[v] for v in edge]
    edgeLengths[e] = sqrt(numpy.sum(square(v1-v2)))

sideAreas = numpy.zeros((nsides,))
for s, side in enumerate(sides):
    perimeter = edgeLengths[list(side)]
    sideAreas[s] = mean(perimeter[[0,2]]) * mean(perimeter[[1,3]])

boxWidth = mean(edgeLengths[widthEdges])
boxHeight = mean(edgeLengths[heightEdges])
boxLength = mean(edgeLengths[LengthEdges])
boxVolume = boxWidth * boxHeight * boxLength
msg = 'Box W={0:.2f} H={1:.2f} L={2:.2f} V={3:.2f}'
print(msg.format(boxWidth,boxHeight,boxLength,boxVolume))

img = nibabel.load(basefile)
data = img.get_data()
bright = data.max()
dims = data.shape
nvoxels =  numpy.dot(*dims)

raise ValueError
v = 0
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
            v += 1
            # calculate volume of pyramid of each side to point.
            # pyramid volume is 1/3*base area* height
            # height can be determined by getting area using Heron's, 
            # and then inv use formula for area of triangle
            # total volume > volume of box? outside.
            sideResults = []
            for side in sides:
                sideVector = coords[side[0]] - coords[side[1]]
                pointVector = coords[side[0]] - numpy.array((x,y,z))
                sideResults.append(0 < numpy.cross(sideVector,pointVector))
            if sum(sideResults) == nsides:
                data[x, y, z] = bright


plt.imshow(data[:,100,:])
plt.show()


#In  my coordinate system, 
#X is A/P, 0 at back of brain
#Y is L/R, 0 at right of brain
#Z is slice direction, 0 at bottom of brain



