

cwd = $(shell pwd) # this dereferences the symlinks in pwd
SUBJECT=$(notdir $(cwd))
SESSNUM=$(shell echo $(cwd) | egrep -oe session[0-9]) # grep for the session number
PROJECT_DIR=/projects2/act-plus


.PHONY: afq_dir afq_all afq_clean afq_mostlyclean

# keep everything by default
.SECONDARY:

afq_all: afq_dir afq/dt6.mat afq/afq.mat afq/fa.csv afq/Fibers.gif afq/tract_avg_fa.csv

afq_dir:
	mkdir -p afq

#get tensor in .m format
afq/dt6.mat: dti/out/dtifit_out_S0.nii.gz memprage/T1.nii.gz
	matlab -nodesktop -nodisplay -nosplash -r "dtiMakeDt6FromFsl('dti/out/dtifit_out_S0.nii.gz','memprage/T1.nii.gz','afq/dt6.mat');quit"

#do the tracking, clean up the tracts, and extract metrics
afq/afq.mat: afq/dt6.mat
	matlab -nodesktop -nodisplay -nosplash -r "afq=AFQ_run({'afq/'},[0]) ; save('afq/afq.mat','afq'); quit"

#save metrics in a reasonable format
afq/fa.csv: afq/afq.mat
	matlab -nodesktop -nodisplay -nosplash -r "load('afq/afq.mat') ; cell2csv('afq/temp_fgnames.csv',afq.fgnames') ; csvwrite('afq/temp_fa.csv',cell2mat(afq.vals.fa')) ; csvwrite('afq/temp_md.csv',cell2mat(afq.vals.md')) ; csvwrite('afq/temp_volume.csv',cell2mat(afq.vals.volume')) ; quit "
	paste -d , afq/temp_fgnames.csv afq/temp_fa.csv > afq/fa.csv
	paste -d , afq/temp_fgnames.csv afq/temp_md.csv > afq/md.csv
	paste -d , afq/temp_fgnames.csv afq/temp_volume.csv > afq/tract_volume.csv
	rm -f afq/temp_fgnames.csv afq/temp_fa.csv afq/temp_md.csv afq/temp_volume.csv

#output a rotating gif for QC. REQUIRES A DISPLAY
afq/Fibers.gif: afq/afq.mat
	matlab -nodesktop -nosplash -r "load('afq/fibers/MoriGroups_clean_D5_L4.mat') ; AFQ_RotatingFgGif_DJP(fg,jet(20),'afq/Fibers.gif') ; quit "

afq/tract_avg_fa.csv: afq/fa.csv
	$(PROJECT_DIR)/bin/weighted_average.sh afq/fa.csv afq/tract_volume.csv afq/tract_avg_fa.csv
	$(PROJECT_DIR)/bin/weighted_average.sh afq/md.csv afq/tract_volume.csv afq/tract_avg_md.csv
	$(PROJECT_DIR)/bin/weighted_average.sh afq/tract_volume.csv afq/tract_volume.csv afq/tract_avg_thickness.csv


afq_mostlyclean:
	echo "nothing to be done (not sure what can be deleted here)"

afq_clean:
	rm -rf afq/

