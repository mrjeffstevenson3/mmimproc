import numpy, math

# read in constants (concentrations per vial etc)
concentrationsFile = 'data/T1_phantom_vials_percGel_gdEDTA_concentrations.csv'
concentrations = numpy.loadtxt(concentrationsFile)

# read in temperature values by session
import temperaturedata
sessions = temperaturedata.getSessionRecords()

# establish model

# calculate expected T1 by vial and session



T = tempCelcius + 273.15        # $Conditions.B1
B0 = 3.0                        # $Conditions.B2

tempCelcius = sessions.values()[0].averageTemperature()
percGel = concentrations[0,1]   # $Conditions.B4
nmGado = concentrations[0,2]    # $Conditions.B5

TAUC = 0.0000000000232 * math.exp(4683.7/T) # $Constants.B9 or D9

# $'Species C'.B55 # This whole table is dependent on T. I guess I could replicate it with J as an array.
# $'Species C'.B56
# $'Species B'.B57
# $'Species B'.B58

# $Gado.E20
# $Gado.E21

T1GEL = 0.52/(0.37/$'Species B'.B57+0.15/($'Species C'.B55 + TAUC))
T2GEL = 0.52/(0.37/$'Species B'.B58+0.15/($'Species C'.B56 + TAUC))
PWAT = 100 - (1.34976 * percGel)
PTOT = 100 - (0.888 * percGel)
T1FIN = 1000*PTOT/(PWAT/$Gado.E20+0.46176 * percGel/T1GEL)
T2FIN = 1000*PTOT/(PWAT/$Gado.E21+0.46176 * percGel/T2GEL)

## plot T1 by vial for different temperatures
## plot observed
## For a session, determine correction as a function of observed T1

