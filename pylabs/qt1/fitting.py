import warnings
import numpy
import nibabel
from scipy.optimize import curve_fit


def irformula(x, a, b, c):
    return numpy.abs(a * (1 - b * numpy.exp(-x/c)))

def t1fit(files, X, maskfile=None, scantype='IR', t1filename=None):
    if t1filename is None:
        t1filename = 't1_fit.nii.gz'

    if isinstance(files, basestring):
        anImg = nibabel.load(files)
        imageDimensions = anImg.shape[:-1]
        data = [anImg.get_data()[...,i].ravel() for i in range(anImg.shape[-1])]
    else:
        anImg = nibabel.load(files[0])
        imageDimensions = anImg.shape
        data = [nibabel.load(f).get_data().ravel() for f in files]

    if maskfile is not None:
        maskImg = nibabel.load(maskfile)
        if maskImg.shape != imageDimensions:
            errmsg = 'Mask dimensions {0} not the same as image {1}.'
            raise ValueError(errmsg.format(maskImg.shape, imageDimensions))
        mask = maskImg.get_data().ravel()

    affine = anImg.get_affine()
    X = numpy.array(X)
    nx = len(X)
    ny = len(data)
    msg = 'Fitting {0} points with image dimensions {1}.'
    print(msg.format(nx, imageDimensions))
    if not nx == ny:
        msg = 'Number of parameters ({0}) does not match number of images ({1}).'
        raise ValueError(msg.format(nx, ny))

    nvoxels = data[0].size
    t1data = numpy.zeros(data[0].shape)
    for v in range(nvoxels):
        Y = [image[v] for image in data]
        if maskfile is not None
            if not mask[v]:
                continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if scantype == 'IR':
                    ai = Y[X.argmax()]
                    bi = 2
                    ci = 1000
                    p0=[ai, bi, ci]
                    popt, pcov = curve_fit(irformula, X, Y, p0=p0)
                    t1data[v] = popt[2]
                else:
                    raise ValueError('Unknown scantype: '+scantype)
        except RuntimeError:
            pass
    t1data = t1data.reshape(imageDimensions)
    t1img = nibabel.Nifti1Image(t1data, affine)
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
