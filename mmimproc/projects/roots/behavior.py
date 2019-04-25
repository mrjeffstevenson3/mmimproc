import pandas, numpy
fpath = 'data/behavior/roots_behavior.csv'
data = pandas.read_csv(fpath, index_col=0, usecols=range(8)[1:], na_values='999')
basics = data[0:25]
allvars = data[25:].astype(float)
pre = allvars[allvars.index.str.contains('PRE-')]
post = allvars[allvars.index.str.contains('POST-')]

# Select variables that represent a total of a set of items
varnamesOfTotals = ['P-POST-Child-Behavior-Questionnaire-Surgency',
       'P-POST-Child-Behavior-Questionnaire-Negative-Affect',
       'P-POST-Child-Behavior-Questionnaire-Effortful-Control',
       'P-POST-Child-Behavior-Checklist-Internal-T-score',
       'P-POST-Child-Behavior-Checklist-External-T-score',
       'P-POST-Child-Behavior-Checklist-Total-T-score',
       'R-POST-Mean-Questions-1-6',
       'R-POST-Affect-Knowledge-Test-Sum-of-8-Vignettes',
       'R-POST-N-stickers-given-to-other-child',
       'R-POST-little-helpers-task',
       'R-POST-SE-IAT-Score', 
       'R-POST-Flag-Switch',
       'R-POST-Peabody-Picture-Vocab-Test-Standard-Score',
       'T-POST-SDQ-Prosocial-Scale-Score',
       'T-POST-SDQ-Total-Difficulties-Score',
       'T-POST-Child-Behavior-Scale-Aggression-Scale',
       'T-POST-Child-Behavior-Scale-Prosocial-Scale',
       'T-POST-Emotional-Regulation-Checklist-Lability-Negativity',
       'T-POST-Emotional-Regulation-Checklist-Emotion-Regulation']
posttotalvars = post.loc[varnamesOfTotals]

# Get rid of variables with nans
varmaskWithoutNans = posttotalvars.notnull().all(axis=1)
postWithoutNans = posttotalvars[varmaskWithoutNans]

selectedvars = postWithoutNans

# pandas.set_option('display.large_repr', 'truncate')
# pandas.set_option('display.max_columns', 0)




