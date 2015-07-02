from nose.tools import (assert_raises, assert_equal, assert_not_equal,
                        assert_true)
import os, shutil, unittest
from mock import Mock
from hamcrest import anything
from pylabs.correlation.conversion import csv2fslmat

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


def test_formatted_filename():
    filesys = Mock()
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile, selectSubjects=[317, 396], filesys=filesys)
    assert_equal(filesys.write.call_args[0][0],'matfiles/c2b38s2d_inhtot.mat')

