import numpy, math

## read in constants (concentrations per vial etc)
concentrationsFile = 'data/T1_phantom_vials_percGel_gdEDTA_concentrations.csv'
concentrations = numpy.loadtxt(concentrationsFile)

## read in temperature values by session
from pylabs.qt1.temperaturedata import getSessionRecords
sessions = getSessionRecords()

## calculate expected T1 by vial and session
tempCelcius = sessions.values()[0].averageTemperature()
T = tempCelcius + 273.15
from pylabs.qt1.model import expectedT1
T1 = expectedT1(T=T, gel=concentrations[0,1], gado=concentrations[0,2])

## plot T1 by vial for different temperatures
## plot observed
## For a session, determine correction as a function of observed T1
