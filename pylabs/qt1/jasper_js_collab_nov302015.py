# hello

# Can you see this?
yes
# phantom dict
phantom_disc_ddata = defaultdict(list)

#funtion def stmt
def phantom_midslice_par2mni(parfile, method, datadict, outdir=None, exceptions=None, outfilename=None, run=1,
                                verbose=True, scaling='fp', minmax=('parse', 'parse'), origin='scanner', overwrite=True):
    key, value = [], []                                
    #key value list for real images:
    key = [(datetime.datetime.strptime(scandate, '%Y%m%d').date(), method+'_real', tr, run)]
    value = [(outfilename+'_real_1slmni_'+str(run)+'.nii', contrast)]

    #key value for magnitude:
    key += [(datetime.datetime.strptime(scandate, '%Y%m%d').date(), method+'_mag', tr, run)]
    value += [(outfilename+'_mag_1slmni_'+str(run)+'.nii', contrast)]

                                    
                                    
                                    
                                    
mydate = datetime.datetime.strptime(scandate, '%Y%m%d').date()
mymethod = method+'_mag'
partialkey = (mydate, mymethod, tr)

runkeys = [key for key in datadict.keys() if key[:3] == partialkey]  
for r in range(runkeys):
    exvalues = datadict[partialkey+(r)]
    for exvalue in exvalues:
        if contrast == exvalue[1]:               
            break;
    else:
        run = r # if you just want the run number  # case 2 key found but value/contrast does not exist eg new file
        break;
else:
    run = len(runkeys) + 1 # need to make new run    case 1, case 3
    
    
key += [(mydate, mymethod, tr, run)]  # case 3 = found key value pair exists we have repeat run   # case 1 = no key exists eg new file/run for loop never runs
value += [(outfilename+'_mag_1slmni_'+str(run)+'.nii', contrast)]

