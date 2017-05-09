# -*- coding: utf-8 -*-
from pathlib import *
import os
import tempfile
import shutil


class InDir(object):
    """Context manager to work within a directory temporarily

    Parameters
    ----------
    dir_ : str
        The directory name to work in.
    """
    def __init__(self, dir_):
        self._dir = dir_

    def __enter__(self):
        self._orig_dir = os.getcwd()
        os.chdir(self._dir)

    def __list__(self):
        print(os.listdir(self._dir))

    def __exit__(self, type_, value, tb):
        os.chdir(self._orig_dir)


class InTempDir(InDir):
    """Context manager to mkdir, chdir, and rm -Rf a temp dir"""
    def __init__(self, delete=True):
        self._del = delete
        super(InTempDir, self).__init__(tempfile.mkdtemp())

    def __exit__(self, type_, value, tb):
        super(InTempDir, self).__exit__(type_, value, tb)
        if self._del:
            shutil.rmtree(self._dir)


def appendposix(fname, suff):
    fname = Path(fname)
    ext = fname.suffixes
    l = len(ext)
    ext = ''.join(ext)
    fname = fname.stem
    if l == 2:
        fname = Path(fname).stem
    if l == 3:
        fname = Path(fname).stem
    fname = str(fname)
    fname += suff+ext
    return Path(fname)
