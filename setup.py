#! /usr/bin/env python
#
# Copyright (C) 2014 Eric Larson <larson.eric.d@gmail.com>
#    Re-used based on mne-python code.

import os

# we are using a setuptools namespace
import setuptools  # noqa, analysis:ignore
from numpy.distutils.core import setup

descr = """Multimodal neuroscience analysis pipeline functions."""

DISTNAME = 'mmimproc'
DESCRIPTION = descr
MAINTAINER = 'Jeff Stevenson'
MAINTAINER_EMAIL = 'mrjeffstevenson3@gmail.com'
URL = 'http://github.com/mrjeffstevenson3/mmimproc'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'http://github.com/mrjeffstevenson3/mmimproc'
with open(os.path.join('mmimproc', '__init__.py'), 'r') as fid:
    for line in fid:
        if '__version__' in line:
            VERSION = line.strip().split(' = ')[1]
            break

if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          zip_safe=False,  # the package can run out of an .egg file
          classifiers=['Intended Audience :: Science/Research',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved',
                       'Programming Language :: Python',
                       'Topic :: Software Development',
                       'Topic :: Scientific/Engineering',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX',
                       'Operating System :: Unix',
                       'Operating System :: MacOS'],
          platforms='any',
          packages=['mmimproc', 'mmimproc.tests',
                    'mmimproc.utils', 'mmimproc.utils.tests',
                    ],
          install_requires=['niprov >= 0.1.post10'],
          package_data={},
          scripts=[],
          test_suite="tests",)
