import os
from pathlib import *


class WorkingContext(object):
    """
    Used to execute a command in directory other than python working dir.
    Now compatible with pathlib.
    Example
    -------
    from mmimproc.utils import WorkingContext
    with WorkingContext("/myworkingdir"):
        execute commands to run with "/myworkingdir" as cwd.

    resumes execution with orig python cwd
    """

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        self.startdir = Path.cwd()
        if not self.workdir.is_dir():
            self.workdir.mkdir(parents=True)

    def __enter__(self):
        if not (self.startdir == self.workdir):
            os.chdir(str(self.workdir))

    def __exit__(self, exctype, excval, exctb):
        if not (self.startdir == self.workdir):
            os.chdir(str(self.startdir))
