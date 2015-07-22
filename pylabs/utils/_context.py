import os


class WorkingContext(object):

    def __init__(self, workdir):
        self.workdir = workdir
        self.startdir = os.getcwd()

    def __enter__(self):
        if not (self.startdir == self.workdir):
            os.chdir(self.workdir)

    def __exit__(self, exctype, excval, exctb):
        if not (self.startdir == self.workdir):
            os.chdir(self.startdir)
