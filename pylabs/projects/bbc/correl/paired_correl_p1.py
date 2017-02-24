from pathlib import *
import pandas as pd
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils import run_subprocess, WorkingContext
from pylabs.io.images import savenii
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())

groupcol=True
subj_list = ['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']
#behav_list = [u'PATrhyTotSS', u'PATsegTotSS', u'CTOPPphoaCS', u'CTOPPrnCS', u'CTOPPphomCS', u'PPVTSS', u'TOPELeliSS', u'STIMQ-PSDSscaleScore1-to-15-SUM', u'self-esteem-IAT']
behav_list = [(u'21', u'PATrhyTotSS') , (u'22', u'PATsegTotSS') , (u'23', u'CTOPPphoaCS')  ,(u'24', u'CTOPPrnCS') ,(u'25', u'CTOPPphomCS'), (u'26', u'PPVTSS'), (u'27', u'TOPELeliSS') ,(u'28', u'STIMQ-PSDSscaleScore1-to-15-SUM'), (u'29', u'self-esteem-IAT')]
csvraw = fs / 'bbc' / 'behavior' / 'bbc_behav_2-22-2017_rawsub.csv'
outdir = fs / 'bbc' / 'stats' / 'matfiles'
data = pd.read_csv(str(csvraw), header=[0,1], index_col=1, tupleize_cols=True)
sub_data = data.tail(len(subj_list))[behav_list]

if not outdir.is_dir:
    outdir.mkdir(parents=True)

for behav in sub_data.iteritems():
    content = ''
    (w, p) = (2, len(behav[1]))
    content += '/NumWaves\t{0}\n/NumPoints\t{1}\n'.format(w, p)
    content += '/PPheights\t\t{0:.6e} {1:.6e}\n'.format(
        sub_data[behav[0]].min(), sub_data[behav[0]].max())
    content += '/Matrix\n'
    for vals in behav[1]:
        if groupcol:
            content +=  '1 {0:.6e}\n'.format(vals)
    content += '\n'
    matfname =  outdir / 'c{0}b{1}s{2}{3}_{4}.mat'.format(
        '2', behav[0][0].zfill(2), str(len(behav[1])).zfill(2), 's', behav[0][1])
    with open(str(matfname), mode='w') as matfile:
        matfile.write(content)

