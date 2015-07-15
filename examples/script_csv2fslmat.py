#!/usr/bin/python 
from pylabs.correlation.behavior import csv2fslmat
csvfile = 'EF_and_Brain_july08_2015_Meq0_delta.csv'
vbm17= [
317,
318,
328,
332,
334,
335,
347,
353,
364,
370,
371,
376,
379,
381,
384,
385,
396,
]
tbss19 = [
317, 
322, 
324, 
328, 
332, 
334, 
335, 
341, 
347, 
353, 
364, 
370, 
371, 
376, 
379, 
381, 
384,
385,
396,
]
csv2fslmat(csvfile, selectSubjects=tbss19, cols=[41], demean=True, groupcol=False)
