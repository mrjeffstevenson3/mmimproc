"""
Based on matlab code by Samu Taulu.

"""
import numpy
from os.path import join, isdir
import collections, os
import matplotlib.pyplot as plt
import mne
from mnefun import Params
from mnefun._paths import get_epochs_evokeds_fnames
from picks import fullChpiValidEpochs as pickedSubjects
params = Params()
#params.work_dir = '/home/jasper/data/bbc/meg/'
#params.work_dir = '/diskArray/data/bbc/meg'
params.work_dir = '/media/jasper/PINGS_DRIVE/bbc/meg'
params.subjects = ['bbc_'+str(s) for s in pickedSubjects]
# Those values correspond to real categories as:
params.in_names = ['response', 'tone1', 'tone2cont', 'tone2match',
                                'word1', 'word2cont', 'word2match']
params.analyses = [
    'All',
    'Resp_vs_Aud',
    'Each'
]
params.out_names = [
    ['All'],
    ['Resp','Aud'],
    params.in_names,
]

## Pretend we are in mnefun operation:
p = params
subjects = p.subjects
analyses = p.analyses
conds = params.out_names

## dir
grandavgDir = join(p.work_dir, 'grand')
plotdir = join(p.work_dir, 'evoked_report')
for dirname in (grandavgDir, plotdir):
    if not isdir(dirname):
        os.mkdir(dirname)


## Load all evokeds
anaConds = []
for a in (1, 2):
    for cond in conds[a]:
        anaConds.append((analyses[a], cond))

n = len(subjects)
allEvokeds = {anaCond: dict() for anaCond in anaConds}
for s, subj in enumerate(subjects):
    for ac, analysisCondition in enumerate(anaConds):
        msg = 'Loading evokeds for subject {} of {}, cond {} of {}'
        print(msg.format(s, n, ac, len(anaConds)))
        analysis, condition = analysisCondition
        _, evokedfnames = get_epochs_evokeds_fnames(p, subj, [analysis])
        evokeds = mne.read_evokeds(evokedfnames[0], verbose=False)
        evokeds = [e for e in evokeds if e.kind == 'average']
        evokeds = [e for e in evokeds if e.comment == condition]
        allEvokeds[analysisCondition][subj] = evokeds[0]

## Create grand average files
for ac, analysisCondition in enumerate(anaConds):
    msg = 'Creating grand average for cond {} of {}'
    print(msg.format(ac, len(anaConds)))
    evokedsForAvg = allEvokeds[analysisCondition].values()
    assert len(evokedsForAvg) == n
    avg = mne.grand_average(evokedsForAvg)
    allEvokeds[analysisCondition]['avg'] = avg
    grandavgFilename = join(grandavgDir, '{}_{}{}_{}_n{}-ave.fif'.format(
        analysisCondition[1], p.lp_cut, p.inv_tag, p.eq_tag, n))
    avg.save(grandavgFilename)

## Create grand average files
for ac, analysisCondition in enumerate(anaConds):
    tag = analysisCondition[1]
    with open(join(plotdir, tag+'_evokeds.html'), 'w') as htmlfile:
        htmlfile.write('<html><ol>\n')
        for subj, evoked in allEvokeds[analysisCondition].items():
            fname = subj + '_' + tag + '.png'
            print('Creating '+fname)
            if numpy.isnan(evoked.data.sum()):
                print('Skipping, nans.')
                continue
            evoked.plot_joint(show=False)
            pltpath = join(plotdir, fname)
            plt.savefig(pltpath)
            htmlline = '<li><h2>{}</h2><img src="{}"/></li>\n'
            htmlfile.write(htmlline.format(subj, pltpath))
        htmlfile.write('</ol></html>\n')


"""
## Create grand average files
grandavgDir = join(p.work_dir, 'grand')
if not isdir(grandavgDir):
    os.mkdir(grandavgDir)
for tag, evokeds in subjectEvokeds.items():
    assert len(evokeds) == n
    avg = mne.grand_average(evokeds)
    grandavgFilename = join(grandavgDir, '{}_{}{}_{}_n{}-ave.fif'.format(
                            tag, p.lp_cut, p.inv_tag, p.eq_tag, n))
    avg.save(grandavgFilename)

report = mne.Report() #baseline=_get_baseline(p)
report.parse_folder(data_path=grandavgDir, n_jobs=1, 
                    pattern=['*_n{}-ave.fif'.format(n)])
"""
#report.save('bbc_evoked_report.html', open_browser=False, overwrite=True)
