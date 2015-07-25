from __future__ import print_function
import os, time, sys


def waitForFiles(files):
    while True:
        nfilesdone = 0
        for f in files:
            if os.path.isfile(f):
                nfilesdone += 1
        msg = 'Waiting for {0} out of {1} files.'
        print( msg.format(len(files)-nfilesdone, len(files)))
        if nfilesdone == len(files):
            break
        time.sleep(5)

