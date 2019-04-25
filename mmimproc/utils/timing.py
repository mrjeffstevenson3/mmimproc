from __future__ import print_function
import os, time, sys, datetime


def waitForFiles(files, interval=3):
    """ Simple function to delay until certain files have been created.

    Args:
        files (list): List of files to look for.
        interval (int): Number of seconds to wait in between checks/polls.
    """
    msg = 'Waiting for {0} out of {1} files at {2}'
    oldnfilesdone = -1
    while True:
        nfilesdone = 0
        for f in files:
            if os.path.isfile(f):
                nfilesdone += 1
        if nfilesdone > oldnfilesdone:
            now = datetime.datetime.now().replace(microsecond=0)
            print( msg.format(len(files)-nfilesdone, len(files), now) )
            oldnfilesdone = nfilesdone
        if nfilesdone == len(files):
            break
        time.sleep(interval)

