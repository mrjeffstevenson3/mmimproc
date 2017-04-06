# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

orig_dwi = [
    (('999b', 1, 'dwi-topup_6S0', 1),('999b', 1, 'dwi-topdn_6S0', 1),('999b', 1,'dwi-topup_64dir-3sh-800-2000', 1)),

    ]