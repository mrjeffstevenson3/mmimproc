import warnings
import numpy
import nibabel
from scipy.optimize import curve_fit


def irformula(x, a, b, c):
    return numpy.abs(a * (1 - b * numpy.exp(-x/c)))

def t1fitCombinedFile(combinedFile, X, scantype='IR', t1filename=None):
    X = numpy.array(X)
    if t1filename is None:
        t1filename = combinedFile.replace('.nii','_t1.nii')
    img = nibabel.load(combinedFile)
    nx = len(X)
    ny = img.shape[3]
    if not nx == ny:
        msg = 'Number of parameters ({0}) does not match number of images ({1}).'
        raise ValueError(msg.format(nx, ny))
    dims = img.shape[:3]
    t1data = numpy.zeros(dims)
    data = img.get_data()
    for x in range(dims[0]):
        for y in range(dims[1]):
            for z in range(dims[2]):
                Y = data[x, y, z, :]
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        if scantype == 'IR':
                            ai = Y[X.argmax()]
                            bi = 2
                            ci = 1000
                            p0=[ai, bi, ci]
                            popt, pcov = curve_fit(irformula, X, Y, p0=p0)
                            t1data[x,y,z] = popt[2]
                        else:
                            raise ValueError('Unknown scantype: '+scantype)
                except RuntimeError:
                    pass
    t1img = nibabel.Nifti1Image(t1data, img.get_affine())
    nibabel.save(t1img, t1filename)
    return t1filename






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
