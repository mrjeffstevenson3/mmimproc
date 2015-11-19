import numpy, math

def expectedT1(T, gel, gado):

    ## T                        # $Conditions.B1
    ## gel = concentrations[0,1]   # $Conditions.B4
    ## gado = concentrations[0,2]    # $Conditions.B5

    B0 = 3.0                        # $Conditions.B2
    Frequency = 42.57 * T            # Mhz  $Conditions.G1

    TAUC = 0.0000000000232 * math.exp(4683.7/T) # $Constants.B9 or D9

    (T1GAD, T2GAD, WI) = gadolinium(T, B0, gado)   # $Gado.E20 and $Gado.E21
    (T1B, T2B) = speciesBC(T, TAUC, WI, 'B') # $'Species B'.B57 & $'Species B'.B58
    (T1C, T2C) = speciesBC(T, TAUC, WI, 'C') # $'Species C'.B55 & $'Species C'.B56


    T1GEL = 0.52/(0.37/T1B + 0.15/(T1C + TAUC))
    T2GEL = 0.52/(0.37/T2B + 0.15/(T2C + TAUC))
    PWAT = 100 - (1.34976 * gel)
    PTOT = 100 - (0.888 * gel)
    T1FIN = 1000*PTOT / (PWAT/T1GAD + 0.46176 * gel/T1GEL)
    T2FIN = 1000*PTOT / (PWAT/T2GAD + 0.46176 * gel/T2GEL)

    return T1FIN

def speciesBC(T, TAUC, WI, species):
    EXP = numpy.exp

    ## WI                           # Gado.B17

    ## From Constants sheet, B4-12
    if species == 'B':
        TM1 = 0.0000000000000166*EXP(2942.9/ T)  # BD4
        A = 0.95                               # BD5
        TM2 = 0.000000000261*EXP(2171/ T)        # BD6
        B = 0.05                                # BD7
    elif species == 'C':
        TM1 = 0.000000000000639*EXP(2677.3/ T)   # BD4
        A = 0.45                               # BD5
        TM2 = 0.000000000000625*EXP(4492.1/ T)   # BD6
        B = 0.55                               # BD7
    else:
        raise ValueError('Unknown Species: '+species)

    ## TAUC                     # BD9
    C1 = 8.00E+09               # BD10
    C2  = 8.00E+09              # BD11
    BETA = 1.7                  # BD12

    J = 1 #range(1,50)                              # C1

    EZ = EXP(-6.907+0.27631*(J-1))                  # C2
    TM1EZ = EZ * TM1                                # C3
    TM2EZ = EZ * TM2                                # C4

    T1distA  = TM1EZ/(1+(TM1EZ* WI)**2)
    T1distB  = 4*TM1EZ/(1+(2*TM1EZ*WI)**2)
    T2distA  = 3*TM1EZ
    T2distB  = 5*TM1EZ/(1+(TM1EZ* WI)**2)
    T2distC  = 2*TM1EZ/(1+(2*TM1EZ* WI)**2)

    T1distA2  = TM2EZ/(1+(TM2EZ* WI)**2)
    T1distB2  = 4*TM2EZ/(1+(2*TM2EZ* WI)**2)
    T2distA2  = 3*TM2EZ
    T2distB2  = 5*TM2EZ/(1+(TM2EZ* WI)**2)
    T2distC2  = 2*TM2EZ/(1+(2*TM2EZ* WI)**2)

    PT1  = 0.27631*A*EXP(-(((-6.9077+0.27631*(J-1))/BETA)**2))/(1.77245*BETA)
    PT2  = 0.27631*B*EXP(-(((-6.9077+0.27631*(J-1))/BETA)**2))/(1.77245*BETA)
    PTOT1 = PT1*C1*(T1distA+T1distB)         +PT2*C2*(T1distA2+T1distB2)
    PTOT2 = PT1*C1*(T2distA+T2distB+T2distC) +PT2*C2*(T2distA2+T2distB2+T2distC2)

    Q55 = sum(PTOT1)
    R55 = sum(PTOT2)

    t1 =1/(0.6667*Q55)
    t2 =1/(0.3333*R55)

    return (t1, t2)


def gadolinium(T, B0, nmGado):
    EXP = math.exp
    # $'' is the Conditions sheet
    S = 3.5                                                 #B4
 
    TM =1/(20480000000* T*EXP(((-1503.5/ T)-3.765)))        #B6
    TV =0.000000000000303*EXP(1057.9/ T)                    #B7
    TR =9.68E-015*EXP(2472.5/ T)                            #B8
 
    HCC = 3.40E+04                                          #B10
    Q = 4.7                                                 #B11
    AA = 370000000000000*EXP(150.83/ T)                     #B12
    T10 = 7210*EXP(-2348.3/ T)                              #B13
    T20 = 7210*EXP(-2348.3/ T)*0.9                          #B14
 
    G = 2                                                   #B16
    WI = 2*math.pi*1000000*42.57*B0                         #B17
    WS = WI * 658                                           #B18
 
    ES = TV/(1+(WS*TV)**2)                                  #B20
    ES1 =TV/(1+(2*WS*TV)**2)                                #B21
    TS =1/(2E+020*(ES+4*ES1))                               #B22
    TS2 =1/(1E+020*(3*TV+5*ES+2*ES1))                       #B23

    TE = TS2*TM/(TS+TM)                                     #E4
    TC =TS*TM*TR/(TR*TM+TR*TS+TM*TS)                        #E5
    TOS = 4200000000*nmGado*(3*TC+7*TC/(1+(WS*TC)**2))      #E6
    TE2 =TS2*TM/(TS2+TM)                                    #E7
    TC2 =TS2*TR*TM/(TM*TR+TS2*TR+TS2*TM)                    #E8
    TOS2 =4200000000*nmGado*(3*TC2+7*TC2/(1+(WS*TC2)**2))   #E9
    Z2 =13.1595*S*(1+S)*HCC**2*(TE2+TE2/(1+(WS*TE2)**2))    #E10
    Z =2*13.1595*S*(1+S)*HCC**2*(TE/(1+WS**2*TE**2))        #E11
    S1 =3*TC/(1+TC**2*WI**2)                                #E12
    S2 =7*TC/(1+TC**2*WS**2)                                #E13
    S3 = S1                                                 #E14
    S4 = S2*13/7                                            #E15
    T1M =1/(AA*(S1+S2)+Z)                                   #E16
    T2M =1/(0.5*AA*(4*TC+S4+S5)+Z)                          #E17
    T1P =Q*nmGado/(55500*(T1M+TM))                          #E18
    T2P =Q*nmGado/(55500*(T2M+TM))                          #E19
    T1GAD =1/(T1P+1/T10+TOS)                                #E20
    T2GAD =1/(T2P+1/T20+TOS2)                               #E21

    return (t1g, t2g, WI)


