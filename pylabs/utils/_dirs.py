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


def appendposix(file, suff):
    '''
    Adds suffix to end of file basename, then puts extention(s) back on.
    :param file: pathlib path and file name with ext (ext optional)
    :param suff:  string to append at end of file name such as '_brain' or '_brain_mask
    :return: returns reformed posix path with string added at end of file name and extension.
    '''
    file = Path(file)
    file_exts = ''.join(file.suffixes)
    return Path(str(file).replace(file_exts, suff+file_exts))

