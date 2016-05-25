from pylabs.alignment.ants_reg import subj2templ_applywarp as reg2templ
from pylabs.utils.paths import getlocaldataroot, getnetworkdataroot
import niprov
prov = niprov.Context()
prov.dryrun = True
prov.verbose = True
convert = False
#fs = getnetworkdataroot()
fs = getlocaldataroot()
project = 'roots_of_empathy'
sub_nmbrs = [28, 29, 30, 37, 53, 65]
diff_mods = ['FA', 'RA', 'MD']
subjname_templ = 'sub-2013-C0{sub_nmbr}'
diff_fname_templ = '{subj_name}_nomo_mf_{diff_mod}.nii.gz'
sub_names = [str(subjname_templ).format(sub_nmbr=x) for x in sub_nmbrs]
warpfname1_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200Warp.nii.gz'
affinefname_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200Affine.txt'
reffname_templ = 'T1we_susanthr200{subj_name}_ses-{ses}_wemempr_{run}_rms_b1corr_brain_susan200deformed.nii.gz'

if convert:
    niftiDict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    niftiDict, niftiDF = conv_subjs(project, subjects, niftiDict)
else:
    with open(join(fs, project, 'niftiDict_all_subj_201605181335.pickle'), 'rb') as f:
        niftiDict = cPickle.load(f)


for subj in sub_names:


