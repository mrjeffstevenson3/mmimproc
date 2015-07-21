from nose.tools import (assert_raises, assert_equal, assert_not_equal,
                        assert_true)
import os, shutil, unittest
from mock import Mock, patch
from pylabs.correlation.behavior import csv2fslmat
import pylabs.correlation.behavior
import numpy

sampledir = 'pylabs/correlation/tests/sampledata/'
cd = os.getcwd()


def test_saves_with_filename():
    correctmatfilename = os.path.join(cd, 'matfiles/c1b05s5d_cardsorttotal.mat')
    csvfile = sampledir+'behavior_simple.csv'
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        csv2fslmat(csvfile=csvfile, filesys=Mock())
        FslMatFile().saveAs.assert_called_with(correctmatfilename)

def test_formatted_filename():
    filesys = Mock()
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile, selectSubjects=[317, 396], filesys=filesys)
    assert_equal(filesys.write.call_args[0][0],
        os.path.join(cd,'matfiles/c1b38s2d_inhtot.mat'))

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

def test_can_pick_columns():
    csvfile = sampledir+'behavior_simple.csv'
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        csv2fslmat(csvfile=csvfile, filesys=Mock(), demean=False, 
            groupcol=False, cols=[3, 4])
        assert_called_with_array(
            FslMatFile().setData, numpy.array( [[41530],
                                                [41505],
                                                [41503],
                                                [41529],
                                                [41526]]))

def test_Can_add_covariate_columns():
    csvfile = sampledir+'behavior_simple.csv'
    expectedFnames = [os.path.join(cd, 'matfiles/c3b03s5d_age.mat'),
                      os.path.join(cd, 'matfiles/c3b04s5d_DOT.mat')]
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        fnames = csv2fslmat(csvfile=csvfile, filesys=Mock(), demean=False, 
            groupcol=False, cols=[3, 4], covarcols=[2, 3])
        assert_called_with_array(
            FslMatFile().setData, numpy.array( [[41530, 1, 20],
                                                [41505, 1, 30],
                                                [41503, 0, 50],
                                                [41529, 0, 40],
                                                [41526, 0, 40]]))
    assert_equal(expectedFnames, fnames)

def test_filenames_returned():
    csvfile = sampledir+'behavior_simple.csv'
    expectedFnames = [os.path.join(cd, 'matfiles/c1b03s5d_age.mat'),
                    os.path.join(cd, 'matfiles/c1b04s5d_DOT.mat')]
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        fnames = csv2fslmat(csvfile=csvfile, filesys=Mock(), demean=False, 
            groupcol=False, cols=[3, 4])
    assert_equal(expectedFnames, fnames)

def test_calls_niprov_log_and_passes_opts():
    opts = Mock()
    behavmod = pylabs.correlation.behavior.__file__
    csvfile = sampledir+'behavior_simple.csv'
    with patch('pylabs.correlation.behavior.niprov') as niprov:
        fnames = csv2fslmat(csvfile=csvfile, opts=opts, filesys=Mock())
        niprov.log.assert_any_call(fnames[0], 'csv2fslmat', csvfile, 
            script=behavmod, opts=opts)

def test_uses_tag_argument_to_name_matfiles_subdir():
    csvfile = sampledir+'behavior_simple.csv'
    expectedFnames = [os.path.join(cd, 'matfiles_helloworld/c1b03s5d_age.mat'),
        os.path.join(cd, 'matfiles_helloworld/c1b04s5d_DOT.mat')]
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        fnames = csv2fslmat(csvfile=csvfile, tag='helloworld', 
            filesys=Mock(), demean=False, groupcol=False, cols=[3, 4])
    assert_equal(expectedFnames, fnames)

def test_can_override_working_dir_where_to_put_matfiles():
    csvfile = sampledir+'behavior_simple.csv'
    wdir = '/foo/bar/bla/'
    expectedFnames = [os.path.join(wdir, 'matfiles/c1b03s5d_age.mat'),
        os.path.join(wdir, 'matfiles/c1b04s5d_DOT.mat')]
    with patch('pylabs.correlation.behavior.FslMatFile') as FslMatFile:
        fnames = csv2fslmat(csvfile=csvfile, filesys=Mock(), demean=False, 
            groupcol=False, cols=[3, 4], workdir=wdir)
    assert_equal(expectedFnames, fnames)

def assert_called_with_array(callee, A):
    numpy.testing.assert_equal(callee.call_args[0][0], A)
