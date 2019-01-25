import pylabs
pylabs.datadir.target = 'jaba'
from pylabs.utils import *
from pylabs.io.images import savenii
from pylabs.fmap_correction.b1_map_corr import calcb1map
from pylabs.conversion.brain_convert import img_conv
from scipy.ndimage.filters import median_filter as medianf
from pylabs.projects.acdc.file_names import merge_ftempl_dicts

# subject specific info
picks = {'patch': True,
         'project': 'acdc',
         'subj': 'sub-acdc112',
         'session': 'ses-1',
         'run': '1',
         # must set fas mannually when patch used. not reported in PAR file correctly.
         'fas': [4.0, 25.0],}

ses_dir = fs/'{project}/{subj}/{session}'.format(**picks)
qt1_dir = ses_dir/'qt1'
b1map_dir = ses_dir/'fmap'
#get conversion info
picks['vfa_fn_templ'] = img_conv[picks['project']]['_VFA_FA4-25_']['fname_template']
picks['b1map_fn_templ'] = img_conv[picks['project']]['_B1MAP-QUIET_']['fname_template']
with pd.HDFStore(str(fs/'{project}/all_{project}_info.h5'.format(**picks))) as store:
    subjDF = store.select('/{subj}/{session}/convert_info'.format(**picks))
    store.close()
# get b1map TRs
picks['b1map_TRs'] = np.fromstring(subjDF.loc[('fmap', str(removesuffix(picks['b1map_fn_templ'].format(**merge_ftempl_dicts(dict1=picks, dict2=img_conv[picks['project']]['_B1MAP-QUIET_']))))), 'tr'].translate(None,'[]'), sep=' ')
# get info and data
picks['vfa_tr'] = np.fromstring(subjDF.xs('qt1', level=0).iloc[0, subjDF.columns.get_loc('tr')].translate(None,'[]'), sep=' ')
picks['vfa_fn'] = picks['vfa_fn_templ'].format(**merge_ftempl_dicts(dict1=picks, dict2={'scan_name': 'vfa', 'tr': str(picks['vfa_tr'][0]).replace('.', 'p')}))
picks['b1map_fn'] = picks['b1map_fn_templ'].format(**merge_ftempl_dicts(dict1=picks, dict2=img_conv[picks['project']]['_B1MAP-QUIET_']))
vfa_affine = nib.load(picks['vfa_fn']).affine
b1_data = nib.load(str(b1map_dir/picks['b1map_fn'])).get_data()
vfa_data = nib.load(str(qt1_dir/picks['vfa_fn'])).get_data()

# calc b1map
S1 = medianf(b1_data[:,:,:,0], size=7)
S2 = medianf(b1_data[:,:,:,1], size=7)
b1map = calcb1map(S1, S2, picks['b1map_TRs'])
b1map_out_fname = b1map_dir/'{subj}_{session}_b1map_phase_mf.nii'.format(**picks)
savenii(b1map, vfa_affine, str(b1map_out_fname))
