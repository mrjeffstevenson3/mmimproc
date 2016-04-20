import numpy
import matplotlib.pyplot as plt


class ScaledPolyfit(object):

    def __init__(self, X, Y, degrees):
        self.X = X
        self.Y = Y
        self.xmean = X.mean()
        #self.ymean = Y.mean()
        self.xstd = X.std()
        #self.ystd = Y.std()
        self.Xz = (X-self.xmean)/self.xstd
        #self.Yz = (X-self.xmean)/self.xstd
        self.p = numpy.polyfit(self.Xz, self.Y, degrees)
        self.poly1d = numpy.poly1d(self.p)

    def calc(self, X):
        Xz = (X-self.xmean)/self.xstd
        return self.poly1d(Xz)
        #Yz = self.poly1d(Xz)
        #return (Yz*self.ystd) + self.ymean

    def plot(self):
        xspace = numpy.linspace(self.X.min()-100, self.X.max()+100, 200)
        plt.plot(self.X, self.Y, 'bo', xspace, self.calc(xspace))

