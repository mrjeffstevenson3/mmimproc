from __future__ import division
import glob, pandas
from os.path import join, basename

sessCols = ['Subject', 'Session', 'SessionDate', 'SessionTime', 'Group']
trialCols = [ 'Block', 'Trial', 'PictureTargetOn.ACC', 'PictureTargetOn.CRESP', 
    'PictureTargetOn.RT', 'Running[Trial]', 'word1', 'word2']
cols = ['sub', 'mod', 'sess', 'ntrials', 'nhits', 'acc', 'rt']

datadir = '/home/jasper/mirror/js/bbc/behavior/combined'
#datadir = '/Users/rubi/Data/bbc/behavior/combined'
dirs = glob.glob(join(datadir,'*'))
data = []
for subjectdir in dirs:
    csvs = glob.glob(join(subjectdir,'*.csv'))
    for csv in csvs:
        nameparts = basename(csv).split('_')
        subject, modality, session = basename(csv).split('_')[0:3]
        modality = modality.lower()
        subject = int(subject[3:6])
        print('{} {} {}'.format(subject, modality, session))
        try:
            sessData = pandas.read_csv(csv, usecols=sessCols)
            trialData = pandas.read_csv(csv) #, usecols=trialCols
        except ValueError as exc:
            print('Could not read csv.')
            continue
        if len(trialData.columns) < 20:
            print('Missing columns.')
            continue
        sessData = sessData.loc[0]
        trialData = trialData.dropna(axis=0, how='all')
        if modality == 'fmri':
            accColumnPrefix = 'text2'
        if modality == 'meg':
            accColumnPrefix = 'word2'
        task = trialData['Running[Trial]'].astype(str) == 'OnList'
        ntrials = task.sum()
        targets = trialData['CorrectAnswer'].astype(str) == 'r'
        response = trialData[accColumnPrefix+'.RESP'].notnull()
        accurate = targets == response
        hits = task & targets & response
        nhits = hits.sum()
        accuracy = (accurate & task).sum() / task.sum()
        hitrt = trialData.loc[hits][accColumnPrefix+'.RT'].mean()
        data.append((subject, modality, session, ntrials, nhits, accuracy, hitrt))
data = pandas.DataFrame(data, columns=cols)
data.sort_values('sub')
fmri = data[data['mod']=='fmri'].sort_values('sub').round(2)
meg = data[data['mod']=='meg'].sort_values('sub').round(2)
fmri.to_csv('bbc_behav_fmri.csv')
meg.to_csv('bbc_behav_meg.csv')





