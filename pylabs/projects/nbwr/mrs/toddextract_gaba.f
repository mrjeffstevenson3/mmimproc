c
c 
	character*1 cnmr(16384)
	open(11,file = 'sub-nbwr215_WIP_RTGABAMM_TE80_120DYN_12_2_raw_act.SDAT')
	open(12,file = 'sub-nbwr215_WIP_RTGABAMM_TE80_120DYN_12_2_edited_tr_raw_act.SDAT')
	do irow=1,120
	if(irow.ge.1.and.irow.le.20)then
	do ii=1,16384
	call fgetc(11,cnmr(ii),istate)
	call fputc(12,cnmr(ii),istate)
	enddo  !ii
	endif
	if(irow.ge.21.and.irow.le.30)then
	do ii=1,16384
	call fgetc(11,cnmr(ii),istate)
	enddo  !ii
	endif

	if(irow.ge.31.and.irow.le.70)then
	do ii=1,16384
	call fgetc(11,cnmr(ii),istate)
	call fputc(12,cnmr(ii),istate)
	enddo  !ii
	endif
	if(irow.ge.71.and.irow.le.80)then
	do ii=1,16384
	call fgetc(11,cnmr(ii),istate)
	enddo  !ii
	endif

	if(irow.ge.81.and.irow.le.120)then
	do ii=1,16384
	call fgetc(11,cnmr(ii),istate)
	call fputc(12,cnmr(ii),istate)
	enddo  !ii
	endif
	enddo  !irow
	close(11)
	close(12)

	stop
	end
	
