from datetime import datetime

def pr_examdate2pydatetime(pr_examdate):
    pr_datefmat = '%Y.%m.%d / %H:%M:%S'
    return datetime.strptime(pr_examdate, pr_datefmat)

def pr_examdate2BIDSdatetime(pr_examdate):
    pr_datefmat = '%Y.%m.%d / %H:%M:%S'
    py_datefmat = datetime.strptime(pr_examdate, pr_datefmat)
    BIDS_datefmat = '%Y-%m-%dT%H:%M:%S'
    return datetime.strftime(py_datefmat, BIDS_datefmat)

def pr_date(pr_examdate):
    pr_datefmat = '%Y.%m.%d / %H:%M:%S'
    py_datefmat = datetime.strptime(pr_examdate, pr_datefmat)
    return datetime.date(py_datefmat)

def matchscandate(testdate, niftiDict, outkey, midkey):
    match = False
    if niftiDict.has_key(outkey):
        if niftiDict[outkey].has_key(midkey):
            if niftiDict[outkey][midkey]['exam_date'] == testdate:
                match =True
    return match