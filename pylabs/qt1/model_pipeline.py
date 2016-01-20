import numpy, math

def calculate_model(scanner):
    ## read in constants (concentrations per vial etc)
    concentrationsFile = 'data/T1_phantom_vials_percGel_gdEDTA_concentrations.csv'
    concentrations = numpy.loadtxt(concentrationsFile)

    ## read in temperature values by session
    from pylabs.qt1.temperaturedata import getSessionRecords
    sessions = getSessionRecords(scanner)

    ## calculate expected T1 by vial and session
    from pylabs.qt1.model import expectedT1
    vialsInOrder = range(18,6,-1)
    expected = numpy.zeros((len(sessions), 12)) # dates * vials
    for d, date in enumerate(sessions.keys()):
        tempCelcius = sessions[date].averageTemperature()
        T = tempCelcius + 273.15
        for v, vialno in enumerate(vialsInOrder):
            expected[d, v] = expectedT1(T=T,
                gel=concentrations[vialno-1,1],
                gado=concentrations[vialno-1,2])

    ## Save by date to tab-separated values file
    expectedT1filepath = 'data/expectedT1_by_session_and_vial_{0}.tsv'.format(scanner)
    with open(expectedT1filepath, 'w') as expectedT1file:
        expectedT1file.write('\t{0}\n'.format('\t'.join(
            [str(vialno) for vialno in vialsInOrder])))
        for d, date in enumerate(sessions.keys()):
            expectedT1file.write('{0}\t{1}\n'.format(date, '\t'.join(
                [str(t1) for t1 in expected[d, :]])))
    return expected
