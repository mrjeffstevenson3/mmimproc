from os.path import join
import glob, datetime
from datetime import datetime
import numpy
fpath = 'data/T1_phantom_temperature_readings_inventory.csv'

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
        if self.date and (len(self.temps) > 1):
            self.valid = True

    def averageTemperature(self):
        return sum(self.temps)/len(self.temps)


def getSessionRecords():
    with open(fpath) as tempfile:
        lines = tempfile.readlines()
    sessions = {}
    for line in lines[1:]:
        record = TemperatureRecord(line.split(','))
        if record.valid:
            sessions[record.date] = record
    return sessions

if __name__ == '__main__':
    sessions = getSessionRecords()

