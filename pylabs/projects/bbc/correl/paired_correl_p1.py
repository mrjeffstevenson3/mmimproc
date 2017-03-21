# this script generates the subtracted and unsubtracted fsl mat files for group and correlation stats
from pathlib import *
import pandas as pd
import numpy as np
from pylabs.utils.paths import getnetworkdataroot
from pylabs.utils.provenance import ProvenanceWrapper
provenance = ProvenanceWrapper()
fs = Path(getnetworkdataroot())

groupcol=True
subj_list = ['209-101', '211-105', '208-106', '202-108', '249-113', '241-116', '243-118', '231-119', '253-120']
unsub_subj_list = ['BBC209', 'BBC101', 'BBC211', 'BBC105', 'BBC208', 'BBC106', 'BBC202', 'BBC108', 'BBC249', 'BBC113', 'BBC241',
                   'BBC116', 'BBC243', 'BBC118', 'BBC231', 'BBC119', 'BBC253', 'BBC120']
behav_list = [(u'21', u'PATrhyTotSS') , (u'22', u'PATsegTotSS') , (u'23', u'CTOPPphoaCS')  ,(u'24', u'CTOPPrnCS') ,(u'25', u'CTOPPphomCS'), (u'26', u'PPVTSS'), (u'27', u'TOPELeliSS') ,(u'28', u'STIMQ-PSDSscaleScore1-to-15-SUM'), (u'29', u'self-esteem-IAT')]
csvraw = fs / 'bbc' / 'behavior' / 'bbc_behav_2-22-2017_rawsub.csv'
outdir = fs / 'bbc' / 'stats' / 'matfiles'
data = pd.read_csv(str(csvraw), header=[0,1], index_col=1, tupleize_cols=True)
sub_data = data.tail(len(subj_list))[behav_list]
unsub_data = data.loc[unsub_subj_list, behav_list]

if not outdir.is_dir:
    outdir.mkdir(parents=True)
#make subtracted mat files with behavior correlation
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
# make unsubtracted mat files
for behav in unsub_data.iteritems():
    if len(behav[1]) % 2 != 0:
        raise ValueError('paired behavior list is not even. aborting.')
    unsub_content = ''
    num_waves = (len(behav[1]) / 2) + 2 if groupcol else (len(behav[1]) / 2) + 1
    num_pnts = len(behav[1])
    unsub_content += '/NumWaves\t{0}\n/NumPoints\t{1}\n'.format(num_waves, num_pnts)
    heights = ['{0:6e}\t'.format(0)] * (len(behav[1]) / 2)
    unsub_content += '/PPheights\t\t{0:.6e} {1:.6e}\n'.format(
        unsub_data[behav[0]].min(), unsub_data[behav[0]].max())
    unsub_content += '/Matrix\n'
    counter = 0
    for i, vals in enumerate(behav[1]):
        cols = ['{0:6e}\t'.format(0)] * (len(behav[1]) / 2)
        cols[int(counter)] = '{0:6e}\t'.format(1)
        if groupcol:
            if i % 2 == 0:
                unsub_content +=  '1\t'+''.join(cols)+'{0:.6e}\n'.format(vals)
            else:
                unsub_content += '-1\t'+''.join(cols)+'{0:.6e}\n'.format(vals)
        else:
            unsub_content += ''.join(cols)+'{0:.6e}\n'.format(vals)
        counter += 0.5
    unsub_content += '\n'
    matfname =  outdir / 'c{0}b{1}s{2}{3}_{4}.mat'.format(num_waves,
         behav[0][0].zfill(2), str(num_pnts).zfill(2), 'p', behav[0][1])
    with open(str(matfname), mode='w') as matfile:
        matfile.write(unsub_content)
# make con files first for subtracted data the unsubtracted
subconfname = outdir / 'subtracted_pairs_correl_c{0}.con'.format(2 if groupcol else 1)
subcon_content = ''
subcon_content += '/ContrastName1\tsubtracted pairs controls gt foster\n'
subcon_content += '/ContrastName2\tsubtracted pairs foster gt controls\n'
subcon_content += '/NumWaves\t{0}\n/NumContrasts\t{1}\n'.format(2,2)
subcon_content += '/PPheights\t{0:.6e}\t{1:.6e}\n'.format(0,1)
subcon_content += '/RequiredEffect\t{0:.6e}\t{1:.6e}\n'.format(0,40)
subcon_content += '/Matrix\n\n'
subcon_content += '{0:.6e}\t{1:.6e}\n'.format(1,0)
subcon_content += '{0:.6e}\t{1:.6e}\n'.format(-1,0)
with open(str(subconfname), mode='w') as subconfile:
    subconfile.write(subcon_content)
# con file for unsubtracted correlations
unsubconfname = outdir / 'paired_correl_exch_blks_c{0}.con'.format((len(unsub_data.iloc[:,0])/2)+2 if groupcol else (len(unsub_data.iloc[:,0])/2)+1)
unsubcon_content = ''
unsubcon_content += '/ContrastName1\tsubtracted pairs controls gt foster\n'
unsubcon_content += '/ContrastName2\tsubtracted pairs foster gt controls\n'
unsubcon_content += '/NumWaves\t{0}\n'.format((len(unsub_data.iloc[:,0])/2)+2 if groupcol else (len(unsub_data.iloc[:,0])/2)+1)
unsubcon_content += '/NumContrasts\t{0}\n'.format(2)
unsubcon_content += '/PPheights\t{0:.6e}\t{1:.6e}\n'.format(0,1)
unsubcon_content += '/RequiredEffect\t{0:.6e}\t{1:.6e}\n'.format(0,40)
unsubcon_content += '/Matrix\n\n'
unsub_cols = ['{0:6e}\t'.format(0)] * ((len(unsub_data.iloc[:,0])/2)+1)
unsubcon_content += '{0:.6e}\t{1}\n'.format(1,''.join(unsub_cols))
unsubcon_content += '{0:.6e}\t{1}\n'.format(-1,''.join(unsub_cols))
with open(str(unsubconfname), mode='w') as unsubconfile:
    unsubconfile.write(unsubcon_content)
# make exchangeability block grp file
exchblk_fname = outdir / 'paired_exch_blks_c{0}.grp'.format(1)
exchblk_content = ''
exchblk_content += '/NumWaves\t{0}\n'.format(1)
exchblk_content += '/NumPoints\t{0}\n'.format(len(unsub_data.iloc[:,0]))
exchblk_content += '/PPheights\t{0}\n'.format(len(unsub_data.iloc[:,0])/2)
exchblk_content += '/Matrix\n\n'
for x in np.arange(1,len(unsub_data.iloc[:,0])/2+1, 0.5).astype(int):
    exchblk_content += '{0}\n'.format(x)
with open(str(exchblk_fname), mode='w') as exchblkfile:
    exchblkfile.write(exchblk_content)
