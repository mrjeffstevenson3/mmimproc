import numpy

# read in constants (concentrations per vial etc)
concentrationsFile = 'data/T1_phantom_vials_percGel_gdEDTA_concentrations.csv'
concentrations = numpy.loadtxt(concentrationsFile)

# read in temperature values by session
import temperaturedata
sessions = temperaturedata.getSessionRecords()

# establish model

# calculate expected T1 by vial and session
