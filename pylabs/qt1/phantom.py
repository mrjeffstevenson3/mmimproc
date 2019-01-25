# under development. not finished.

atlasfname = 'phantom_slu_mask_20160113.nii.gz'
atlasfpath = join(projectdir,atlasfname)

class T1Phantom(object):

    def __init__(self, fpath):
        self.fpath = fpath

    def aligned(self):
        """return aligned version"""

    def sortVials(self, vialOrder):
        pass

## expose vial data and vial labels

def samplevials(phantomFilePath):
    """
    Take average of the vial areas of the phantom file passed and then 
    uses ordervials()
    """

    ### Gather data by vial
    vialdata = statsByRegion(phantomFilePath, atlasfpath)
    labels = atlaslabels(atlasfname)

    ## Get rid of "background" ROI
    labels = labels[1:] # remove label for background
    vialdata['average'] = numpy.delete(vialdata['average'], 0)

    ## Reorder vials according to T1
    measuredVialsInOrder = [l for l in vialNumbersByAscendingT1 if str(l) in labels]
    vialIndicesInOrder = [labels.index(str(l)) for l in measuredVialsInOrder]
    # reorder labels
    labels = [labels[v] for v in vialIndicesInOrder]
    # reorder expected
    for key in expectedByDate.keys():
        expectedByDate[key] = [expectedByDate[key][v] for v in vialIndicesInOrder]
    # reorder vialData
    for key in vialdata.keys():
        vialdata[key]['average'] = vialdata[key]['average'][vialIndicesInOrder]

def ordervials
    """
    Takes array of vial data and cleans it up; order according to T1 and
    get rid of unused vials.
    """


## todo for model
#    ## Reverse order of vials for expected
#    for key in expectedByDate.keys():
#        expectedByDate[key].reverse()
## sample vials as atlas:    labels = atlaslabels(atlasfname)
