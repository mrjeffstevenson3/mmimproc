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
    Same as append2fn below. older code. Adds suffix to end of file basename, then puts extention(s) back on.
    :param file: pathlib path and file name with ext (ext optional)
    :param suff:  string to append at end of file name such as '_brain' or '_brain_mask
    :return: returns reformed posix path with string added at end of file name and extension.
    todo: refactor and replace with append2fn
    '''
    file = Path(file)
    file_exts = ''.join(file.suffixes)
    if file.suffixes == [] or file_exts == '':
        return Path(str(file)+suff)
    else:
        return Path(str(file).replace(file_exts, suff+file_exts))

def append2fn(fn, newstr):
    """
    Appends new string to end of file name and before file .nii or .nii.gz extensions.
    Preserves file path if file path exists.
    """
    if str(Path(fn).parent) == '.':
        return Path(Path(fn).stem).stem + newstr + ''.join(Path(fn).suffixes)
    else:
        return Path(Path(fn).parent, Path(Path(fn).stem).stem + newstr + ''.join(Path(fn).suffixes))


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


def prependposix(infile, prefix):
    """
    Adds prefix to beginning of file basename, then puts path back on.
    :param infile: pathlib path and file name with ext (ext optional)
    :param prefix:  string to prepend at beginning of file name.
    :return: returns reformed posix path with string added at beginning of file name and extension.
    """
    infile = Path(infile)
    new_name = str(prefix) + infile.name
    return Path(infile.parent/new_name)


def remove_prepend(infile, prefix):
    """
    Removes prefix to beginning of file basename, then puts path back on.
    :param infile: pathlib path and file name with ext (ext optional)
    :param prefix:  string to be removed from beginning of file name.
    :return: returns reformed posix path with string removed from beginning of file name.
    """
    infile = Path(infile)
    if prefix in ['.nii', '.nii.gz', '.hdr', '.img', '.vtk', '.h5']:
        raise ValueError('prefix to remove conflicts with file extensions.')
    new_name = infile.name.replace(prefix, '')
    return Path(infile.parent/new_name)


def insertdir(infile, newdir):
    """
    inserts dir into last line of path for file. e.g /root/exist_dir1/file.ext to /root/exist_dir1/newdir/file.ext
    """

    infile = Path(infile)
    return infile.parent/newdir/infile.name


def bumptodefunct(infile):
    """
    this function moves and renames file down into a defunct directory with a date stamp
    Args:
        infile: the posix file or directory to rename and move
    """
    infile = Path(infile)
    if not (infile.parent / 'defunct').is_dir():
        (infile.parent / 'defunct').mkdir(parents=True)
    if infile.is_file():
        new_fname = appendposix(insertdir(infile, 'defunct'), '_replaced_on_{:%Y%m%d%H%M}'.format(datetime.datetime.now()))
        infile.rename(new_fname)
        print(str(infile)+' moved to defunct as '+str(new_fname))
    if infile.is_dir():
        new_dirname = infile.parent/'defunct'/(str(infile.name)+'_replaced_on_{:%Y%m%d%H%M}'.format(datetime.datetime.now()))
        infile.rename(new_dirname)
        print(str(infile) + ' directory moved to defunct as ' + str(new_dirname))
    return

