from nose.tools import (assert_raises, assert_equal, assert_not_equal,
                        assert_true)
import os, shutil, unittest
from pylabs.correlation.conversion import csv2fslmat

sampledir = 'pylabs/correlation/tests/sampledata/'

def test_basic():
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile)
    assert_true(os.path.isfile('matfiles/cardsorttotal.mat'))
    with open('matfiles/cardsorttotal.mat') as createdfile:
        with open(sampledir+'cardsorttotal.mat') as correctfile:
            assert_equal(createdfile.readlines(), correctfile.readlines())

def test_select_two_subjects():
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile, selectSubjects=[317, 396])
    assert_true(os.path.isfile('matfiles/cardsorttotal.mat'))
    with open('matfiles/cardsorttotal.mat') as createdfile:
        with open(sampledir+'cardsorttotal_only2.mat') as correctfile:
            assert_equal(createdfile.readlines(), correctfile.readlines())
