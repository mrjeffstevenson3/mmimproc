from pylabs.projects.nbwr.file_names import project, get_vbm_names, get_freesurf_names

subjids_picks = SubjIdPicks()

picks = ['998']

setattr(subjids_picks, 'subjids', picks)

vbm_fnames = get_vbm_names(subjids_picks)
freesurf_fnames = get_freesurf_names(subjids_picks)

print vbm_fnames, type(vbm_fnames)
print freesurf_fnames, type(freesurf_fnames)

