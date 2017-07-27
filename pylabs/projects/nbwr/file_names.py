# orig_dwi are the original dwi source files output from conversion -> inputs to topup
# set as a triple tuple (topup_dwi_6S0 6 vol S0 1st, topdn_dwi_6S0 6 vol S0 2nd, dwi-topup_64dir-3sh-800-2000 multishell 64 dir dwi 3rd)
# topup_dwi_6S0 and topdn_dwi_6S0 are inputs to topup along with dwell time
# topup_unwarped is the output from topup and input to eddy

# class object to pass list of subject ids
class SubjIdPicks(object):
    pass

project = 'nbwr'
ftempl = 'sub-nbwr{}_ses-{}_{}_{}'
# freesurfer, VBM, T2 file name lists
vbm_fnames = []
freesurf_fnames = []
t2_fnames = []
# dwi file name lists
topup_fnames = []
topdn_fnames= []
dwi_fnames = []
# 3 flip qT1 file name lists
spgr_fa5_fnames = []
spgr_fa15_fnames = []
spgr_fa30_fnames = []
b1map_fnames = []
# 5 flip qT1 file name lists
spgr5_fa5_fnames = []
spgr5_fa10_fnames = []
spgr5_fa15_fnames = []
spgr5_fa20_fnames = []
spgr5_fa30_fnames = []
b1map5_fnames = []

vbm_rms = [
    ('998', 1, 'vbmmempr_ti850_rms', 1),
    ]
freesurf_rms = [
    ('999b', 1, 'vbmmempr_rms', 1),
    ('998', 1, 'vbmmempr_ti1100_rms', 1),
    ('144', 1, 'fsmempr_ti1100_rms', 1),
    ('401', 1, 'fsmempr_ti1100_rms', 1),
    ('317', 1, 'fsmempr_ti1100_rms', 1),
    ('132', 1, 'fsmempr_ti1100_rms', 1),
        ]

orig_dwi = [
    (('999b', 1, 'dwi-topup_6S0', 1), ('999b', 1, 'dwi-topdn_6S0', 1), ('999b', 1,'dwi-topup_64dir-3sh-800-2000', 1)),
    (('998', 1, 'dwi-topup_6S0', 1), ('998', 1, 'dwi-topdn_6S0', 1), ('998', 1,'dwi-topup_64dir-3sh-800-2000', 1)),
    (('144', 1, 'dwi-topup_6S0', 1), ('144', 1, 'dwi-topdn_6S0', 1), ('144', 1,'dwi-topup_64dir-3sh-800-2000', 1)),
    (('401', 1, 'dwi-topup_6S0', 1), ('401', 1, 'dwi-topdn_6S0', 1), ('401', 1,'dwi-topup_64dir-3sh-800-2000', 1)),
    (('317', 1, 'dwi-topup_6S0', 1), ('317', 1, 'dwi-topdn_6S0', 1), ('317', 1,'dwi-topup_64dir-3sh-800-2000', 1)),
    (('132', 1, 'dwi-topup_6S0', 1), ('132', 1, 'dwi-topdn_6S0', 1), ('132', 1,'dwi-topup_64dir-3sh-800-2000', 1)),
    ]
orig_spgr = [
    (('999b', 1, 'spgr_fa-05-tr-15p0', 1), ('999b', 1, 'spgr_fa-15-tr-15p0', 1), ('999b', 1,'spgr_fa-30-tr-15p0', 1), ('999b', 1,'b1map', 1)),
    (('998', 1, 'spgr_fa-05-tr-12p0', 1), ('998', 1, 'spgr_fa-15-tr-12p0', 1), ('998', 1, 'spgr_fa-30-tr-12p0', 1), ('998', 1, 'b1map', 1)),
    (('144', 1, 'spgr_fa-05-tr-12p0', 1), ('144', 1, 'spgr_fa-15-tr-12p0', 1), ('144', 1, 'spgr_fa-30-tr-12p0', 1), ('144', 1, 'b1map', 1)),
    (('401', 1, 'spgr_fa-05-tr-12p0', 1), ('401', 1, 'spgr_fa-15-tr-12p0', 1), ('401', 1, 'spgr_fa-30-tr-12p0', 1), ('401', 1, 'b1map', 1)),
    (('317', 1, 'spgr_fa-05-tr-12p0', 1), ('317', 1, 'spgr_fa-15-tr-12p0', 1), ('317', 1, 'spgr_fa-30-tr-12p0', 1), ('317', 1, 'b1map', 1)),
    (('132', 1, 'spgr_fa-05-tr-12p0', 1), ('132', 1, 'spgr_fa-15-tr-12p0', 1), ('132', 1, 'spgr_fa-30-tr-12p0', 1), ('132', 1, 'b1map', 1)),
    ]
orig_5spgr = [
    (('998', 1, 'spgr_fa-05-tr-12p0', 1), ('998', 1, 'spgr_fa-10-tr-12p0', 1), ('998', 1, 'spgr_fa-15-tr-12p0', 1), ('998', 1, 'spgr_fa-20-tr-12p0', 1), ('998', 1,'spgr_fa-30-tr-12p0', 1), ('998', 1,'b1map', 1)),
    (('144', 1, 'spgr_fa-05-tr-12p0', 1), ('144', 1, 'spgr_fa-10-tr-12p0', 1), ('144', 1, 'spgr_fa-15-tr-12p0', 1), ('144', 1, 'spgr_fa-20-tr-12p0', 1), ('144', 1, 'spgr_fa-30-tr-12p0', 1), ('144', 1, 'b1map', 1)),
    (('401', 1, 'spgr_fa-05-tr-12p0', 1), ('401', 1, 'spgr_fa-10-tr-12p0', 1), ('401', 1, 'spgr_fa-15-tr-12p0', 1), ('401', 1, 'spgr_fa-20-tr-12p0', 1), ('401', 1, 'spgr_fa-30-tr-12p0', 1), ('401', 1, 'b1map', 1)),
    (('317', 1, 'spgr_fa-05-tr-12p0', 1), ('317', 1, 'spgr_fa-10-tr-12p0', 1), ('317', 1, 'spgr_fa-15-tr-12p0', 1), ('317', 1, 'spgr_fa-20-tr-12p0', 1), ('317', 1, 'spgr_fa-30-tr-12p0', 1), ('317', 1, 'b1map', 1)),
    (('132', 1, 'spgr_fa-05-tr-12p0', 1), ('132', 1, 'spgr_fa-10-tr-12p0', 1), ('132', 1, 'spgr_fa-15-tr-12p0', 1), ('132', 1, 'spgr_fa-20-tr-12p0', 1), ('132', 1, 'spgr_fa-30-tr-12p0', 1), ('132', 1, 'b1map', 1)),
    ]

orig_b1map = [('999b', 1,'b1map', 1), ('998', 1, 'b1map', 1), ('144', 1, 'b1map', 1),
            ('401', 1, 'b1map', 1),('317', 1, 'b1map', 1),('132', 1, 'b1map', 1),
            ]

orig_t2 = [('999b', 1,'3dt2', 1), ('998', 1, '3dt2', 1), ('144', 1, '3dt2', 1),
            ('401', 1, '3dt2', 1),('317', 1, '3dt2', 1),('132', 1, '3dt2', 1),
            ]

def get_vbm_names(subjids_picks):
    for vbm in vbm_rms:
        if vbm[0] in subjids_picks.subjids:
            vbm_fnames.append(ftempl.format(*vbm))
    return vbm_fnames

def get_freesurf_names(subjids_picks):
    for freesurf in freesurf_rms:
        if freesurf[0] in subjids_picks.subjids:
            freesurf_fnames.append(ftempl.format(*freesurf))
    return freesurf_fnames

def get_dwi_names(subjids_picks):
    for topup, topdn, dwi in orig_dwi:
        if all(x in subjids_picks.subjids for x in [topup[0], topdn[0], dwi[0]]):
            topup_fnames.append(ftempl.format(*topup))
            topdn_fnames.append(ftempl.format(*topdn))
            dwi_fnames.append(ftempl.format(*dwi))
    return topup_fnames, topdn_fnames, dwi_fnames

def get_5spgr_names(subjids_picks):
    for b1map, spgr5_fa5, spgr5_fa10, spgr5_fa15, spgr5_fa20, spgr5_fa30 in orig_5spgr:
        if all(x in subjids_picks.subjids for x in [spgr5_fa5[0], spgr5_fa10[0], spgr5_fa15[0], spgr5_fa20[0], spgr5_fa30[0], b1map[0]]):
            b1map5_fnames.append(ftempl.format(*b1map))
            spgr5_fa5_fnames.append(ftempl.format(*spgr5_fa5))
            spgr5_fa10_fnames.append(ftempl.format(*spgr5_fa10))
            spgr5_fa15_fnames.append(ftempl.format(*spgr5_fa15))
            spgr5_fa20_fnames.append(ftempl.format(*spgr5_fa20))
            spgr5_fa30_fnames.append(ftempl.format(*spgr5_fa30))
    return b1map5_fnames, spgr5_fa5_fnames, spgr5_fa10_fnames, spgr5_fa15_fnames, spgr5_fa20_fnames, spgr5_fa30_fnames

def get_3spgr_names(subjids_picks):
    for b1map, spgr_fa5, spgr_fa15, spgr_fa30 in orig_spgr:
        if all(x in subjids_picks.subjids for x in [spgr_fa5[0], spgr_fa15[0], spgr_fa30[0], b1map[0]]):
            b1map_fnames.append(ftempl.format(*b1map))
            spgr_fa5_fnames.append(ftempl.format(*spgr_fa5))
            spgr_fa15_fnames.append(ftempl.format(*spgr_fa15))
            spgr_fa30_fnames.append(ftempl.format(*spgr_fa30))
    return b1map_fnames, spgr_fa5_fnames, spgr_fa15_fnames, spgr_fa30_fnames


def get_3dt2_names(subjids_picks):
    for t2 in orig_t2:
        if t2[0] in subjids_picks.subjids:
            t2_fnames.append(ftempl.format(*t2))
    return t2_fnames

#
# for topup, topdn, dwi in orig_dwi:
#     topup_fnames.append(ftempl.format(*topup))
#     topdn_fnames.append(ftempl.format(*topdn))
#     dwi_fnames.append(ftempl.format(*dwi))
#
#
# for spgr_fa5, spgr_fa15, spgr_fa30, b1map in orig_spgr:
#     spgr_fa5_fnames.append(ftempl.format(*spgr_fa5))
#     spgr_fa15_fnames.append(ftempl.format(*spgr_fa15))
#     spgr_fa30_fnames.append(ftempl.format(*spgr_fa30))
#     b1map_fnames.append(ftempl.format(*b1map))
#
#
# for spgr5_fa5, spgr5_fa10, spgr5_fa15, spgr5_fa20, spgr5_fa30, b1map in orig_5spgr:
#     spgr5_fa5_fnames.append(ftempl.format(*spgr5_fa5))
#     spgr5_fa10_fnames.append(ftempl.format(*spgr5_fa10))
#     spgr5_fa15_fnames.append(ftempl.format(*spgr5_fa15))
#     spgr5_fa20_fnames.append(ftempl.format(*spgr5_fa20))
#     spgr5_fa30_fnames.append(ftempl.format(*spgr5_fa30))
#     b1map5_fnames.append(ftempl.format(*b1map))
#
#
# for vbm in vbm_rms:
#     vbm_fnames.append(ftempl.format(*vbm))
#
# for freesurf in freesurf_rms:
#     freesurf_fnames.append(ftempl.format(*freesurf))
