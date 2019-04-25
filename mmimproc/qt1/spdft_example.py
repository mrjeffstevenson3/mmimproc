"""
Usage example for spdft
"""
import numpy
import mmimproc.qt1.spdft as spdft

X = numpy.array([1, 2, 3])
Y = numpy.array([4.5, 6, 7.5])

sp = spdft.fit(X, Y)
