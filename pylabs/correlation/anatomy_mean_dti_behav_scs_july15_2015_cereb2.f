	character*1 cnmr(2000),chead(348),a1(20),ctstat,catlas(4000)
	integer*2 inmr1(2000), atlas(182,218,182,1,4)
	equivalence (inmr1,catlas)
	character*75 cfn(4),cfntracts(4,20)
	character*120 cfnpass,cfndti,cfnplot,cfnlabel,cfntract1
	character*110 cfnlabels(500),cfnsav(500)
	character*80 cfnatlas
	character*2 c2dti,ch2behav,c2
	character*3 creg
		character*40 cfnout
			character*80 cplotlabel(31,200)
	character*5 cside(500)
	integer*2 ihead(174)
	real nmr(500),plotmatrix(200,200),mrisub(100)
	real imagef(182,218,182,5),tracts(182,218,182,19),dti(182,218,182,19)
	real behav(200,200),r1(500),vbm(500),final(200,200)
	equivalence (nmr,cnmr)
	equivalence (chead,ihead)
	real dnmr(10000), behav1(10000)
	integer isubjects(200)
	integer*2 iborder(30)
c
c this is the brain region order used for the final table
	iborder(1) = 1
	iborder(2) = 2
	iborder(3) = 10
	iborder(4) = 7
	iborder(5) = 8
	iborder(6) = 3
	iborder(7) = 4
	iborder(8) = 11
	iborder(9) = 12
	iborder(10) = 15
	iborder(11) = 16
	iborder(12) = 19
	iborder(13) = 20
	
	iborder(14) = 17
	iborder(15) = 18
	iborder(16) = 5
	iborder(17)= 6
	iborder(18) = 13
	iborder(19) = 14
	iborder(20) = 9
	iborder(21) = 21
	iborder(22) = 22
	iborder(23) = 23

c
	open(11,file = 'passname.txt')
	read(11,*)cfnpass
	close(11)
	open(11,file = 'tstat.txt')
	read(11,*)ctstat
	close(11)

	
	open(11,file = 'behavcol.txt')
	read(11,*)ich2behav
	close(11)
	write(ch2behav,19)ich2behav
	if(ch2behav(1:1).eq.' ') ch2behav(1:1)='0'
	
	open(11,file = 'dtimeas.txt')
	read(11,*)c2dti
	close(11)
		
	open(11,file = 'groupnums.txt')
	read(11,*)istartgr1,iendgr1,istartgr2,iendgr2
	close(11)

	open(11,file = 'thresh.txt')
	read(11,*)threshold
	close(11)
c
	open(11,file = 'subjectids.txt')
	read(11,*)(isubjects(i),i=1,iendgr2)
	close(11)

	
	open(11,file = 'afile2.hdr',form='unformatted')
	do i=1,348
	call fgetc(11,chead(i),istate)
	enddo
	close(11)
	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	itsize = ihead(25)
	write(6,*) 'ixsize ',ixsize,iysize,izsize,itsize


	isubtot=iendgr1
	ibehavtot = 38
c
c change the character c2behav into a column number
c
c	write(6,*)'enter the behavioral column number '
c	read(5,*)ich2behav
 19	format(i2)
	write(6,*)'ich2behav ',ich2behav
	isubtotbeh=24	
	open(11,file = 'behav.csv')
	read(11,*)cfn
	read(11,*)cfn
	do i=1,isubtotbeh
	read(11,*)(r1(ii),ii=1,ibehavtot)
	write(6,*)'1 17 ',r1(1),r1(36),i3
	do ii=1,ibehavtot
	behav(ii,i) = r1(ii)
	enddo   !ii
	enddo   !i
	close(11)
c
	isubtotmri=19
	isubtotbeh=24
	ibehavtot = 38
	open(11,file = 'list_of_subjects_mri19.txt')
	do i=1,isubtotmri
	read(11,*)mrisub(i)
	enddo
	close(11)
c
c first reorder so that behavioral is matched to the vbm list
c

	do iset1 =1,isubtotmri
	do iset2 = 1,isubtotbeh
	if(behav(1,iset2).eq.mrisub(iset1))then
	do ifil=1,ibehavtot
	final(ifil,iset1) = behav(ifil,iset2)
	enddo  !ifil behcol
	write(6,*)'found sub ',final(1,iset1),iset1,final(36,iset1)
	endif
	enddo !iset2
	enddo  !iset1

c
c open the correct dti all file
c


	open(11,file = 'afile2.img',form='unformatted')
	do it=1,itsize
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	dti(i,j,k,it) = nmr(i)
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)
c
	open(11,file = 'afile3.img',form='unformatted')
	do it=1,itsize
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	tracts(i,j,k,it) = nmr(i)
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)

c
c load all three atlases for gray matter

c
	
	do ifil=1,2
	if(ifil.eq.2)cfnatlas = 'JHU-1mm_newATR1_newCC21_LR_cerebellum.hdr'
	if(ifil.eq.1)cfnatlas = 'mori1.hdr'

	write(6,*)'cfnatlas ',cfnatlas
	open(11,file = cfnatlas,form='unformatted')

	do i=1,348
	call fgetc(11,chead(i),istate)
	enddo
	close(11)

	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	write(6,*) 'ixsize ',ixsize,iysize,izsize
	do i=1,80
	if(cfnatlas(i:i).eq.'.')iper = i
	enddo
	cfnatlas(iper+1:iper+3) = 'img'
	open(11,file = cfnatlas,form='unformatted')
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*2
	call fgetc(11,catlas(i),istate)
	enddo
	do i=1,ixsize
	atlas(i,j,k,1,ifil) = inmr1(i)
	enddo
	enddo  !j
	enddo  !k
	close(11)
	enddo  !ifil


c

	open(11,file = 'afile.img',form='unformatted')

	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	write(6,*) 'ixsize ',ixsize,iysize,izsize

	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	imagef(i,j,k,2) = nmr(i)
c	if(imagef(i,j,k,2).ge.0.98)write(6,*)'tstat check ',imagef(i,j,k,2),i,j,k
	enddo !i
	enddo  !j
	enddo  !k
	close(11)
	
c
c generate reports
c
	cfnlabel(1:26) = 'moriatlas_reports.txt'
	cfnlabel(6:7)=ch2behav
	cfnlabel(8:9)=c2dti
	cfnlabel(10:10)=ctstat


	open(12,file = cfnlabel(1:21))
		cfnlabel(1:26) = 'finiatlas_reports.txt'
	cfnlabel(6:7)=ch2behav
	cfnlabel(8:9)=c2dti
	cfnlabel(10:10)=ctstat


	open(22,file = cfnlabel(1:21))
	open(32,file = 'brainregions.txt')
	write(12,*)cfnpass
	write(12,*)'findex count95 atlassize fract95 mean95 atlas_type behav_col modality correlation brain_region sidedness mnix mniy mniz '
		cfnout='averstdev95_moriasfa1.txt'
	cfnout(19:20) = c2dti
	cfnout(21:21)= ctstat

	cfnout(16:18)='xyz'

	open(23,file = cfnout)
	write(23,*)' regindex side x y z count '

	do ifil = 1,2
		
	if(ifil.eq.2)then
	iatlas_size = 23
	open(13,file = 'JHU-tracts_jsedits_july13_2015_cerebellum.txt')
	do i=1,iatlas_size
	read(13,*)cfnlabels(i)
	enddo
	close(13)
	endif
	
	if(ifil.eq.1)then
	iatlas_size = 176
	open(13,file = 'JHU_MNI_SS_WMPM_Type-I_SlicerLUT.txt')
	do i=1,3
	read(13,*)cfnlabels(i)
	enddo
		do i=1,176
	read(13,*)i1,cfnlabels(i)
	write(6,*)'cfnlabels ',cfnlabels(i),k
	enddo
	endif

	iregindex = 1
	do iregx = 1,iatlas_size
c	do iregx = 1,19
	if(ifil.eq.2)then
	ireg = iborder(iregx)
	else
	ireg = iregx
	endif
c	ireg = iregx
	icount = 0
	sum = 0
	size = 0

	regsize = 0
c	write(6,*)'imagef ',imagef(115,110,108,2),ireg
c	pause

	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
c	do k=114+1,114+1
c	do j=109+1,109+1
c	do i=107+1,107+1

c		write(6,*)'imagef(i,j,k,2) ',imagef(i,j,k,2),atlas(i,j,k,1,ifil),i,j,k,ireg
	if(imagef(i,j,k,2).ge.threshold.and.atlas(i,j,k,1,ifil).eq.ireg)then
	icount = icount+1
	size = size+1
	sum = sum+imagef(i,j,k,2)
c	write(6,*)'imagef(i,j,k,2) ',imagef(i,j,k,2),i,j,k,ireg
	endif

	if(atlas(i,j,k,1,ifil).eq.ireg)then
	regsize = regsize+1
	endif

	enddo  !i
	enddo  !j
	enddo  !k

	if(icount.ge.7)then



	write(6,*)ireg,icount,ifil
	endif

	if(icount.ge.7)then
	do it=1,isubtot
	sumd = 0
	sized = 0
	rmax = 0
	summod=0
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(imagef(i,j,k,2).ge.threshold.and.atlas(i,j,k,1,ifil).eq.ireg.and.dti(i,j,k,it).ne.0)then
	rmax = max(imagef(i,j,k,2),rmax)
	if(rmax.eq.imagef(i,j,k,2))then
	imax = i
	jmax = j
	kmax = k
	endif

	
	sumd = sumd +dti(i,j,k,it)
		summod =summod + tracts(i,j,k,it)
c	write(6,*)'dti ',dti(i,j,k,it),i,j,k,it,ireg
	sized = sized +1
	cfnsav(iregindex) = cfnlabels(ireg)
	if(i.lt.91)cside(iregindex) = 'right'
	if(i.ge.91)cside(iregindex) = 'left'
	endif


	enddo  !i
	enddo  !j
	enddo  !k
	rout = sumd/sized
	routmod = summod/sized


	plotmatrix(it,iregindex) = rout
	plotmatrix(it+31,iregindex) = routmod
		cplotlabel(it,iregindex) = cfnlabels(ireg)

	dnmr(it) = rout
	behav1(it) = final(ich2behav,it)
	enddo  !it
	
	do i=1,19
c	write(6,*)'corr check ',dnmr(i),behav1(i),i,isubtot
	enddo  

	call correlation(dnmr,behav1,rcorr,isubtot)	
c	write(12,*)ireg,icount,regsize,size/regsize,sum/size,ifil,' ',ch2behav,' ',c2dti,' ',rcorr,cfnlabels(ireg),cside(iregindex)
c	write(6,*)ireg,icount,regsize,size/regsize,sum/size,ifil,' ',ch2behav,' ',c2dti,' ',rcorr,cfnlabels(ireg),cside(iregindex)
	write(12,*)ireg,icount,regsize,size/regsize,sum/size,ifil,' ',ch2behav,' ',c2dti,' ',rcorr,cfnlabels(ireg),cside(iregindex),(90-(imax-1)),((jmax-1)-126),((kmax-1)-72),(dti(imax,jmax,kmax,it),it=1,isubtot),(tracts(imax,jmax,kmax,it),it=1,isubtot)
	write(6,*)ireg,icount,regsize,size/regsize,sum/size,ifil,' ',ch2behav,' ',c2dti,' ',rcorr,cfnlabels(ireg),cside(iregindex),(90-(imax-1)),((jmax-1)-126),((kmax-1)-72)
	if(icount.ge.7)then
	write(23,*)cplotlabel(1,iregindex),cside(iregindex),(90-(imax-1)),((jmax-1)-126),((kmax-1)-72),icount
	else
		write(23,*)cplotlabel(1,iregindex),'0 0 0 0 ',icount
	endif
	if(ifil.eq.2)write(22,*)icount,rcorr
	if(ifil.eq.2)write(32,*)cfnlabels(ireg)
	iregindex = iregindex+1
	else
	if(ifil.eq.2)write(22,*)ireg,'9999 ','9999'
	if(ifil.eq.2)write(32,*)cfnlabels(ireg)
	endif

	enddo  !ireg

	do ir = 1,iregindex-1
	write(creg,18)ir
 18	format(i3)
 	if(creg(1:1).eq.' ')creg(1:1) = '0'
 	 if(creg(2:2).eq.' ')creg(2:2) = '0'

		if(ifil.eq.1)cfnplot = 'plotxxxxxxxmori.txt'
		if(ifil.eq.2)cfnplot = 'plotxxxxxxxjhuj.txt'
		if(ifil.eq.3)cfnplot = 'plotxxxxxxxcereb.txt'
		if(ifil.eq.4)cfnplot = 'plotxxxxxxxcere4.txt'

	cfnplot(4:6)=creg
	cfnplot(7:8)=ch2behav
	cfnplot(9:10)=c2dti
		cfnplot(11:11)=ctstat



	open(21,file = cfnplot)
	do i=1,isubtot
c	write(21,*)final(ich2behav,i),plotmatrix(i,ir)*100,behav(1,i),isubjects(i)
	write(21,*)final(ich2behav,i),plotmatrix(i,ir),plotmatrix(i+31,ir),behav(1,i),isubjects(i)
	enddo
	close(21)

	if(ifil.eq.1)cfnplot = 'plotxxxxxxxmori.txtl'
		if(ifil.eq.2)cfnplot = 'plotxxxxxxxjhuj.txtl'
			if(ifil.eq.3)cfnplot = 'plotxxxxxxxcereb.txtl'
			if(ifil.eq.4)cfnplot = 'plotxxxxxxxcere4.txtl'
	cfnplot(4:6)=creg
	cfnplot(7:8)=ch2behav
	cfnplot(9:10)=c2dti
		cfnplot(11:11)=ctstat

	open(21,file = cfnplot)
	write(21,*)cfnsav(ir)
	close(21)
	
		if(ifil.eq.1)cfnplot = 'plotxxxxxxxmori.txts'
		if(ifil.eq.2)cfnplot = 'plotxxxxxxxjhuj.txts'
		if(ifil.eq.3)cfnplot = 'plotxxxxxxxcereb.txts'
				if(ifil.eq.4)cfnplot = 'plotxxxxxxxcere4.txts'
	cfnplot(4:6)=creg
	cfnplot(7:8)=ch2behav
	cfnplot(9:10)=c2dti
		cfnplot(11:11)=ctstat
	open(21,file = cfnplot)
	write(21,*)cside(ir)
	close(21)


	enddo  !ir



	enddo  !ifil

	close(12)
	close(23)
	close(22)
	close(32)

c
	stop
	end
	

		
c correlation
c
	subroutine correlation(dnmr,behav1,rcorr,itsize)
	real dnmr(10000),behav1(10000)
	suma = 0
	sumb = 0
	sumsquarea = 0
	sumsquareb = 0
	sumab = 0
	rsize = 0
	do it=1,itsize
	suma = suma + dnmr(it)
	sumb = sumb + behav1(it)
	sumsquarea = sumsquarea + (dnmr(it)**2)
	sumsquareb = sumsquareb + (behav1(it)**2)

	sumab = sumab + (dnmr(it)*behav1(it))
	rsize =rsize +1
	enddo !it

	rmeana = suma/rsize
	rmeanb = sumb/rsize
c	write(6,*)'rmeana rmeanb ',rmeana,rmeanb

	sumasquare = 0
	sumbsquare = 0
	sumab = 0
	do i=1,itsize
	sumasquare = sumasquare+((dnmr(i)-rmeana)**2)
	sumbsquare = sumbsquare+((behav1(i)-rmeanb)**2)
	sumab = sumab + ((dnmr(i)-rmeana)*(behav1(i)-rmeanb))
	enddo
	denoma = (sumasquare**0.5)
	denomb = (sumbsquare**0.5)
	rdenominator = denoma*denomb
	if(rdenominator.ne.0)then
	rcorr = sumab/(denoma*denomb)	
	else
	rcorr = 0
	endif
	return
	end
