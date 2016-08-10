from __future__ import print_function
import os, fnmatch, glob, collections, datetime, cPickle, sys, pickle
from os.path import join
import numpy
import matplotlib.pyplot as plt
from pylabs.regional import statsByRegion
from pylabs.correlation.atlas import atlaslabels
from pylabs.utils.paths import getlocaldataroot
import pylabs.qt1.expected
import pylabs.qt1.blacklist as bad
from pylabs.qt1.vials import vialNumbersByAscendingT1
from pylabs.qt1.naming import qt1filepath


def plotT1Timeseries(dates, data, labels, title, dtype=None, secondaryData=None, plotdir='.'):
    ylimPresets = {'t1':[0,2500],'absdiff':[-500,500],'reldiff':[-50,50]}
    plotfpath = join(plotdir,'{0}_timeseries.png'.format(title))
    plt.figure()
    lines = plt.plot(dates, data) 
    axes = plt.gca()
    if dtype in ylimPresets:
        axes.set_ylim(ylimPresets[dtype])
    if secondaryData is not None:
        ax2 = axes.twinx()
        ax2lines = ax2.plot(dates, secondaryData, 'r--')
        ax2.set_ylim(ylimPresets['reldiff'])
        lines += ax2lines
    plt.legend(lines, labels, loc=8)
    plt.savefig(plotfpath)

def atlasPhantoms(images, expectedByDate, projectdir, dirstruct='BIDS'):

    atlasfname = 'phantom_alignment_target_round_mask.nii.gz'
    atlasfpath = join(projectdir,atlasfname)

    ### Gather data by vial
    vialdata = {}

    print('Method, TR, B1 corr, date                        Found file')
    for image in images:
        filepath = qt1filepath(image, projectdir, dirstruct)
        newkey =  tuple([image[k] for k in ('method', 'TR', 'b1corr', 'X','date')])
        fileExists = os.path.isfile(filepath)
        print('{0: <65}\t{1}'.format(newkey, fileExists))
        if not fileExists:
            continue
        if newkey in vialdata:
            print(' --> Already have a run for this key.')
        vialdata[newkey] = statsByRegion(filepath, atlasfpath)

    print('\nVialdata for {0} images.\n'.format(len(vialdata.keys())))

    labels = atlaslabels(atlasfname)
    datesWithTemps = expectedByDate.keys()

    ## Get rid of "background" ROI
    labels = labels[1:] # remove label for background
    for key in vialdata.keys():
        vialdata[key]['average'] = numpy.delete(vialdata[key]['average'], 0)

    ## Reverse order of vials for expected
    for key in expectedByDate.keys():
        expectedByDate[key].reverse()

    ## Remove blacklisted vials
    for badvial in bad.vials:
        vialIndex = labels.index(str(badvial))
        for key in vialdata.keys():
            vialdata[key]['average'] = numpy.delete(vialdata[key]['average'], 
                vialIndex)
        for key in expectedByDate.keys():
            del expectedByDate[key][vialIndex]
        del labels[vialIndex]
    nvials = len(labels)

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

    ## Start plotting
    plotdir = join(projectdir,'plots')
    if not os.path.isdir(plotdir):
        os.makedirs(plotdir)
    b1corrtag = {True:'b1corr',False:'notb1c'}
    vialsOfInterest = [7,12]

    methods = set([k[:4] for k in vialdata.keys()])
    datafile = 'data/t1_factordata.pickle'
    factordata = {}
    for method in methods:
        methodstr = '{0}_{1}_{2}_{3}'.format(method[0], method[1],
                                             b1corrtag[method[2]], method[3])
        print(methodstr)
        thisMethodKeys = [k for k in vialdata.keys() if k[:4] == method]
        dates = sorted([k[4] for k in thisMethodKeys if k[4] in datesWithTemps])
        
        blackListedDates = [k[2] for k in bad.phantoms if k[:2]==method[:2]]
        dates = [d for d in dates if d not in blackListedDates]
        if not dates:
            print('No usable dates for this method.')
            continue # No dates for this method

        regStatsInOrder = [vialdata[method+(d,)]['average'] for d in dates]
        obsVialtc = numpy.array(regStatsInOrder)

        ## Observed data
        plotT1Timeseries(dates, obsVialtc, labels, methodstr, dtype='t1', 
            plotdir=plotdir)

        ## Expected plot for same dates
        expVialtc = numpy.array([expectedByDate[d] for d in dates])
        plotT1Timeseries(dates, expVialtc, labels, methodstr+'_expected', 
            dtype='t1', plotdir=plotdir)

        ## Difference
        diffVialtc = expVialtc - obsVialtc
        plotT1Timeseries(dates, diffVialtc, labels, methodstr+'_diff', 
            dtype='absdiff', plotdir=plotdir)

        ## Relative Difference
        reldiffVialtc = ((expVialtc - obsVialtc)/expVialtc)*100
        plotT1Timeseries(dates, reldiffVialtc, labels, methodstr+'_reldiff',     
            dtype='reldiff', plotdir=plotdir)

        ## Singled out vials:
        for voi in vialsOfInterest:
            voiIndex = labels.index(str(voi))
            svExpObs = numpy.array([expVialtc[:,voiIndex],obsVialtc[:,voiIndex]]).T
            svReldiff = reldiffVialtc[:,voiIndex]

            plotT1Timeseries(dates, svExpObs, ['model','observed','diff'], 
                methodstr+'_vial{0}'.format(voi), dtype='t1', 
                secondaryData=svReldiff, plotdir=plotdir)

        ## Time average:
        plt.figure()
        ax = plt.gca()
        width = .2
        ind = numpy.arange(nvials)
        rects1 = ax.bar(ind,         expVialtc.mean(axis=0), width, color='blue')
        rects2 = ax.bar(ind+width,   obsVialtc.mean(axis=0), width, color='green')
        rects3 = ax.bar(ind+width*2, diffVialtc.mean(axis=0), width, color='red')
        ax.set_ylim([-500,2500])
        plt.legend((rects1[0],rects2[0],rects3[0]), ['model','observed','diff'], loc=2)
        plotfpath = join(plotdir,'{0}_avg.png'.format(methodstr))
        plt.savefig(plotfpath)

        ## Save data to generate correction factor:
        factordata[method] = {'dates':dates, 
                                'model':expVialtc.tolist(), 
                                'observed':obsVialtc.tolist()}

    pickle.dump(factordata, open( datafile, 'wb'))

if __name__ == '__main__':
    coreg = True # Look at coregistered file or non-coregistered files
    projectdir = join(getlocaldataroot(),'phantom_qT1_disc')
    images = {}
    dicts = ['phantom_disc_dict_dec3.txt', 'phantom_disc_dict_gilad.txt']
    for dictname in dicts:
        imageDictFile = join(projectdir, dictname)
        with open(imageDictFile) as dfile:
            images.update(cPickle.load(dfile))
    expectedByDate = pylabs.qt1.expected.readfromfile()
    atlasPhantoms(images, expectedByDate=expectedByDate, projectdir=projectdir, 
        dirstruct='legacy')




    


