#!/usr/bin/python 
from pylabs.behavior.conversion import csv2fslmat
csvfile = '/run/user/1000/gvfs/smb-share:domain=WORKGROUP,server=scotty.ilabs.uw.edu,share=js,user=toddr/self_control/hbm_group_data/tbss_19subj/workdir_thr1p5_v3/stats/EF_and_Brain_mar26_2015.csv'
subjects= [
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
csv2fslmat(csvfile, selectSubjects=subjects)
