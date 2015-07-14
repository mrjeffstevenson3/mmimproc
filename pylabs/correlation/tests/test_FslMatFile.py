from nose.tools import assert_equal
from mock import Mock
import numpy


def test_Fileformat():
    from pylabs.correlation.behavior import FslMatFile
    filesys = Mock()
    expected = ('/NumWaves	2\n'
                '/NumPoints	3\n'
                '/PPheights		-5.000000e+00 5.000000e+00\n'
                '/Matrix\n'
                '1.000000e+00	5.000000e+00	\n'
                '1.000000e+00	-5.000000e+00	\n'
                '1.000000e+00	0.000000e+00	\n')
    fname = 'bla.txt'
    mat = FslMatFile(filesys=filesys)
    #mat.setContrastName('cardsorttotal'))
    mat.setData(numpy.array([[1,5],[1,-5],[1,0]]))
    mat.saveAs(fname)
    filesys.write.assert_called_with(fname, expected)

def test_Fileformat():
    from pylabs.correlation.behavior import FslMatFile
    filesys = Mock()
    expected = ('/NumWaves	3\n'
                '/NumPoints	2\n'
                '/PPheights		-3.000000e+00 5.000000e+00\n'
                '/Matrix\n'
                '1.000000e+00	5.000000e+00	5.000000e+00	\n'
                '1.000000e+00	-3.000000e+00	4.000000e+00	\n')
    fname = 'bla.txt'
    mat = FslMatFile(filesys=filesys)
    #mat.setContrastName('cardsorttotal'))
    mat.setData(numpy.array([[1,5,5],[1,-3,4]]))
    mat.saveAs(fname)
    filesys.write.assert_called_with(fname, expected)
    
