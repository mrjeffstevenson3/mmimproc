from pylabs.qt1.brain_qt1_pipeline_v2 import sort_par_glob, convertParFiles

fs = getlocaldataroot()
datadir = join(fs, 'tadpole/tadpole_999')
subjSPGRparfiles = glob(pathjoin(datadir, 'source_parrec/*T1_MAP*.PAR'))
subjSPGRparfiles = sort_par_glob(subjSPGRparfiles)
niioutdir = pathjoin(datadir, 'source_nii')
convertParFiles(subjSPGRparfiles, niioutdir)
