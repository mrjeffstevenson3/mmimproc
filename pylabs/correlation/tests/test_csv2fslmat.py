from nose.tools import (assert_raises, assert_equal, assert_not_equal,
                        assert_true)
import os, shutil, unittest
from mock import Mock, patch
from hamcrest import anything
from pylabs.correlation.behavior import csv2fslmat
import numpy

sampledir = 'pylabs/correlation/tests/sampledata/'

def test_basic():
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile)
    assert_true(os.path.isfile(correctmatfilename(24)))
    with open(correctmatfilename(24)) as createdfile:
        with open(sampledir+'cardsorttotal.mat') as correctfile:
            assert_equal(createdfile.readlines(), correctfile.readlines())

def test_select_two_subjects():
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile, selectSubjects=[317, 396])
    assert_true(os.path.isfile(correctmatfilename(2)))
    with open(correctmatfilename(2)) as createdfile:
        with open(sampledir+'cardsorttotal_only2.mat') as correctfile:
            assert_equal(createdfile.readlines(), correctfile.readlines())

def correctmatfilename(nsubjects):
    return 'matfiles/c2b05s{0}d_cardsorttotal.mat'.format(nsubjects)

def assert_called_with_array(callee, A):
    numpy.testing.assert_equal(callee.call_args[0][0], A)


def test_formatted_filename():
    filesys = Mock()
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile, selectSubjects=[317, 396], filesys=filesys)
    assert_equal(filesys.write.call_args[0][0],'matfiles/c2b38s2d_inhtot.mat')

def test_demeaning():
    csvfile = sampledir+'behavior_simple.csv'
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        csv2fslmat(csvfile=csvfile, filesys=Mock())
        # (by default) values written out should be demeaned.
        assert_called_with_array(
            FslMatFile().setData, numpy.array([[-2],[-1],[0],[1],[2]]))
        csv2fslmat(csvfile=csvfile, filesys=Mock(), demean=False)
        # values written out should not be demeaned.
        assert_called_with_array(
            FslMatFile().setData, numpy.array([[28],[29],[30],[31],[32]]))

def test_group_column():
    csvfile = sampledir+'behavior_simple.csv'
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        csv2fslmat(csvfile=csvfile, filesys=Mock(), groupcol=False)
        assert_called_with_array(
            FslMatFile().setData, numpy.array([[-2],[-1],[0],[1],[2]]))
        csv2fslmat(csvfile=csvfile, filesys=Mock(), groupcol=True)
        assert_called_with_array(
            FslMatFile().setData, numpy.array([[1,-2],[1,-1],[1,0],[1,1],[1,2]]))

def test_filenames_returned():
    pass


#    with patch('pylabs.correlation.behavior.numpy.loadtxt') as loadtxt:
#        loadtxt.return_value = [11,10,9]
