# -*- coding: utf-8 -*-
from pathlib import *
import os
import tempfile
import shutil
import datetime


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
    if file.suffixes == [] or file_exts == '':
        return Path(str(file)+suff)
    else:
        return Path(str(file).replace(file_exts, suff+file_exts))

def replacesuffix(file, suff):
    '''
    Replaces existing suffix with new string + extention(s).
    :param file: pathlib path and file name with ext (ext optional)
    :param suff:  string to append at end of file name such as '_brain.nii.gz' or '_brain_mask.nii.gz
    :return: returns reformed posix path with string added at end of file name and new extension.
    '''
    file = Path(file)
    if len(file.suffixes) <= 1:
        return Path(str(file.parent/file.stem)+suff)
    else:
        return Path(str(file.parent/Path(file.stem).stem)+suff)

def removesuffix(file):
    '''
    Replaces existing suffix with new string + extention(s).
    :param file: pathlib path and file name with ext (ext optional)
    :param suff:  string to append at end of file name such as '_brain.nii.gz' or '_brain_mask.nii.gz
    :return: returns reformed posix path with string added at end of file name and new extension.
    '''
    file = Path(file)
    if len(file.suffixes) <= 1:
        return Path(str(file.parent/file.stem))
    elif len(file.suffixes) == 2:
        return Path(str(file.parent/Path(file.stem).stem))
    elif len(file.suffixes) == 3:
        return Path(str(file.parent/Path(Path(file.stem).stem).stem))
    elif len(file.suffixes) > 3:
        raise ValueError('more than 3 extensions. this function not set up to handle more than 3.')

def prependposix(file, prefix):
    '''
    Adds prefix to beginning of file basename, then puts path back on.
    :param file: pathlib path and file name with ext (ext optional)
    :param prefix:  string to prepend at beginning of file name.
    :return: returns reformed posix path with string added at beginning of file name and extension.
    '''
    file = Path(file)
    new_name = str(prefix) + file.name
    return Path(file.parent/new_name)

def insertdir(file, newdir):
    '''
    inserts dir into last line of path for file. e.g /root/exist_dir1/file.ext to /root/exist_dir1/newdir/file.ext
    '''

    file = Path(file)
    return file.parent/newdir/file.name

def bumptodefunct(file):
    '''
    this function moves and renames file down into a defunct directory with a date stamp
    Args:
        file: the posix file to rename and move
    '''
    file = Path(file)
    if not (file.parent / 'defunct').is_dir():
        (file.parent / 'defunct').mkdir(parents=True)
    if file.is_file():
        new_fname = appendposix(insertdir(file, 'defunct'), '_replaced_on_{:%Y%m%d%H%M}'.format(datetime.datetime.now()))
        file.rename(new_fname)
        print(str(file)+' moved to defunct as '+str(new_fname))
    if file.is_dir():
        new_dirname = file.parent/'defunct'/(str(file.name)+'_replaced_on_{:%Y%m%d%H%M}'.format(datetime.datetime.now()))
        file.rename(new_dirname)
        print(str(file) + ' directory moved to defunct as ' + str(new_dirname))
    return

