from nose.tools import (assert_raises, assert_equal, assert_not_equal,
                        assert_true)
import os, shutil
from pylabs.behavior.conversion import csv2fslmat

sampledir = 'pylabs/behavior/tests/sampledata/'

def test_x():
    if os.path.isdir('matfiles'):
        shutil.rmtree('matfiles') # clean up
    csvfile = sampledir+'behavior.csv'
    csv2fslmat(csvfile=csvfile)
    assert_true(os.path.isfile('matfiles/cardsorttotal.mat'))
    with open('matfiles/cardsorttotal.mat') as createdfile:
        with open(sampledir+'cardsorttotal.mat') as correctfile:
            assert_equal(createdfile.read(), correctfile.read())
