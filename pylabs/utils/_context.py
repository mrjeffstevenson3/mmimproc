import os


class WorkingContext(object):
    """
    Used to execute a command in directory other than python working dir.
    Example
    -------
    from pylabs.util import WorkingContext
    with WorkingContext("/myworkingdir"):
        execute commands to run with "/myworkingdir" as cwd.

    resumes execution with orig python cwd
    """

    def __init__(self, workdir):
        self.workdir = workdir
        self.startdir = os.getcwd()
        if not os.path.isdir(self.workdir):
            os.makedirs(self.workdir)

    def __enter__(self):
        if not (self.startdir == self.workdir):
            os.chdir(self.workdir)

    def __exit__(self, exctype, excval, exctb):
        if not (self.startdir == self.workdir):
            os.chdir(self.startdir)
