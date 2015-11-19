import numpy, math

# read in constants (concentrations per vial etc)
concentrationsFile = 'data/T1_phantom_vials_percGel_gdEDTA_concentrations.csv'
concentrations = numpy.loadtxt(concentrationsFile)

# read in temperature values by session
import pylabs.qt1.temperaturedata
sessions = temperaturedata.getSessionRecords()

# establish model
import pylabs.qt1.model

# calculate expected T1 by vial and session


## plot T1 by vial for different temperatures
## plot observed
## For a session, determine correction as a function of observed T1
