import os, numpy
from pylabs.utils import Filesystem, PylabsOptions

class FslMatFile(object):
    """Fsl Matrix (.mat) file.

    Used to read and write .mat files.
    """

    def __init__(self, filename=None, filesys=Filesystem()):
        """Create an FslMatFile object.

        Args:
            filename (str): Optional. If provided, means the file is read and 
                the returned object will reflect values in the file.
            filesys (Filesystem): Replace for testing purposes.
        """
        self.filesys = filesys
        if filename:
            lines = self.filesys.readlines(filename)
            for line in lines:
                parts = line.split()
                if parts[0] == '/NumWaves':
                    self.numwaves = int(parts[1])

    def setData(self, data):
        """Provide the data array to create a .mat file from.

        Args:
            data (numpy.array): Data to write to the file. Must be 2d.
        """
        self.data = data

    def saveAs(self, fname):
        content = ''
        #content += '/ContrastName1\t{0}\n'.format(measure)
        (w,p) = self.data.shape
        content += '/NumWaves\t{1}\n/NumPoints\t{0}\n'.format(w,p)
        content += '/PPheights\t\t{0:.6e} {1:.6e}\n'.format(
            self.data.min(), self.data.max())
        content += '/Matrix\n'
        for r in range(self.data.shape[0]):
            for c in range(self.data[r,:].size):
                content += '{0:.6e}\t'.format(self.data[r, c])
            content += '\n'
        self.filesys.write(fname, content)
        print(fname)
