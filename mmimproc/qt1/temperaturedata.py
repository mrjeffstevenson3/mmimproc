from os.path import join
import glob, datetime
from datetime import datetime
import numpy


class TemperatureRecord(object):

    def __init__(self, cols):
        self.valid = False
        self.date = None
        self.temps = []
        for c, strval in enumerate(cols):
            if strval == '':
                continue
            if c == 0:
                self.date = datetime.strptime(strval, '%m/%d/%Y').date()
            elif c in [2, 4]:
                self.temps.append(float(strval))
        if self.date and (len(self.temps) > 0):
            self.valid = True

    def averageTemperature(self):
        return sum(self.temps)/len(self.temps)


def getSessionRecords(scanner):
    from mmimproc.utils import mmimproc_datadir
    fpath = mmimproc_datadir/'T1_phantom_temperature_readings_inventory_{0}.csv'.format(scanner)
    with open(str(fpath)) as tempfile:
        lines = tempfile.readlines()
    sessions = {}
    for line in lines[1:]:
        record = TemperatureRecord(line.split(','))
        if record.valid:
            sessions[record.date] = record
    return sessions

if __name__ == '__main__':
    sessions = getSessionRecords()

