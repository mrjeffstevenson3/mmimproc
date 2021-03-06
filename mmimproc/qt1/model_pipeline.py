import numpy, math, pandas
from mmimproc.utils import mmimproc_datadir

vialsInOrder = range(18,6,-1)

def calculate_model(scanner):
    ## read in constants (concentrations per vial etc)
    concentrationsFile_name = 'T1_phantom_vials_percGel_gdEDTA_concentrations.csv'
    concentrationsFile = mmimproc_datadir/concentrationsFile_name
    concentrations = numpy.loadtxt(str(concentrationsFile))

    ## read in temperature values by session
    from mmimproc.qt1.temperaturedata import getSessionRecords
    sessions = getSessionRecords(scanner)

    ## calculate expected T1 by vial and session
    from mmimproc.qt1.model import expectedT1

    expected = numpy.zeros((len(sessions), 12)) # dates * vials
    expectedByDate = {}
    for d, date in enumerate(sessions.keys()):
        tempCelcius = sessions[date].averageTemperature()
        T = tempCelcius + 273.15
        expectedByDate[date] = []
        for v, vialno in enumerate(vialsInOrder):
            expected[d, v] = expectedT1(T=T,
                gel=concentrations[vialno-1,1],
                gado=concentrations[vialno-1,2])
            expectedByDate[date].append(expected[d, v])

    ## Save by date to tab-separated values file
    expectedT1filepath = mmimproc_datadir/'expectedT1_by_session_and_vial_{0}.tsv'.format(scanner)
    with open(str(expectedT1filepath), 'w') as expectedT1file:
        expectedT1file.write('\t{0}\n'.format('\t'.join(
            [str(vialno) for vialno in vialsInOrder])))
        for d, date in enumerate(sessions.keys()):
            expectedT1file.write('{0}\t{1}\n'.format(date, '\t'.join(
                [str(t1) for t1 in expected[d, :]])))
    return expectedByDate

def modelForDate(targetdate, scanner):
    expectedByDate = calculate_model(scanner)
    expectedByDate[targetdate]
    labels = [str(v) for v in vialsInOrder]
    return pandas.Series(expectedByDate[targetdate], index=labels)

def hasRecordForDate(targetdate, scanner):
    expectedByDate = calculate_model(scanner)
    return targetdate in expectedByDate
