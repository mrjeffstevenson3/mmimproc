# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

project = 'nbwr'
orig_dwi = [
    (('999b', 1, 'dwi-topup_6S0', 1), ('999b', 1, 'dwi-topdn_6S0', 1), ('999b', 1,'dwi-topup_64dir-3sh-800-2000', 1)),

    ]
orig_spgr = [
    (('999b', 1, 'spgr_fa-05-tr-15p0', 1), ('999b', 1, 'spgr_fa-15-tr-15p0', 1), ('999b', 1,'spgr_fa-30-tr-15p0', 1), ('999b', 1,'b1map', 1))
    ]
ftempl = 'sub-nbwr{}_ses-{}_{}_{}'
topup_fname = []
topdn_fname = []
dwi_fname = []
for topup, topdn, dwi in orig_dwi:
    topup_fname.append(ftempl.format(*topup))
    topdn_fname.append(ftempl.format(*topdn))
    dwi_fname.append(ftempl.format(*dwi))

spgr_fa5_fname = []
spgr_fa15_fname = []
spgr_fa30_fname = []
b1map_fname = []
for spgr_fa5, spgr_fa15, spgr_fa30, b1map in orig_spgr:
    spgr_fa5_fname.append(ftempl.format(*spgr_fa5))
    spgr_fa15_fname.append(ftempl.format(*spgr_fa15))
    spgr_fa30_fname.append(ftempl.format(*spgr_fa30))
    b1map_fname.append(ftempl.format(*b1map))

