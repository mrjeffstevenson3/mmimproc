from pylabs.projects.bbc.dwi.passed_qc import dwi_passed_qc
from pylabs.utils.paths import getnetworkdataroot

fs = getnetworkdataroot()
project = 'bbc'
fname_templ = 'sub-bbc{sid}_ses-{snum}_{meth}_{runnum}'
subjid, sespassqc, runpassqc = zip(*dwi_passed_qc)
methodpassqc = ['dti_15dir_b1000'] * len(dwi_passed_qc)
dwi_fnames = [fname_templ.format(sid=str(s), snum=str(ses), meth=m, runnum=str(r)) for s, ses, m, r in zip(subjid, sespassqc, methodpassqc, runpassqc)]

for dwif in dwi_fnames:
    from os.path import join