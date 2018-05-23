c  gfortran -O3 -mcmodel=medium -g anatomy_group_generatetable_july15_2015_cereb2.f -o anatomy_group_generatetable_july15_2015_cereb2 -ffixed-line-length-none

	character*1 cnmr(2000),chead(348),a1(20),ctstat
	integer*2 inmr2b(500),atlas(182,218,182,50,5)
	character*1 cnmr2b(1000)
	equivalence (inmr2b,cnmr2b)
	integer*1 inmr1(2000)
	character*100 cfn(6),cfnlabels(500),cfntracts(4,500)
	character*80 cfnpass,cfndti,cfnplot,cfnlabel,cfntract1
	character*80 cregsav(500),cfnatlas
	character*2 c2dti,ch2behav,creg
	integer*2 ihead(174),ibinsav(5)
	character*110 cfnlabels_prob(200)
	character*40 cfnout
	character*5 cside(500)
	real nmr(500),plotmatrix(200,200),plotmatrix97(31,200)
	character*80 cplotlabel(31,200)
	real imagef(182,218,182,9),tracts(182,218,182,31),dti(182,218,182,40)
	real r1(200),vbm(200),final(200,200)
	equivalence (nmr,cnmr)
	equivalence (inmr1,cnmr)
	equivalence (chead,ihead)

	real dnmr(1000), behav1(2000),dnmr2(1000)
		integer isubjects(100)
	integer*2 iborder(21)
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

c
	isubtot = 31

	open(11,file = 'passname.txt')
	read(11,*)cfnpass
	close(11)
	
 19	format(i2)
	open(11,file = 'dtimeas.txt')
	read(11,*)c2dti
	close(11)
	
	open(11,file = 'tstat.txt')
	read(11,*)ctstat
	close(11)

	open(11,file = 'groupnums.txt')
	read(11,*)istartgr1,iendgr1,istartgr2,iendgr2
	close(11)

	open(11,file = 'thresh.txt')
	read(11,*)threshold
	close(11)
	open(11,file = 'subjectids.txt')
	read(11,*)(isubjects(i),i=1,iendgr2)
	close(11)

	do i=1,80
	if(cfnpass(i:i).eq.'.')then
	iper = i
	go to 99
	endif
	enddo
 99	continue
c  
c
c open the correct dti all file
c
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
	cfndti(21:23) = 'img'


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

	do ifil=1,2
	if(ifil.eq.2)cfnatlas = 'JHU-1mm_newATR1_newCC21_LR_cerebellum.img'
	if(ifil.eq.1)cfnatlas = 'mori1.img'

	open(11,file = cfnatlas,form='unformatted')

	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	write(6,*) 'ixsize ',ixsize,iysize,izsize

	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*2
	call fgetc(11,cnmr2b(i),istate)
	enddo
	do i=1,ixsize
	imagef(i,j,k,4+ifil) = inmr2b(i)
	enddo
	enddo  !j
	enddo  !k
	
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
	enddo
	enddo  !j
	enddo  !k
	close(11)
c
	do ifil = 1,2

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
	itsize = ihead(25)
	write(6,*) 'ixsize ',ixsize,iysize,izsize,itsize,ifil

	do i=1,80
	if(cfnatlas(i:i).eq.'.')iper = i
	enddo
	cfnatlas(iper+1:iper+3) = 'img'
	
	open(11,file = cfnatlas,form='unformatted')
	do it=1,itsize
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*2
	call fgetc(11,cnmr2b(i),istate)
	enddo
	do i=1,ixsize
	atlas(i,j,k,it,ifil) = inmr2b(i)
	if(ifil.eq.5.and.k.eq.90.and.j.eq.90)write(6,*)'inm2b ',inmr2b(i),i
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)


	enddo  !ifil
c
c generate reports
c
c
	cfnplot = 'plotxxx_all.txt'
	cfnplot(5:6) = c2dti
	cfnplot(7:7) = ctstat

	open(21,file = cfnplot)
	cfnlabel(1:10) = 'moria_repo'
	cfnlabel(11:12) = c2dti
	cfnlabel(13:13) = ctstat

	cfnlabel(14:17) = '.txt'
	open(12,file = cfnlabel(1:17))

c	write(12,*)'findex count96 atlassize fract96 mean96 atlas_type column_index atlas_label bin95 bin96 bin97 bin98 bin99 maxsig'
	write(12,*)'findex count95 atlassize fract95 mean95 atlas_type modality brain_region sidedness mnix mniy mniz ',(ii,ii=1,31),(ii,ii=1,31)
	cfnout='averstdev95_moriasfa1.txt'
	cfnout(19:20) = c2dti
	cfnout(21:21)= ctstat

	open(22,file = cfnout)
	write(22,*)' regindex meanbi meanmono ttest ttestmode '
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


c begin insert from vbm

	iregindex = 1
	icolindex = 1

	do iregx = 1,iatlas_size
c	do iregx = 1,19
	if(ifil.eq.3)then
	ireg = iborder(iregx)
	else
	ireg = iregx
	endif
	icount = 0
	sum = 0
	size = 0
	icount97 = 0
	sum97 = 0
	size97 = 0

	regsize = 0

	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(imagef(i,j,k,2).ge.threshold.and.atlas(i,j,k,1,ifil).eq.ireg)then
	icount = icount+1
	size = size+1
	sum = sum+imagef(i,j,k,2)
	endif

	if(atlas(i,j,k,1,ifil).eq.ireg)then
	regsize = regsize+1
	endif

	enddo  !i
	enddo  !j
	enddo  !k
c
c start binning
c

	do ibin=1,5
	icountbin = 0

	if(ibin.eq.1)then
	thrstart = 0.95
	thrend = 0.9599
	endif
	if(ibin.eq.2)then
	thrstart = 0.96
	thrend = 0.9699
	endif
	if(ibin.eq.3)then
	thrstart = 0.97
	thrend = 0.9799
	endif
	if(ibin.eq.4)then
	thrstart = 0.98
	thrend = 0.9899
	endif
	if(ibin.eq.5)then
	thrstart = 0.99
	thrend = 0.9999
	endif


	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(imagef(i,j,k,2).ge.thrstart.and.imagef(i,j,k,2).le.thrend.and.atlas(i,j,k,1,ifil).eq.ireg)then
	icountbin = icountbin+1
	endif

	enddo  !i
	enddo  !j
	enddo  !k
	ibinsav(ibin) = icountbin
	enddo  !ibin

c  end binning
c
c start find the max significance
c
	rmax = 0
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(atlas(i,j,k,1,ifil).eq.ireg)then
	rmax = max(imagef(i,j,k,2),rmax)
	endif

	enddo  !i
	enddo  !j
	enddo  !k
c
c end find the max signficance


	if(icount.ge.0)then

c	write(12,*)ireg,icount,regsize,size/regsize,sum/size,ifil+2,icolindex,cfnlabels_prob(ireg),(ibinsav(ii),ii=1,5),rmax

	write(6,*)ireg,icount,ifil
	icolindex = icolindex+1

	endif

	if(icount.ge.1)then
	do it=1,isubtot
	sumd = 0
	sized = 0
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
	sized = sized +1
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


	write(21,*)(plotmatrix(it,iregindex)),plotmatrix(it+31,iregindex),isubjects(it),iregindex,ifil,cside(iregindex),ireg,cfnlabels(ireg)

	enddo  !it
	cregsav(iregindex) = cfnlabels(ireg)
	
		write(12,*)ireg,icount,regsize,size/regsize,sum/size,ifil,' ',c2dti,' ',cfnlabels(ireg),' ',cside(iregindex),' ',(90-(imax-1)),((jmax-1)-126),((kmax-1)-72),(dti(imax,jmax,kmax,it),it=1,isubtot),(tracts(imax,jmax,kmax,it),it=1,isubtot)
	write(6,*)ireg,icount,regsize,size/regsize,sum/size,ifil,' ',c2dti,' ',cfnlabels(ireg),' ',cside(iregindex),(90-(imax-1)),((jmax-1)-126),((kmax-1)-72)
	write(23,*)cplotlabel(1,iregindex),cside(iregindex),(90-(imax-1)),((jmax-1)-126),((kmax-1)-72),icount
	iregindex = iregindex+1
	endif

	enddo  !ireg


	do ii=1,iregindex-1
c
c average and stem for plotting
c
	do i=istartgr1,iendgr1
	dnmr(i) = plotmatrix(i,ii)
	enddo
	isize = iendgr1-istartgr1+1
	call average(aver1,stdev1,stem1,dnmr,isize)
c	write(22,*)aver,stem,ii,'1'
	do i=istartgr2,iendgr2
	dnmr2(i-iendgr1) = plotmatrix(i,ii)
	enddo
	isize2 = iendgr2-istartgr2+1
	call average(aver2,stdev2,stem2,dnmr2,isize2)
	
	call ttest(dnmr,dnmr2,isize,isize2,tfa)

c
c for mode
c
	do i=istartgr1,iendgr1
	dnmr(i) = plotmatrix(i+31,ii)
	enddo
	isize = iendgr1-istartgr1+1
	call average(avermod1,stdevmod1,stemmod1,dnmr,isize)
c	write(22,*)aver,stem,ii,'1'
	do i=istartgr2,iendgr2
	dnmr2(i-iendgr1) = plotmatrix(i+31,ii)
	enddo
	isize2 = iendgr2-istartgr2+1
	call average(avermod2,stdevmod2,stemmod2,dnmr2,isize2)

	
	call ttest(dnmr,dnmr2,isize,isize2,tmod)
c	write(22,*)cplotlabel(1,ii),aver1,'+/-',stem1,aver2,,'+/-',stem2,t,avermod1,,'+/-',stemmod1,avermod2,,'+/-',stemmod2,tmod
	write(22,22)cplotlabel(1,ii),aver1,'+',stem1,aver2,'+',stem2,tfa,tmod
	write(6,22)cplotlabel(1,ii),aver1,'+',stem1,aver2,'+',stem2,tfa,tmod
c	pause
c 22	format(a10,f5.2,a1,es6.1e1,f5.2,a1,es6.1e1,f6.2)
 22	format(a30,es7.1e1,a1,es6.1e1,es7.1e1,a1,es6.1e1,2f6.2)


	enddo  !ifil
	enddo  !iregindex

	close(12)
	close(22)
	close(23)
	
c end insert from vbm	

c
	stop
	end
c
	subroutine average(aver,stdev,stem,dnmr,isize)
	real dnmr(1000)
c
c
c
c	calculate the average
c
	sum=0
	do 40 i=1,isize
c	write(6,*)'dnmr in aver ',dnmr(i),i
 40	sum=dnmr(i)+sum
c
	aver=sum/isize
c	write(6,*)'average and size = ',aver,isize
c
c	calculate the standart deviation
c
	sum=0
	do 50 i=1,isize
 50	sum=sum + ((dnmr(i)-aver)**2)
c
	risize = isize
	stdev=sum/(risize-1)
	stdev = sqrt(stdev)
	risize=isize
	stem = stdev/sqrt(risize)
c	write(6,*)'standard deviation = ',stdev
c	write(6,*)'standard error in the mean = ',stem
c
	return
	end
c

	subroutine ttest(dnmr,dnmr2,isize,isize2,t)
	real dnmr(1000),dnmr2(1000),dnmr3(1000)
	integer isize,isize2
	real n_x,n_y,mu_x,mu_y
c
c	write(6,*)'isize isize2 ',isize,isize2
  	n_x  = isize
  	n_y  = isize2
  	df   = n_x + n_y - 2
	sumx = 0
	sumy = 0
	do i=1,isize
	sumx = sumx+dnmr(i)
	enddo

	do i=1,isize2
	sumy = sumy+dnmr2(i)
	enddo

  	mu_x = sumx/ n_x
  	mu_y = sumy / n_y

	sumsqx = 0
	sumsqy = 0
	do i=1,isize
	sumsqx = sumsqx+(dnmr(i)-mu_x)**2
	enddo

	do i=1,isize2
	sumsqy = sumsqy+(dnmr2(i)-mu_y)**2
	enddo

  	v    = sumsqx + sumsqy
  	t    = (mu_x - mu_y) * sqrt ((n_x * n_y * df) / (v * (n_x + n_y)))
	return
	end
c
c correlation
c
	subroutine correlation(dnmr,behav1,rcorr,itsize)
	real dnmr(2000),behav1(2000)
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
