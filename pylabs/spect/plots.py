import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

import numpy
from numpy.random import randn
from scipy import array, newaxis


def plotcoords(DATA):

    Xs = DATA[:,0]
    Ys = DATA[:,1]
    Zs = DATA[:,2]


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_trisurf(Xs, Ys, Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)

#    ax.xaxis.set_major_locator(MaxNLocator(5))
#    ax.yaxis.set_major_locator(MaxNLocator(6))
#    ax.zaxis.set_major_locator(MaxNLocator(5))

    fig.tight_layout()

    plt.show() # or:
    # fig.savefig('3D.png')
