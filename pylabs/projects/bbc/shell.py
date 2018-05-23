import os, datetime, subprocess, petname


def tryrun(cmd, logfpath=None, env=None):
    start = datetime.datetime.now()

    if env is None:
        env = os.environ.copy()

    if logfpath is None:
        logfpath = petname.Generate(2,'-')+'.log'

    try:
        with open(logfpath, 'w') as logfile:
            out = subprocess.check_call(cmd,
                env=env, stdout=logfile, stderr=logfile)
    except subprocess.CalledProcessError as err:
        print('    FAILED')
    duration = datetime.datetime.now() - start
    microseconds = datetime.timedelta(microseconds=duration.microseconds)
    duration = duration - microseconds
    print('    '+str(duration))
