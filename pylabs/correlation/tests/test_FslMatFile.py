import unittest
from mock import Mock
import numpy


class FslMatFileTests(unittest.TestCase):

    def test_Fileformat(self):
        from pylabs.correlation.fslmatfile import FslMatFile
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

    def test_Fileformat(self):
        from pylabs.correlation.fslmatfile import FslMatFile
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

    def test_After_loading_matfile_can_obtain_NumWaves(self):
        from pylabs.correlation.fslmatfile import FslMatFile
        filesys = Mock()
        content = ['/NumWaves	3\n',
                    '/NumPoints	2\n',
                    '/PPheights		-3.000000e+00 5.000000e+00\n',
                    '/Matrix\n',
                    '1.000000e+00	5.000000e+00	5.000000e+00	\n',
                    '1.000000e+00	-3.000000e+00	4.000000e+00	\n']
        filesys.readlines.return_value = content
        mat = FslMatFile('targetfname', filesys=filesys)
        filesys.readlines.assert_called_with('targetfname')
        self.assertEqual(mat.numwaves, 3)
