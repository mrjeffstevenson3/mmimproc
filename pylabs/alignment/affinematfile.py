import numpy as np

class FslAffineMat(object):

    data = None

    def saveAs(self, fname):
        np.savetxt(fname, self.data, fmt='%1.8f')

