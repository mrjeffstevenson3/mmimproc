from datetime import datetime

def pr_examdate2pydatetime(pr_examdate):
    pr_datefmat = '%Y.%m.%d / %H:%M:%S'
    return datetime.strptime(pr_examdate, pr_datefmat)

def pr_examdate2BIDSdatetime(pr_examdate):
    pr_datefmat = '%Y.%m.%d / %H:%M:%S'
    py_datefmat = datetime.strptime(pr_examdate, pr_datefmat)
    BIDS_datefmat = '%Y-%m-%dT%H:%M:%S'
    return datetime.strftime(py_datefmat, BIDS_datefmat)
