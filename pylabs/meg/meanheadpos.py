"""
Based on matlab code by Samu Taulu.

"""
import numpy


def create_grand_average_evoked(p, subjects, run_indices):
    """ Create average evoked files across subjects

    at the median or mean head position
    mnefun-style function signature.
    """
    pass


def quat2trans(quat):
    n = quat.shape[0]
    trans = numpy.zeros((n, 4, 4))
    for t in range(n):
        q = numpy.zeros(7,)
        q[1:] = quat[t, :]
        q[0] = numpy.sqrt( 1 - q[1]**2 - q[2]**2 -  q[3]**2 )
        trans[t, :, :] = numpy.identity(4)
        ## same values, could be refactored
        trans[t, 0, 0] = q[0]*q[0] + q[1]*q[1] - q[2]*q[2] - q[3]*q[3]
        trans[t, 0, 1] = 2*(q[1]*q[2] - q[0]*q[3])
        trans[t, 0, 2] = 2*(q[1]*q[3] + q[0]*q[2])
        trans[t, 1, 0] = 2*(q[1]*q[2] + q[0]*q[3])
        trans[t, 1, 1] = q[0]*q[0] - q[1]*q[1] + q[2]*q[2] - q[3]*q[3]
        trans[t, 1, 2] = 2*(q[2]*q[3] - q[0]*q[1])
        trans[t, 2, 0] = 2*(q[1]*q[3] - q[0]*q[2])
        trans[t, 2, 1] = 2*(q[2]*q[3] + q[0]*q[1])
        trans[t, 2, 2] = q[0]*q[0] - q[1]*q[1] - q[2]*q[2] + q[3]*q[3]
        trans[t, :3, 3] = q[4:]
    return trans


if __name__ == '__main__':
    from os.path import join, isdir
    import collections, os
    import mne
    from mnefun import Params
    from mnefun._paths import get_epochs_evokeds_fnames
    from picks import fullChpiValidEpochs as pickedSubjects
    params = Params()
    #params.work_dir = '/home/jasper/data/bbc/meg/'
    params.work_dir = '/diskArray/data/bbc/meg'
    params.subjects = ['bbc_'+str(s) for s in pickedSubjects]
    params.analyses = [
        'All',
        'Resp_vs_Aud',
        'Each'
    ]
    params.unfreeze()
    params.headpos_center_method = 'mean'

    ## Pretend we are in mnefun operation:
    p = params
    subjects = p.subjects
    analyses = p.analyses

    ## First calculate mean / median head pos
    alltrans = numpy.zeros((len(subjects), 3))
    for s, subj in enumerate(subjects):
        posfile = join(p.work_dir, subj, p.raw_dir, subj+'.pos')
        posdata = numpy.loadtxt(posfile, skiprows=1)
        quat = posdata[:, 1:7]
        subjtrans = quat2trans(quat)
        alltrans[s] = subjtrans[:, :3, 3].mean(axis=0)
    trans = numpy.identity(4)
    assert p.headpos_center_method in ('mean', 'median')
    if p.headpos_center_method == 'mean':
        trans[:3, 3] = alltrans.mean(axis=0)            # mean
    elif p.headpos_center_method == 'median':
        trans[:3, 3] = numpy.median(alltrans, axis=0) # median

    ## Then create new evoked files with this position
    n = len(subjects)
    subjectEvokeds = collections.defaultdict(list)
    for s, subj in enumerate(subjects):
        for analysis in analyses:
            _, evokedfnames = get_epochs_evokeds_fnames(p, subj, [analysis])
            group_pos_fname = evokedfnames[0].replace('-ave', '_grouppos-ave')
            evokeds_group_pos = []
            evokeds = mne.read_evokeds(evokedfnames[0])
            for evoked in evokeds:
                evoked = evoked.copy()
                evoked.info['dev_head_t']['trans'] = trans
                evokeds_group_pos.append(evoked)
                tag = analysis  + '_' + evoked.comment
                if evoked.kind == 'average':
                    subjectEvokeds[tag].append(evoked)
            mne.write_evokeds(group_pos_fname, evokeds_group_pos)

    ## Create grand average files
    grandavgDir = join(p.work_dir, 'grand')
    if not isdir(grandavgDir):
        os.mkdir(grandavgDir)
    for tag, evokeds in subjectEvokeds.items():
        assert len(evokeds) == n
        avg = mne.grand_average(evokeds)
        grandavgFilename = join(grandavgDir, '{}_{}{}_{}_n{}-ave.fif'.format(
                                tag, p.lp_cut, p.inv_tag, p.eq_tag, n))
        avg.save(grandavgFilename)

    report = mne.Report() #baseline=_get_baseline(p)
    report.parse_folder(data_path=grandavgDir, n_jobs=1, 
                        pattern=['*_n{}-ave.fif'.format(n)])
    report.save('bbc_evoked_report.html', open_browser=False, overwrite=True)
