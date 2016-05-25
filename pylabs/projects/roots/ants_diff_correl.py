from pylabs.alignment.ants_reg import subj2templ_applywarp as reg2templ
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot

import niprov
prov = niprov.Context()
prov.dryrun = True
prov.verbose = True
#fs = getnetworkdataroot()
fs = getlocaldataroot()
project = 'roots_of_empathy'
sub_nmbrs = [28, 29, 30, 37, 53, 65]
subjname_templ = 'sub-2013-C0{sub_nmbr}'
sub_names = [str(subjname_templ).format(sub_nmbr=x) for x in sub_nmbrs]
warpfname1_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200Warp.nii.gz'
affinefname_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200Affine.txt'
reffname_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200deformed.nii.gz'

