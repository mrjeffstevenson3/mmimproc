import os, sys
import datetime


class Filesystem(object):
    """Wrapper of filesystem access functionality such as that implemented by 
    the os package in the standard library.
    """

    def __init__(self):
        self.open = open

    def fileExists(self, path):
        return os.path.isfile(path) 

    def walk(self, path):
        return os.walk(path)

    def readlines(self, path):
        with open(path) as fhandle:
            lines = fhandle.read().splitlines()
        return lines

    def makedirs(self, dirs):
        if not os.path.isdir(dirs):
            os.makedirs(dirs)

    def read(self, path):
        """Read the contents of a textfile.

        Args:
            path: Path to the file to read.

        Returns:
            str: Contents of the file

        Raises:
            IOError: [Errno 2] No such file or directory: 'xyz'
        """
        with open(path) as fhandle:
            contents = fhandle.read()
        return contents

    def write(self, path, content):
        """Write string content to a textfile.

        Args:
            path: Path to the file to read.
            content (str): What to fill the file with
        """
        with open(path, 'w') as fhandle:
            fhandle.write(content)

    def getsize(self, path):
        return os.path.getsize(path)

    def getctime(self, path):
        """Get the creation time for the file at path.

        Args:
            path: Path to the file to read.

        Returns:
            datetime: Time when the file was last changed
        """
        return datetime.datetime.fromtimestamp(os.path.getctime(path))

def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.
    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.
    Note: This function was backported from the Python 3 source code.
    """

    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode) and
                not os.path.isdir(fn))

    # If we're given a path with a directory part, look it up directly
    # rather than referring to PATH directories. This includes checking
    # relative to the current directory, e.g. ./script
    if os.path.dirname(cmd):
        if _access_check(cmd, mode):
            return cmd
        return None

    if path is None:
        path = os.environ.get("PATH", os.defpath)
    if not path:
        return None
    path = path.split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if os.curdir not in path:
            path.insert(0, os.curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path
        # extensions. This will allow us to short circuit when given
        # "python.exe". If it does match, only test that one, otherwise we
        # have to try others.
        if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
            files = [cmd]
        else:
            files = [cmd + ext for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for dir in path:
        normdir = os.path.normcase(dir)
        if normdir not in seen:
            seen.add(normdir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if _access_check(name, mode):
                    return name
    return None