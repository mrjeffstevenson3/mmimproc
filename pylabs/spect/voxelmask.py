from __future__ import division # division always floating point
from nipype.interfaces import fsl
import nibabel, numpy
from datetime import datetime
from numpy import mean, sqrt, square
import matplotlib.pyplot as plt
from pylabs.utils import progress


# http://math.stackexchange.com/questions/1472049/check-if-a-point-is-inside-a-rectangular-shaped-area-3d
# http://math.stackexchange.com/questions/190111/how-to-check-if-a-point-is-inside-a-rectangle?lq=1
# http://www.mathopenref.com/pyramidvolume.html
# find height of one pyramid side, find height of opposite side. height of pyramid is the height of the # triangle formed by these two

def triangleHeight(b, a, c):
    # base is b
    allSides = [a,b,c]
    if 0 in allSides:
        return 0.0
    longestSide = max(allSides)
    if longestSide > (sum(allSides)-longestSide):
        # Not a valid triangle, assume rounding error
        return 0.0
    s = (a+b+c)/2 # semiperimeter 
    area = sqrt(s*(s-a)*(s-b)*(s-c)) # Heron's
    h = area/(b/2)
    return h


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
oppositeEdges = [(0,2),(1,3)]
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
maxDimSize = max(boxWidth, boxHeight, boxLength)
distanceThreshold = maxDimSize * sqrt(3) * 1.1 # diagonal of box + 10%
msg = 'Box W={0:.2f} H={1:.2f} L={2:.2f} V={3:.2f}'
print(msg.format(boxWidth,boxHeight,boxLength,boxVolume))

# pyramids


img = nibabel.load(basefile)
affine = img.get_affine()
data = img.get_data()
bright = data.max() * 1.2
dims = data.shape
nvoxels =  numpy.prod(dims)

v = 0
start = datetime.now()
for x in range(dims[0]):
    for y in range(dims[1]):
        for z in range(dims[2]):
            v += 1
            progress.progressbar(v, nvoxels, start)
            p = numpy.array([x,y,z])
            voxelTooFar = False

            pyrvols = numpy.zeros((nsides,))
            pyrvols[:] = numpy.NAN
            for s, side in enumerate(sides):
                sideArray = numpy.array(side)
                triangleHeights = [0, 0]
                triangleBaseEdges = sideArray[[0, 2]]
                for t, edgeIndex in enumerate(triangleBaseEdges):
                    v1, v2 = [coords[vertex] for vertex in edges[edgeIndex]]
                    base = edgeLengths[edgeIndex]
                    v1p = sqrt(numpy.sum(square(v1-p)))
                    if v1p > distanceThreshold:
                        voxelTooFar = True
                        break
                    v2p = sqrt(numpy.sum(square(v2-p)))
                    triangleHeights[t] = triangleHeight(base, v1p, v2p)
                else:
                    normalTriangleBase = mean(edgeLengths[sideArray[[1,3]]])
                    pyrHeight = triangleHeight(normalTriangleBase, *triangleHeights)
                    pyrvols[s] = (pyrHeight*sideAreas[s])/3.
                if voxelTooFar:
                    break
            if pyrvols.sum() < boxVolume:
                data[x, y, z] = bright
            elif voxelTooFar:
                data[x, y, z] = data[x, y, z] * .5 
print(' ')

newimg = nibabel.Nifti1Image(data, affine)
nibabel.save(newimg, 'gabaVoxel.nii.gz')


# plt.imshow(data[:,100,:])
# plt.show()


## Optimizations:
# cache triangle height per edge
# break loop if one vxp is much larger than box
# numpy.array(side) earlier

#In  my coordinate system, 
#X is A/P, 0 at back of brain
#Y is L/R, 0 at right of brain
#Z is slice direction, 0 at bottom of brain



