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
Frequency = 42.57 * T            # Mhz  $Conditions.G1

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

    ## From Constantys sheet, B4-12

    TM1	=0.0000000000000166*EXP(2942.9/$''.B1)
    A	=0.95
    TM2	=0.000000000261*EXP(2171/$''.B1)
    B	0.05
	
    TAUC	=D9
    C1	8.00E+09
    C2	8.00E+09
    BETA	1.7


    J = range(1,50)

    EZ		=EXP(-6.907+0.27631*(J-1))
    TM1*EZ		=C1*$''.$B$4
    TM2*EZ		=C1*$''.$B$6
    T1distA		=$C4/(1+($C4*$''.$B$17)^2)
    T1distB		=4*$C5/(1+(2*$C5*$''.$B$17)^2)
    T2distA		=3*$C6
    T2distB		=5*$C7/(1+($C7*$''.$B$17)^2)
    T2distC		=2*$C8/(1+(2*$C8*$''.$B$17)^2)
    T1distA2		=C3/(1+(C3*$''.$B$17)^2)
    T1distB2		=4*C3/(1+(2*C3*$''.$B$17)^2)
    T2distA2		=3*C3
    T2distB2		=5*C3/(1+(C3*$''.$B$17)^2)
    T2distC2		=2*C3/(1+(2*C3*$''.$B$17)^2)
    PT1		=0.27631*$''.$B$5*EXP(-(((-6.9077+0.27631*($A14-1))/$''.$B$12)^2))/(1.77245*$''.$B$12)
    PT2		=0.27631*$''.$B$7*EXP(-(((-6.9077+0.27631*($A15-1))/$''.$B$12)^2))/(1.77245*$''.$B$12)
    PTOT1		=C14*$''.$B$10*(C4+C5)+C15*$''.$B$11*(C9+C10)
    PTOT2		=C14*$''.$B$10*(C6+C7+C8)+C15*$''.$B$11*(C11+C12+C13)

    Q55 = sum(PTOT1)
    R55 = sum(PTOT2)

    T1B	=1/(0.6667*Q55)
    T2B	=1/(0.3333*R55)

    return (t1b, t2b)

def speciesC():
    ## From Constantys sheet, D4-12
    TM1	=0.000000000000639*EXP(2677.3/$''.B1)
    A	=0.45
    TM2	=0.000000000000625*EXP(4492.1/$''.B1)
    B	=0.55
			
    TAUC	=D9		=0.0000000000232*EXP(4683.7/$''.B1)
    C1	8.00E+09		8.00E+09
    C2	8.00E+09		8.00E+09
    BETA	1.7		1.7

    J = range(1,50)

    EZ		=EXP(-6.907+0.27631*(J-1))
    TM1*EZ		=C2*$''.$D$4
    TM2*EZ		=C2*$''.$D$6
    T1distA		=$C5/(1+($C5*$''.$B$17)^2)
    T1distB		=4*$C6/(1+(2*$C6*$''.$B$17)^2)
    T2distA		=3*$C7
    T2distB		=5*$C8/(1+($C8*$''.$B$17)^2)
    T2distC		=2*$C9/(1+(2*$C9*$''.$B$17)^2)
    T1distA2		=C4/(1+(C4*$''.$B$17)^2)
    T1distB2		=4*C4/(1+(2*C4*$''.$B$17)^2)
    T2distA2		=3*C4
    T2distB2		=5*C4/(1+(C4*$''.$B$17)^2)
    T2distC2		=2*C4/(1+(2*C4*$''.$B$17)^2)
    PT1		=0.27631*$''.$D$5*EXP(-(((-6.9077+0.27631*($A15-1))/$''.$D$12)^2))/(1.77245*$''.$D$12)
    PT2		=0.27631*$''.$D$7*EXP(-(((-6.9077+0.27631*($''.$A16-1))/$''.$D$12)^2))/(1.77245*$''.$D$12)
    PTOT1		=C15*$''.$D$10*(C5+C6)+C16*$''.$D$11*(C10+C11)
    PTOT2		=C15*$''.$D$10*(C7+C8+C9)+C16*$''.$D$11*(C12+C13+C14)



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

