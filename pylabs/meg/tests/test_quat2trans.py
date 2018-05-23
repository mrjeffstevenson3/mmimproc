import unittest, scipy.io, numpy
from numpy.testing import assert_array_equal

class Quat2transTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_Matches_matlab_outcome(self):
        from meg.meanheadpos import quat2trans
        posdata = numpy.loadtxt('data/sample.pos', skiprows=1)
        quat = posdata[:, 1:7]
        matlabresults = scipy.io.loadmat('data/sample_quat2trans.mat')
        matlab_trans = numpy.array(matlabresults['trans'].squeeze().tolist())
        trans = quat2trans(quat)
        assert_array_equal(trans, matlab_trans)


