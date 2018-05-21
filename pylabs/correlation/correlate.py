from __future__ import division
from os.path import join
import numpy, nibabel, scipy.stats, math, datetime
from numpy import square, sqrt
from pylabs.utils import progress
import pylabs.io.images
"""
TODO

* Monte carlo with stopping criterion
* global mean
* spearman's ranked correlation
* One-sided or two sided arg
* divide niterations by number of variables
* 2 group cross correlation with slope diff (see below)
"""


def wholeBrain(files, variables, outdir = '', niterations = 1000):
    assert len(files) == variables.shape[0] # ensure equally many subjects
    n = nsubjects = variables.shape[0]
    nvars = variables.shape[1]

    data, affine = pylabs.io.images.loadStack(files)

    print('Vectorizing and masking..')
    spatialdims = data.shape[1:]
    nvoxels = numpy.prod(spatialdims)
    data2d = data.reshape((nsubjects, nvoxels))
    mask1d = (data2d>0).all(axis=0)
    mdata2d = data2d[:, mask1d]
    nvalid = mask1d.sum()
    print('{0:.1f}% of voxels in mask.'.format(nvalid/nvoxels*100))

    X = mdata2d[:, numpy.newaxis, :]
    Y = variables.values[:, :, numpy.newaxis]
    r, t = corr(X, Y)
    p = scipy.stats.t.sf(numpy.abs(t), n-2) * 2       #997ms

    nvoxelsScalar = 4
    scalarResults = numpy.zeros((nvars, nvoxelsScalar))
    for v, varname in enumerate(variables.columns.values):
        for k in range(nvoxelsScalar):
            x = mdata2d[:, k]
            y = variables[varname]
            scalarResults[v, k] = scipy.stats.pearsonr(x,y)[0]
    #assert numpy.allclose(r[:,:4], scalarResults)

    print('Starting FDR permutations..')
    npermutations = math.factorial(n)
    #assert niterations < npermutations
    nbins = 1000
    tmax = 20.
    tres = tmax/nbins
    binedges = numpy.arange(0, tmax-tres, tres)
    tdist = numpy.zeros(binedges.size-1, dtype=int)
    start = datetime.datetime.now()
    for j in range(niterations):
        progress.progressbar(j, niterations, start)
        I = numpy.random.permutation(numpy.arange(nsubjects))
        Y = variables.values[:, :, numpy.newaxis]
        _, tp = corr(X, Y)
        tdist += numpy.histogram(numpy.abs(tp), binedges)[0]
    alpha = .05
    q = .05
    cumtdist = numpy.cumsum(tdist[::-1])/tdist.sum()
    closestbin = numpy.abs(cumtdist-(q*alpha)).argmin()
    tcorr = binedges[::-1][closestbin]
    pcorr = scipy.stats.t.sf(tcorr, n-2)
    assert pcorr < alpha
    print('\nCorrected p-value: {}'.format(pcorr))
    print('Corresponding t-value: {}'.format(tcorr))

    tneg = t.copy()
    tpos = t.copy()
    tneg[tneg>0] = 0
    tneg = numpy.abs(tneg)
    tpos[tpos<0] = 0
    stats = {
        'r': r,
        'tneg': tneg,
        'tpos': tpos,
        '1minp': 1-p,
    }
    ftemplates = {stat:'{}_'+stat+'.nii.gz' for stat in stats.keys()}
    print('Unvectorizing and saving to files..')
    outfnames = {var:{} for var in variables.columns.values}
    for stat, vector in stats.items():
        output2d = numpy.zeros((nvars, nvoxels))
        output2d[:, mask1d] = vector
        output4d = output2d.reshape((nvars,) + spatialdims)
        for v, varname in enumerate(variables.columns.values):
            outfnames[varname][stat] = join(outdir, 
                ftemplates[stat].format(varname))
            img = nibabel.Nifti1Image(output4d[v,:,:,:], affine)
            print('Saving file: {}'.format(ftemplates[stat].format(varname)))
            nibabel.save(img, outfnames[varname][stat])
    return outfnames, pcorr, tcorr


def corr(X, Y):
    n = Y.shape[0]
    mx = X.mean(axis=0, keepdims=True)
    my = Y.mean(axis=0, keepdims=True)
    xm, ym = X-mx, Y-my                             #48ms
    r_num = (xm * ym).mean(axis=0)                  #167ms
    r_den = X.std(axis=0) * Y.std(axis=0)           #108ms
    r = r_num / r_den
    t = r * sqrt( (n - 2) / (1 - square(r)) )       #19ms
    return (r, t)

# convert to python with data ready to plot with instruction
''''

FosterCare=xlsread('ad_foster_control.xls')

groups=FosterCare(:,1);
vocabulary=FosterCare(:,2);
AD=FosterCare(:,3);

ctrl=groups==1;
exp=groups==0;


%% Making a scatter plot  %%

figure,scatter(vocabulary(ctrl),AD(ctrl),150,'b')
[p,s]=polyfit(vocabulary(ctrl),AD(ctrl),1);
hold on;
X_axis=[min(vocabulary(ctrl)) max(vocabulary(ctrl))];
f=polyval(p,X_axis);
plot(X_axis,f,'-b','LineWidth',2);
[r,p]=corrcoef(vocabulary(ctrl),AD(ctrl))
text(95,0.001,['r=' num2str(r(1,2)) ' p< ' num2str(p(1,2))],'Color','b','fontsize',30)

scatter(vocabulary(exp),AD(exp),150,'k')
[p,s]=polyfit(vocabulary(exp),AD(exp),1);
hold on;
X_axis=[min(vocabulary(exp)) max(vocabulary(exp))];
f=polyval(p,X_axis);
plot(X_axis,f,'-k','LineWidth',2);
[r,p]=corrcoef(vocabulary(exp),AD(exp))
text(0.51420,0.5,['r=' num2str(r(1,2)) ' p< ' num2str(p(1,2))],'Color','k','fontsize',30)
xlabel('vocabulary','fontsize',26)
ylabel('Axial Diffusivity()','fontsize',26)


%% calculating the slope difference using the multiple regression analysis

learning=dataset(groups,vocabulary,AD);
learning.groups=nominal(learning.groups);
fit=LinearModel.fit(learning,'AD~vocabulary*groups')
model=anova(fit)

'''




