import unittest

class ScoringTests(unittest.TestCase):

    def setUp(self):
        with open('data/sample_meg_events.csv') as samplefile:
            lines = samplefile.readlines()
        self.events = [l.split(',') for l in lines if len(l)>3]
        self.events = [[int(c.strip()) for c in l] for l in self.events]

    def test_scoring_recodes_matching_vs_control_targets(self):
        from meg.score import processEvents
        events = [
             (212877, 0, 4),
             (214631, 0, 8),
             (215800, 0, 3),
             (216997, 0, 2),
             (219903, 0, 3),
             (221100, 0, 2),
             (224006, 0, 3),
             (225220, 0, 4),
             (226734, 0, 8),
             (228142, 0, 3),
             (229339, 0, 2)]
        targets = [0,1,0,1,1]
        newEvents, counts = processEvents(events, targets)
        self.assertEqual(newEvents[0][2], 31)
        self.assertEqual(newEvents[5][2], 11)
        self.assertEqual(newEvents[7][2], 32)
        self.assertEqual(newEvents[10][2], 12)

    def test_scoring_deletes_overlapping_events(self):
        from meg.score import processEvents
        events = [
             (212877, 0, 1),
             (214631, 0, 2),
             (215800, 0, 3),
             (215997, 0, 4),  ## too early
             (219903, 0, 6),
             (221100, 0, 8),
             (224006, 0, 1),
             (225220, 0, 2),
             (225734, 0, 3),  ## too early
             (228142, 0, 4),
             (229339, 0, 6)]
        targets = [0,0,0,0]
        newEvents, counts = processEvents(events, targets)
        self.assertEqual(len(newEvents), 7)

    def test_scoring_reports_counts(self):
        from meg.score import processEvents
        events = [
             (212877, 0, 1),
             (214631, 0, 2), #cont
             (215800, 0, 3),
             (215997, 0, 4), #match     ## too early
             (219903, 0, 6),
             (221100, 0, 8),
             (224006, 0, 1),
             (225220, 0, 2), #cont
             (225734, 0, 3),            ## too early
             (228142, 0, 4), #match
             (229339, 0, 6)]
        targets = [0,1,0,1]
        newEvents, counts = processEvents(events, targets)
        self.assertEqual(counts['pre']['word1'],      2)
        self.assertEqual(counts['del']['word1'],      0)
        self.assertEqual(counts['kept']['word1'],     2)
        self.assertEqual(counts['pre']['word2match'], 0)
        self.assertEqual(counts['pre']['tone2match'], 2)
        self.assertEqual(counts['del']['tone2match'], 1)
        self.assertEqual(counts['kept']['tone2match'],1)
        self.assertEqual(counts['pre']['total'],      11)
        self.assertEqual(counts['del']['total'],      4)
        self.assertEqual(counts['kept']['total'],     7)


    def test_scoring_deletes_atifactual_events(self):
        from meg.score import processEvents
        events = [
             ( 81857, 0,   1),
             ( 83070, 0,   2),
             ( 85993, 0,   1),
             ( 87206, 0,   2),
             ( 90129, 0,   1),
             ( 91342, 0,   2),
             (100295, 0,   3),
             (101517, 0,   4),
             (104439, 0,   3),
             (105654, 0,   4),
             (107825, 0,   8),
             (109559, 0,   2), # odd one
             (109560, 2,   3),
             (110790, 0,   4),
             (113105, 0,   8),
             (114696, 0,   3),
             (115892, 0,   4)]
        targets = [0,0,0,0,0,0,0]
        newEvents, counts = processEvents(events, targets)
        self.assertEqual(counts['pre']['word2cont'], 3)
        self.assertEqual(len(newEvents), 16)

