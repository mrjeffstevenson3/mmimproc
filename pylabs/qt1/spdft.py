"""
Python interface to spdft.m
"""
from StringIO import StringIO
import matlab.engine
from matlab import double as mdouble
from pylabs.utils import getnetworkdataroot, pylabs_dir

def fit(X, Y):
    """

    :param X: multi dim
    :param Y: flip angle
    :return:
    """
    Xm = mdouble(X.tolist())
    Ym = mdouble(Y.tolist())
    matlabOut = StringIO()
    eng = matlab.engine.start_matlab()
    eng.addpath(eng.genpath(str(pylabs_dir)))
    dYm = []
    options = {'Xc': mdouble([0, float(X.max())])}
    output = eng.spdft(Xm, Ym, dYm, options, nargout=1, stdout=matlabOut)
    eng.quit()
    print('stdout: {}'.format(matlabOut.getvalue()))
    print('output: {}'.format(output))

    print('Done')
    return output
    
    #/home/toddr/Software/matlab2017b/bin/matlab

