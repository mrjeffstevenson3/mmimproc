from __future__ import division # division always floating point
import nibabel, numpy
from datetime import datetime
from numpy import mean, sqrt, square
from pylabs.utils import progress
from pylabs.geometry.triangle import triangleHeight

# optionally create fluid mask with values that show likelihood for being in box
## Optimizations:
# cache triangle height per edge
# break loop if one vxp is much larger than box
# numpy.array(side) earlier
# matrix operations.

def createBoxMask(coords, referenceFilepath, outFilepath='box.nii.gz', 
        tolerance=.01):

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
    boxVolumeThreshold = boxVolume * (1 + tolerance)
    maxDimSize = max(boxWidth, boxHeight, boxLength)
    distanceThreshold = maxDimSize * sqrt(3) # diagonal of box
    msg = 'Box W={0:.2f} H={1:.2f} L={2:.2f} V={3:.2f}'
    print(msg.format(boxWidth,boxHeight,boxLength,boxVolume))

    img = nibabel.load(referenceFilepath)
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
    #            if not voxelTooFar:
    #                data[x, y, z] = pyrvols.sum()
                if pyrvols.sum() < boxVolumeThreshold:
                    data[x, y, z] = bright
                elif voxelTooFar:
                    data[x, y, z] = data[x, y, z] * .5 
                elif numpy.any(numpy.isnan(pyrvols)):
                    raise ValueError('NaN encountered.')
    print(' ')

    newimg = nibabel.Nifti1Image(data, affine)
    nibabel.save(newimg, outFilepath)








