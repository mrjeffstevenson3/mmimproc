.. -*- mode: rst -*-

.. image:: https://magnum.travis-ci.com/ilabsbrainteam/pylabs.svg?token=aHq2kykzNqPpTyYNZ3a9
  :target: https://magnum.travis-ci.com/ilabsbrainteam/pylabs

.. image:: https://coveralls.io/repos/ilabsbrainteam/pylabs/badge.png
  :target: https://coveralls.io/r/ilabsbrainteam/pylabs

`pylabs`_
=========

This package is designed for processing multi-modal neuroimaging
data collected by the Kuhl lab.

Requirements for the Python environment:

- `numpy <http://www.numpy.org>`_
- `scipy <http://www.scipy.org>`_
- `matplotlib <http://matplotlib.org>`_
- `nibabel <http://github.com/nipy/nibabel>`_ (see the `tutorial <http://nipy.org/nibabel/gettingstarted.html>`_)
- `scikit-learn <http://scikit-learn.org>`_

Requirements for the system:

- `DTIPrep <http://www.nitrc.org/projects/dtiprep/>`_
- `Freesurfer <https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall>`_
- `FSL <http://fsl.fmrib.ox.ac.uk/fsldownloads/fsldownloadmain.html>`_
- `Slicer <http://download.slicer.org/>`_

Optional:

- `mne-python <http://github.com/mne-tools/mne-python>`_ (for M/EEG data)
- `MNE-C <http://www.nmr.mgh.harvard.edu/martinos/userInfo/data/MNE_register>`_ (for M/EEG data)
- `NODDI <http://mig.cs.ucl.ac.uk/index.php?n=Tutorial.NODDImatlab>`_ (for a different diffusion method)
