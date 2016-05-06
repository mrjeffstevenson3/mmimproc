import pandas, numpy
fpath = 'data/behavior/roots_behavior.csv'
data = pandas.read_csv(fpath, index_col=0, usecols=range(8)[1:], na_values='999')
basics = data[0:25]
allvars = data[25:].astype(float)
pre = allvars[allvars.index.str.contains('PRE-')]
post = allvars[allvars.index.str.contains('POST-')]
selvarnames = ['R-PRE-little-helpers-task', 'R-PRE-SE-IAT-Score',
               'T-PRE-SDQ-Hyperactivity-Scale-Score',
               'T-PRE-Emotional-Regulation-Checklist-Lability-Negativity',
               'T-PRE-Emotional-Regulation-Checklist-Emotion-Regulation',
               'P-PRE-Child-Behavior-Questionnaire-Surgency',
               'P-PRE-Child-Behavior-Checklist-Total-T-score']
selectedvars = pre.loc[selvarnames].T

