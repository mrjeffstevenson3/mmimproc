import numpy
import nibabel
from scipy.optimize import curve_fit


def t1fitCombinedFile(combinedFile, X, scantype='IR'):
    t1filename = combinedFile.replace('.nii','_t1.nii')
    img = nibabel.load(combinedFile)
    nx = len(X)
    ny = img.shape[3]
    if not nx == ny:
        msg = 'Number of parameters ({0}) does not match number of images ({1}).'
        raise ValueError(msg.format(nx, ny))
    return t1filename



def irformula(x, a, b, c):
    return numpy.abs(a * (1 - b * numpy.exp(-x/c)))


#for coords in data.keys():
#    print('Running for coordinates: '+coords)
#    X = numpy.array(data[coords]['x'])
#    Y = numpy.array(data[coords]['y'])


#    ai = Y[0]
#    bi = 2 # -Y[0]*2
#    ci = 1000
#    popt, pcov = curve_fit(irformula, X, Y, p0=[ai, bi, ci])
#    print('   fitted parameters: a {0} b {1} c {2}'.format(*popt))



#    # plot development over time for each vial
#    Xrange = numpy.arange(5000)
#    fit = [func(x, *popt) for x in Xrange]
#    plt.plot(Xrange, fit) 
#    plt.plot(X, Y, 'bo')
#    plt.savefig('testT1fit.png')

#    lastval = 10000000
#    for x in numpy.arange(0,5000,.1):
#        y = func(x, *popt)
#        if lastval < y:
#            print('zerocrossing: {0}'.format(x))
#            break
#        lastval = y

# todo polarity restoration

#y = S0 (1-V*e pow())

# 80,63,0  1727
# 46,65,0  1113
# 46,30,0   688

# zerocrossing = c * ln(a/b) 
