# -*- coding: utf-8 -*-
"""
================================
Running Fortran code from Python
================================

This example shows how to use f2py to compile and Fortran code from Python.
"""

# Author: Eric Larson <larson.eric.d@gmail.com>
#
# License: BSD (3-clause)
#
# Adapted from:
#    http://docs.scipy.org/doc/numpy/user/c-info.python-as-glue.html

import os
from mmimproc.utils import run_subprocess
import tempfile

os.chdir(os.path.dirname(__file__))

fortran_code = """
C
      SUBROUTINE ZADD(A,B,C,N)
C
CF2PY INTENT(OUT) :: C
CF2PY INTENT(HIDE) :: N
CF2PY DOUBLE COMPLEX :: A(N)
CF2PY DOUBLE COMPLEX :: B(N)
CF2PY DOUBLE COMPLEX :: C(N)
      DOUBLE COMPLEX A(*)
      DOUBLE COMPLEX B(*)
      DOUBLE COMPLEX C(*)
      INTEGER N
      DO 20 J = 1, N
         C(J) = A(J) + B(J)
 20   CONTINUE
      END
"""


with tempfile.NamedTemporaryFile('w', suffix='.f') as fid:
    fid.write(fortran_code)
    fid.flush()
    # This could just as easily be run on a static file instead of
    # "fid.fname", but for convenience let's run it on some code above
    run_subprocess(['f2py', '-c', '-m', 'demo_add', fid.name])

import demo_add

print(demo_add.__doc__)
print('Adding 1+2: %s' % demo_add.zadd(1, 2))
