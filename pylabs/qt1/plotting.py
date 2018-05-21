from os.path import join
import matplotlib.pyplot as plt


def plotT1Timeseries(dates, data, labels, title, dtype=None, secondaryData=None, 
        plotdir='.'):
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
