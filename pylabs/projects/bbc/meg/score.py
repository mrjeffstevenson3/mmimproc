# -*- coding: utf-8 -*-
# Copyright (c) 2015, LABS^N
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import warnings
import pandas
import mne
from data.targets import meg as targets
targets = targets*4

from mnefun._paths import get_raw_fnames, get_event_fnames

def score_words_tones(p, subjects, run_indices):
    """Default scoring function that just passes event numbers through"""
    for si, subj in enumerate(subjects):
        print('  Scoring subject %s... ' % subj)

        # Figure out what our filenames should be
        raw_fnames = get_raw_fnames(p, subj, 'raw', False, False,
                                    run_indices[si])
        eve_fnames = get_event_fnames(p, subj, run_indices[si])

        for raw_fname, eve_fname in zip(raw_fnames, eve_fnames):
            with warnings.catch_warnings(record=True):
                raw = mne.io.read_raw_fif(raw_fname, allow_maxshield=True)
            events = mne.find_events(raw, stim_channel='STI101',
                                     shortest_event=1)
            recoded, counts = processEvents(events, targets)
            print(counts)
            mne.write_events(eve_fname, recoded)

eventids = {'response':60,
    'word1':10, 'word2cont':11,'word2match':12,  
    'tone1':30, 'tone2cont':31, 'tone2match':32}
eventnames = {v: k for k, v in eventids.items()}
origids = {1:'word1',2:'word2',3:'tone1',4:'tone2',
    5:'response',6:'response',7:'response',8:'response'}
mindelay = 750 # samples

def processEvents(events, targets):
    nevents = len(events)
    precounts = dict.fromkeys(eventids.keys(), 0)
    delcounts = dict.fromkeys(eventids.keys(), 0)
    recoded = []
    t = -1
    for event in events:
        sample, preOnsetId, origid = event 
        assert origid in origids

        if len(recoded) > 0:
            if preOnsetId > 0:
                # this catches a rare occurrence e.g. in sub 239
                # where an event is preceded by a fake event.
                print('Throwing out boogie trigger at sample '+str(sample))
                prevEventId = recoded[-1][2]
                precounts[eventnames[prevEventId]] -= 1
                del recoded[-1]
                t -= 1

        etype  = origids[origid]
        if origid in [2, 4]:
            t += 1
            if targets[t]:
                etype += 'match'
            else:
                etype += 'cont'
        precounts[etype] += 1

        
        if len(recoded) > 0:                
            if sample - recoded[-1][0] < mindelay:
                delcounts[etype] += 1
                prevEventId = recoded[-1][2]
                delcounts[eventnames[prevEventId]] += 1
                del recoded[-1]
                continue

        recoded.append((sample, 0, eventids[etype]))

    counts = pandas.DataFrame({'pre':precounts, 'del': delcounts})
    counts['kept'] = counts['pre'] - counts['del']
    counts.loc['total'] = counts.sum()
    return recoded, counts

