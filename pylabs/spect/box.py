import matplotlib.pyplot as plt
import numpy

# https://www.reddit.com/r/programming/comments/80dlc/i_have_a_set_of_rectangles_and_need_to_determine/

grid = numpy.zeros((40,40))

coords = [numpy.array(x) for x in [(10,10),(30,5),(30,30),(10,25)]]
sides = [(0, 1),(1,2),(2,3),(3,0)]

for vertex in coords:
    grid[vertex[0],vertex[1]] = 3


for x in range(40):
    for y in range(40):
        sideResults = []
        for side in sides:
            sideVector = coords[side[0]] - coords[side[1]]
            pointVector = coords[side[0]] - numpy.array((x,y))
            sideResults.append(0 < numpy.cross(sideVector,pointVector))
        if sum(sideResults) == 4:
            grid[x,y] = 1

plt.imshow(grid)
plt.show()


