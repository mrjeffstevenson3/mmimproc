import datetime

expectedT1filepath = 'data/expectedT1_by_session_and_vial.tsv'


def readfromfile():
    data = {}
    with open(expectedT1filepath, 'r') as expectedT1file:
        lines = expectedT1file.readlines()
        for line in lines[1:]:
            cols = line.split()
            date = datetime.datetime.strptime(cols[0],'%Y-%m-%d').date()
            linedata = list(reversed([float(c) for c in cols[1:]]))
            data[date] = linedata
    return data
