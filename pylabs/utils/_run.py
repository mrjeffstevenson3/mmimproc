# -*- coding: utf-8 -*-

import subprocess
import inspect


def run_subprocess(command, cwd=None):
    """Run command using subprocess.Popen

    Run command and wait for command to complete. If the return code was zero
    then return, otherwise raise CalledProcessError.
    By default, this will also add stdout= and stderr=subproces.PIPE
    to the call to Popen to suppress printing to the terminal.

    Example
    -------
    from pylabs.utils._run import run_subprocess as shellcmd
    1. list files from current python execution directory.

    dirlist = shellcmd(['ls', '-l'])

    2. list files from home directory regardless of current python execution directory.

    homedirlist = shellcmd(['ls', '-l'], cwd=/home)

    Parameters
    ----------
    command : list of str
        Command to run as subprocess (see subprocess.Popen documentation).

    Returns
    -------
    stdout : str
        Stdout returned by the process.
    stderr : str
        Stderr returned by the process.
    """
    # code adapted with permission from mne-python
    kwargs = dict(stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd, shell=True)

    p = subprocess.Popen(command, **kwargs)
    stdout_, stderr = p.communicate()

    output = (stdout_, stderr)
    if p.returncode:
        print(stdout_)
        print(stderr)
        err_fun = subprocess.CalledProcessError.__init__
        if 'output' in inspect.getargspec(err_fun).args:
            raise subprocess.CalledProcessError(p.returncode, command, output)
        else:
            raise subprocess.CalledProcessError(p.returncode, command)

    return output


class Shell(object):

    def run(self, command):
        subprocess.check_call(command.split())
