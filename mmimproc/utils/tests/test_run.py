# -*- coding: utf-8 -*-

import os
from os import path as op
from nose.tools import (assert_raises, assert_equal, assert_not_equal,
                        assert_true)

from mmimproc.utils import run_subprocess, InTempDir


def test_run():
    """Test running subprocesses
    """
    bad_name = 'foo_nonexist_test'
    assert_raises(Exception, run_subprocess, [bad_name])
    assert_raises(Exception, run_subprocess, ['f2py', '-c', '-m', 'demo_add',
                                              bad_name])


def test_dirs():
    """Test directory use
    """
    # This implicitly tests InDir as well, since InTempDir subclasses it
    orig_dir = os.getcwd()
    with InTempDir():
        temp_dir = os.getcwd()
        assert_not_equal(temp_dir, orig_dir)
        assert_true(op.isdir(temp_dir))

    assert_equal(os.getcwd(), orig_dir)
    assert_true(not op.isdir(temp_dir))

