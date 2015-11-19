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

(T1B, T2B) = speciesB()                 # $'Species B'.B57 and $'Species B'.B58
(T1C, T2C) = speciesC()                 # $'Species C'.B55 and $'Species C'.B56
(T1GAD, T2GAD) = gadolinium(T, B0, nmGado)   # $Gado.E20 and $Gado.E21

T1GEL = 0.52/(0.37/T1B + 0.15/(T1C + TAUC))
T2GEL = 0.52/(0.37/T2B + 0.15/(T2C + TAUC))
PWAT = 100 - (1.34976 * percGel)
PTOT = 100 - (0.888 * percGel)
T1FIN = 1000*PTOT / (PWAT/T1GAD + 0.46176 * percGel/T1GEL)
T2FIN = 1000*PTOT / (PWAT/T2GAD + 0.46176 * percGel/T2GEL)

def speciesB():
    return (t1b, t2b)

def speciesC():
    # probably very similar
    return (t1c, t2c)

def gadolinium(T, B0, nmGado):
    # $'' is the Conditions sheet
    S	3.5
	
    TM	=1/(20480000000*$''.B1*EXP(((-1503.5/$''.B1)-3.765)))
    TV	=0.000000000000303*EXP(1057.9/$''.B1)
    TR	=9.68E-015*EXP(2472.5/$''.B1)
	
    HCC	3.40E+04
    Q	4.7
    AA 	=370000000000000*EXP(150.83/$''.B1)
    T10	=7210*EXP(-2348.3/$''.B1)
    T20	=7210*EXP(-2348.3/$''.B1)*0.9
	
    G	2
    WI	=2*PI()*1000000*42.57*$''.B2
    WS	=B17*658
	
    ES	=B7/(1+(B18*B7)^2)
    ES1	=B7/(1+(2*B18*B7)^2)
    TS	=1/(2E+020*(B20+4*B21))
    TS2	=1/(1E+020*(3*B7+5*B20+2*B21))

    TE	=B23*B6/(B22+B6)
    TC	=B22*B6*B8/(B8*B6+B8*B22+B6*B22)
    TOS	=4200000000*$''.B5*(3*$Gado.E5+7*$Gado.E5/(1+($Gado.B18*$Gado.E5)^2))
    TE2	=B23*B6/(B23+B6)
    TC2	=B23*B8*B6/(B6*B8+B23*B8+B23*B6)
    TOS2	=4200000000*$''.B5*(3*$Gado.E8+7*$Gado.E8/(1+($Gado.B18*$Gado.E8)^2))
    Z2	=13.1595*B4*(1+B4)*B10^2*(E7+E7/(1+(B18*E7)^2))
    Z	=2*13.1595*B4*(1+B4)*B10^2*(E4/(1+B18^2*E4^2))
    S1	=3*E5/(1+E5^2*B17^2)
    S2	=7*E5/(1+E5^2*B18^2)
    S3	=E12
    S4	=E13*13/7
    T1M	=1/(B12*(E12+E13)+E11)
    T2M	=1/(0.5*B12*(4*E5+E14+E15)+E11)
    T1P	=B11*$''.B5/(55500*($Gado.E16+$Gado.B6))
    T2P	=B11*$''.B5/(55500*($Gado.E17+$Gado.B6))
    T1GAD	=1/(E18+1/B13+E6)
    T2GAD	=1/(E19+1/B14+E9)

    return (t1g, t2g)

## plot T1 by vial for different temperatures
## plot observed
## For a session, determine correction as a function of observed T1

