# -*- coding: utf-8 -*-

from nose.tools import assert_raises
from pylabs.utils import run_subprocess


def test_run():
    """Test running subprocesses
    """
    bad_name = 'foo_nonexist_test'
    assert_raises(Exception, run_subprocess, [bad_name])
    assert_raises(Exception, run_subprocess, ['f2py', '-c', '-m', 'demo_add',
                                              bad_name])
