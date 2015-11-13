from os.path import join
import glob, datetime
import numpy
import matplotlib.pyplot as plt

def decodeDatetime(rawstr):
    fmt ='%m/%d/%y @ %I:%M%p'
    datetimeStr = rawstr.strip('\t\n').replace('/201','/1')
    return datetime.datetime.strptime(datetimeStr, fmt)

def decodeTemp(rawstr):
    return float(rawstr.strip('\t\n')[:-1])

tempsdir = '/diskArray/data/scs/phantom_temp_readings'
sessions = {}
for fpath in glob.glob(join(tempsdir,'*temp.txt')):
    with open(fpath) as tempfile:
        lines = tempfile.readlines()
    sessionDate = decodeDatetime(lines[3]).date()
    dt1 = decodeDatetime(lines[3])
    T1 = decodeTemp(lines[4])
    dt2 = decodeDatetime(lines[7])
    T2 = decodeTemp(lines[8])
    sessions[sessionDate] = (dt1, T1, dt2, T2)

#temps = numpy.zeros(len(sessions), 2)
for session in sessions.values():
    duration = session[2] - session[0]
    X = [0, duration.total_seconds()]
    Y = [session[1], session[3]]
    plt.plot(X, Y) 


plt.show()
