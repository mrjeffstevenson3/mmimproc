from pylabs.qt1.brain_qt1_pipeline_v2 import sort_par_glob, convertParFiles

## Evaluate which flip angles are required to do an adequate SPGR QT1
## based on tadpole phantom 999

fs = getlocaldataroot()
subjectdir = join(fs, 'phantom_qT1_slu/sub-phant20160113')
qt1dir = join(subjectdir, 'anat')

## call phantom_pipeline
## model_pipeline
## fitting_phantoms
## coregister_phantoms
## atlassing (phantoms)

