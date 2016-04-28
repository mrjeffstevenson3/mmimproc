import numpy
import matplotlib.pyplot as plt


class ScaledPolyfit(object):

    def __init__(self, X, Y, degrees, xscaling=False):
        self.xscaling = xscaling
        self.X = X
        self.Y = Y
        self.xmean = X.mean()
        self.xstd = X.std()
        if xscaling:
            Xz = (X-self.xmean)/self.xstd
        else:
            Xz = X
        self.p = numpy.polyfit(Xz, self.Y, degrees)
        self.poly1d = numpy.poly1d(self.p)

    def calc(self, X):
        if self.xscaling:
            Xz = (X-self.xmean)/self.xstd
        else:
            Xz = X
        return self.poly1d(Xz)

    def plot(self):
        xspace = numpy.linspace(self.X.min()-100, self.X.max()+100, 200)
        plt.plot(self.X, self.Y, 'bo', xspace, self.calc(xspace))

