#!/usr/bin/python 
from mmimproc.correlation.behavior import csv2fslmat
csvfile = '/media/DiskArray/shared_data/js/self_control/behavioral_data/behav_from_andy_march27_2015/EF_and_Brain_july08_2015_Meq0_delta.csv'
subjects= [
317,
328,
332,
334,
335,
347,
353,
364,
371,
376,
379,
381,
384,
385,
396,
]
csv2fslmat(csvfile, selectSubjects=subjects,groupcol=True,covarcols=[42])
