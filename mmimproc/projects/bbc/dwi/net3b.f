c
c
	integer*1 iheader(128),iset1(48),iset2(48)
	integer*2 ifin(64),aver(512,24),iend(384),itrial(200,64)
	integer*2 iselect(5),d
	real iraw2(1000,4,2), sum(24,4,2),sumsq(24,4,2),t(24,4)
	real iraw3(512,24,128), iraw(512,24,128)
	common /iraw3pass/iraw3
	real cja(6),cjb(7),cjc(512),cju(512),stdev(2)
	real arx(512,20),bb(30),aparam
	common /deegpass/peeg(1000,2),deeg(1000,2),psize(2)
	real aver2(512,24),denom,r1,r2,phi2sq ,phi1,phi2
	real iraw2p(512,64,5),rsave(10000)
	real sumft(5),sumfth(5)
	real flicker(192,2),falpha(192),static(192,2),salpha(192)
	common /iraw2pass/iraw2p
	common /rsavepass/rsave
	common /arxpass/arx,aparam,bb
	common /fstatuspass/fstatus(5,2)
	common /critpass/critical
	common /istartpass/istartsav
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/imsize1,imsize2
	common /aver3pass/aver3(512,6,4)
	common /cfnpass/cfnp
	character*40 cfnin,cfnsav,cfn,cfnp
	character*2 ich2
	character*3 ich3,ich3a
	character*4 ich4
	character*8 ich8
	character*7 c7
	character*1 ctest
	include 'nmrpar.f'
	equivalence(ifin,iset2)
		rfactor = 1000.0/512.0
	iprint = 1
	open(30,file = 'mnet.out',status='new')
	open(39,file = 'fstatus.out',status='new')
	open(45,file = '011502-11001-arxoff-512.txtb',status='new')
	do iavind=1,5
	if(iavind.eq.1)av = 1
	if(iavind.eq.2)av = 4
	if(iavind.eq.3)av = 8
	if(iavind.eq.4)av = 12
	if(iavind.eq.5)av = 16
c	read(13,*)cfnsav
c	write(6,*)cfnsav
c	write(6,*)'enter the width and the offset '
c	read(5,*)rwidth, roffset
	rwidth = 50
	roffset = 600
c	write(6,*)'enter the input file name '
c	read(5,*)cfn
c	write(6,*)'which raw trace do you want? '
c	read(5,*)irawchoice
c	write(6,*)'how many pixels do you want to filter? '
c	read(5,*)ipnum
c	write(6,*)'starting at what pixel on the left side? '
c	read(5,*)ipstart
	irawchoice = 1
	ipnum = 2
	ipstart = 1
	do i=1,40
	cfnin(i:i) = ' '
	cfn(i:i) = ' '
	cfnsav(i:i) = ' '
	enddo
	cfnin(1:27)='MacintoshHD:net1:masterlist'
	open(42,file = 'sendtoclark1',status = 'new')
	open(43,file = 'sendtoclark2',status = 'new')

			open(41,file = cfnin,status = 'old')
 98	read(41,*,end = 99)ich8,istartsav
 	write(6,*)ich8,istartsav
c
c find out which ones are flicker and static
c
	do icall = 1,2
	do isub = 1,5
	if(icall.eq.1)then
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(1:4)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(1:4)
	cfn(31:37) = 'G1F.DAT'
	endif
	if(icall.eq.2)then
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(5:8)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(5:8)
	cfn(30:30) = '2'
	cfn(31:37) = 'G1F.DAT'
	endif
	if(isub.eq.1)cfn(32:32) = '1'
	if(isub.eq.2)cfn(32:32) = '2'
	if(isub.eq.3)cfn(32:32) = '3'
	if(isub.eq.4)cfn(32:32) = '4'
	if(isub.eq.5)cfn(32:32) = '5'
	cfn(38:38) = ' '
 2231	write(6,*)cfn
			cfnsav = cfn
c
 	open(11,file = cfn,form='unformatted', status = 'old',
	1	recordtype = 'stream',readonly,err = 2221)
	go to 2211
 2221	cfn(33:33) = 'S'
 	go to 2231
 2211	continue
 	close(11)
	ctest = cfnsav(33:33)
	if(ctest.eq.'F')fstatus(isub,icall) = 32
	if(ctest.eq.'S')fstatus(isub,icall) = 1
 	enddo
	write(6,*)'fstatus',(fstatus(ii,icall),ii=1,5),icall
	enddo
c
c create the file name
c
	do icall = 1,2
	incflick = 1
	incstat = 1
	do isub = 1,5
	if(icall.eq.1)then
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(1:4)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(1:4)
	cfn(31:37) = 'G1F.DAT'
	endif
	if(icall.eq.2)then
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(5:8)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(5:8)
	cfn(30:30) = '2'
	cfn(31:37) = 'G1F.DAT'
	endif
	if(isub.eq.1)cfn(32:32) = '1'
	if(isub.eq.2)cfn(32:32) = '2'
	if(isub.eq.3)cfn(32:32) = '3'
	if(isub.eq.4)cfn(32:32) = '4'
	if(isub.eq.5)cfn(32:32) = '5'
	cfn(38:38) = ' '
 223	write(6,*)cfn
			cfnsav = cfn
c			read(41,*)iaversize	!number of cycles of stimuli
	iaversize = 32
c			read(41,*)numep		!number of epochs per cycle
	numep = 2
c
c  calculate the time of the delay for the peak spatial frequency line
c
c
 	open(11,file = cfn,form='unformatted', status = 'old',
	1	recordtype = 'stream',readonly,err = 222)
	go to 221
 222	cfn(33:33) = 'S'
 	go to 223
 221	continue
c
	read(11)iheader
c
c  initialize average
c
	isize = 512
	isizehalf = isize/2
	do if=1,isize
	do i=1,24
	aver(if,i) = 0
	enddo
	enddo
	
	do it=1,iaversize*numep
c	write(6,*)'it ',it
	do if=1,isize
	read(11)iset1
	inc = 0
		do i=1,24
			do ii=1,2
			iset2(ii+inc)=iset1(3-ii+inc)
			enddo
		inc=inc+2
		enddo	!i
		
		do i=1,24
		iraw(if,i,it) = ifin(i)
c		if(it.eq.1)write(6,*)i,ifin(i),if
c		if(i.eq.24)write(6,*)i,ifin(i),if
		enddo	!i
		if(if.eq.isizehalf)then
		do ii = 1,8
		read(11)iset1
		enddo	!ii
		endif
	enddo	!if
		do ii = 1,8
		read(11)iset1
		enddo	!ii
	enddo	!iaverage
	close(11)
c
c
c
c average before the hit rate is taken
c
c
c convert to microvolts
	do i=1,24
	do it=1,(iaversize*numep)
	do if = 1,isize
	iraw(if,i,it) = iraw(if,i,it)*.076
	enddo
	enddo
	enddo
	iav = av
	itinc = 1
	do it=1,64,iav
	do if = 1,isize
		sumav = 0
		do itav=1,iav
		itst = itav+it-1
		r1 = iraw(if,5,itst)-iraw(if,11,itst)
		r3 = iraw(if,17,itst)-iraw(if,11,itst)
		temp = (r1+r3)/2.0
		sumav = temp+sumav
		enddo	!itav
	iraw3(if,5,itinc) = sumav/av
	iraw2p(if,itinc,isub) = iraw3(if,5,itinc)
	enddo	!if
	itinc=itinc+1
 	enddo	!it
	
	enddo	!isub
	
	call monte(av)
	
c
c
c create the file name
c
	incflick = 1
	incstat = 1
	do isub = 1,5
	if(icall.eq.1)then
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(1:4)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(1:4)
	cfn(31:37) = 'G1F.DAT'
	endif
	if(icall.eq.2)then
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(5:8)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(5:8)
	cfn(30:30) = '2'
	cfn(31:37) = 'G1F.DAT'
	endif
	if(isub.eq.1)cfn(32:32) = '1'
	if(isub.eq.2)cfn(32:32) = '2'
	if(isub.eq.3)cfn(32:32) = '3'
	if(isub.eq.4)cfn(32:32) = '4'
	if(isub.eq.5)cfn(32:32) = '5'
	cfn(38:38) = ' '
 1223	write(6,*)cfn
			cfnsav = cfn
c			read(41,*)iaversize	!number of cycles of stimuli
	iaversize = 32
c			read(41,*)numep		!number of epochs per cycle
	numep = 2
c
c  calculate the time of the delay for the peak spatial frequency line
c
c
 	open(11,file = cfn,form='unformatted', status = 'old',
	1	recordtype = 'stream',readonly,err = 1222)
	go to 1221
 1222	cfn(33:33) = 'S'
 	go to 1223
 1221	continue
c
	read(11)iheader
c
c  initialize average
c
	isize = 512
	isizehalf = isize/2
	do if=1,isize
	do i=1,24
	aver(if,i) = 0
	enddo
	enddo
	
	do it=1,iaversize*numep
c	write(6,*)'it ',it
	do if=1,isize
	read(11)iset1
	inc = 0
		do i=1,24
			do ii=1,2
			iset2(ii+inc)=iset1(3-ii+inc)
			enddo
		inc=inc+2
		enddo	!i
		
		do i=1,24
		iraw(if,i,it) = ifin(i)
c		if(it.eq.1)write(6,*)i,ifin(i),if
c		if(i.eq.24)write(6,*)i,ifin(i),if
		enddo	!i
		if(if.eq.isizehalf)then
		do ii = 1,8
		read(11)iset1
		enddo	!ii
		endif
	enddo	!if
		do ii = 1,8
		read(11)iset1
		enddo	!ii
	enddo	!iaverage
	close(11)
c
c average before the hit rate is taken
c
c
c convert to microvolts
	do i=1,24
	do it=1,(iaversize*numep)
	do if = 1,isize
	iraw(if,i,it) = iraw(if,i,it)*.076
	enddo
	enddo
	enddo
	
	do it=1,(iaversize*numep)
	do if = 1,isize
	r1 = iraw(if,5,it)-iraw(if,11,it)
	r2 = iraw(if,5,it+1)-iraw(if,11,it+1)
	r3 = iraw(if,17,it)-iraw(if,11,it)
	r4 = iraw(if,17,it+1)-iraw(if,11,it+1)
	iraw3(if,5,it) = (r1+r3)/2.0
	enddo
 	enddo
c

c
	rinc = 0
	do if=1,isize
	aver2(if,5) = 0
	enddo
	rsize = 64

	do it=1,64
	do if=1,isize
		aver2(if,5) = aver2(if,5) + iraw3(if,5,it)
	enddo
	enddo
c
	do if=1,isize
		aver2(if,5) = aver2(if,5)/rsize
		aver3(if,isub,icall) = aver2(if,5)
	enddo
	iav = av
	itinc = 1
	do it=1,64,iav
	do if = 1,isize
		sumav = 0
		do itav=1,iav
		itst = itav+it-1
		r1 = iraw(if,5,itst)-iraw(if,11,itst)
		r3 = iraw(if,17,itst)-iraw(if,11,itst)
		temp = (r1+r3)/2.0
		sumav = temp+sumav
		enddo	!itav
	iraw3(if,5,itinc) = sumav/av
	enddo	!if
	itinc=itinc+1
 	enddo	!it
c
c output averaged file to disk
c
	cfn(35:37) = 'avg'

	open(31,file = cfn,status = 'new')
	rfactor = 1000.0/512.0
	do if=1,isize
		r1 = if
		rmsec = (r1*rfactor)-30+18.32
		write(31,*)rmsec,char(9),aver2(if,5),char(9),iraw3(if,5,1)
	enddo
	close(31)

c	open(31,file = 'cjc.out ',status = 'new')
	icj = 1
	do it=1,64/iav
c
c
c	
c peak
	sump = 0
	do if=1,isize
		sump = sump + (iraw3(if,5,it)**2)
	enddo
	
	rsize1 = 512
c	write(6,*)'isize for 80 to 180 ',rsize1
	
	call monte2(sump,pvalue)
c	write(6,*)'pvalue it ',pvalue, it
c
c	write(6,*)ctest, it
	if(fstatus(isub,icall).eq.32)then
	flicker(incflick,1) = sump
	flicker(incflick,2) = pvalue
	incflick = incflick+1
	endif	!ctest.eq.F
	
	if(fstatus(isub,icall).eq.1)then
	static(incstat,1) = sump
	static(incstat,2) = pvalue
	incstat = incstat+1
	endif	!ctest.eq.F
c
 198	format(1x,a10,i4,8f9.2)
c

	enddo	!do it
c	close(31)
	
	write(6,*)'incflick isub ',incflick,isub
c
	enddo 	!isub
	isizepass = 192/iav
	call pcombine(flicker,fchisq,isizepass)
	isizepass = 128/iav
	call pcombine(static,schisq,isizepass)
	write(6,*)'chisq ',fchisq,schisq
	do i=1,10000
	dnmr(i)= rsave(i)
	enddo
	isize = 10000
	call average(averp,stdevp,stem)
	do i=1,128/iav
	dnmr(i)= static(i,1)
	enddo
	isize = 128/iav
	call average(averst,stdevst,stem)
	write(6,*)'averst stdevst',averst,stdevst
	write(6,*)'averp stdevp',averp,stdevp

c
c  output file 
c
	fsumstat = 0
	icountflicker = 0
	
	do i=1,128/iav
	ietype = 1
	pthreshold = 0.05
	eff_size = (flicker(i,1)-averp)/stdevp
	fsumstat=fsumstat+flicker(i,1)
c	write(45,105)cfnsav(27:38),ietype,i,flicker(i,1),eff_size,flicker(i,2)
	write(6,105)cfnsav(27:38),ietype,i,flicker(i,1),eff_size,flicker(i,2)
	if(flicker(i,2).lt.pthreshold)icountflicker = icountflicker +1
c	write(6,*)'fl pthe ',flicker(i,2),pthreshold,icountflicker
	enddo
	ssumstat = 0
	icountstatic = 0
	do i=1,128/iav
	ietype = 2
	eff_size = (static(i,1)-averp)/stdevp
	ssumstat = ssumstat+static(i,1)
c	write(45,105)cfnsav(27:38),ietype,i,static(i,1),eff_size,static(i,2)
	write(6,105)cfnsav(27:38),ietype,i,static(i,1),eff_size,static(i,2)
	if(static(i,2).lt.pthreshold)icountstatic = icountstatic +1
	enddo
	write(46,104)cfnsav(27:38),averp,stdevp,fsumstat,fchisq,ssumstat,schisq
 104	format(1x,a11,6f12.2)
 105	format(1x,a11,2i5,3f10.2)
 106	format(1x,a11,6i5,1f10.2)
c	call receiver(ich8,icall)
c
c find peak amplitude
c
	peakampflicker = 0
	do if=1,512
		r1 = (aver3(if,1,icall) + aver3(if,3,icall))/2.0
		peakampflicker = max(peakampflicker,r1)
	enddo
	peakampstatic = 0
	do if=1,512
		r1 = (aver3(if,2,icall) + aver3(if,4,icall))/2.0
		peakampstatic = max(peakampstatic,r1)
	enddo

	iarx = 0
	i52 = 2
	numtst = 128/iav
	ietype = 1
	write(45,106)cfnsav(27:38),iav,iarx,i52,ietype,numtst,icountflicker,peakampflicker
	write(6,106)cfnsav(27:38),iav,iarx,i52,ietype,numtst,icountflicker,peakampflicker
	iarx = 0
	i52 = 2
	numtst = 128/iav
	ietype = 2
	write(45,106)cfnsav(27:38),iav,iarx,i52,ietype,numtst,icountstatic,peakampstatic
	write(6,106)cfnsav(27:38),iav,iarx,i52,ietype,numtst,icountstatic,peakampstatic
	enddo	!icall
	
	go to 98
 99	continue
 	close(41)
	enddo	!iavind
	close(45)
	stop
	end
	
	subroutine average(aver,stdev,stem)
	include 'nmrpar.f'
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
	subroutine FOURIER4
C	ROUTINE USED IN 2DFT ... THIS ROUTINE DOES NOT ZERO EXTENT
C
C
	include 'nmrpar.f'
	common /pkc/pk(100000),pki(100000)
C	TYPE *,'DNMR',(DNMR(I),I=1,30)
C
C	ZERO FILL
C
	rdiv=10.0
c	DO 10 I=1,ISIZE
c	PK(I)=0.
c 10	PKI(I)=0.
C
C	LOAD FID
C
	DO 11 I=1,ISIZE
	PK(I)=DNMR(I)
 11	PKI(I)=DNMR(I+(ISIZE))
C	TYPE *,'PK,PKI',PK(I),PKI(I)
C
	ie=1
C	TYPE *,'ISIZE INFFT',ISIZE
	N=ISIZE
	RN=N+1
	nu=alog(rn)/alog(2.)
C	TYPE *,'N',N,NU,IE
	call FFT(n,NU,IE)
C

	DO  14 I=1,N
	DNMR(I)=PK(i)
 14	DNMR(I+ISIZE)=PKI(i)
c
	RETURN
	end
c
	subroutine FOURIER5
C	ROUTINE USED IN 2DFT ... THIS ROUTINE DOES NOT ZERO EXTENT
C
C
	include 'nmrpar.f'
	common /pkc/pk(100000),pki(100000)
C	TYPE *,'DNMR',(DNMR(I),I=1,30)
C
C	ZERO FILL
C
	rdiv=10.0
c	DO 10 I=1,ISIZE
c	PK(I)=0.
c 10	PKI(I)=0.
C
C	LOAD FID
C
	DO 11 I=1,ISIZE
	PK(I)=DNMR(I)
 11	PKI(I)=DNMR(I+(ISIZE))
C	TYPE *,'PK,PKI',PK(I),PKI(I)
C
	ie=-1
C	TYPE *,'ISIZE INFFT',ISIZE
	N=ISIZE
	RN=N+1
	nu=alog(rn)/alog(2.)
C	TYPE *,'N',N,NU,IE
	call FFT(n,NU,IE)
C

	DO  14 I=1,N
	DNMR(I)=PK(i)
 14	DNMR(I+ISIZE)=PKI(i)
c
	RETURN
	END
	subroutine FFT(N,NU,IE)
	common /pkc/pk(100000),pki(100000)
C  A REAL ARRAY AND AN IMAGINARY ARRAY EACH OF DIMENSION N ARE INPUTS TO THIS
C  ROUTINE. NU IS THE POWER TO WHICH 2 IS RAISED TO GIVE N,I.E. N=2**NU
C  WHEN IE=+1, THE INVERSE TRANSFORM (E**+1) IS CALCULATED.
C  WHEN IE=-1, THE FORWARD TRANSFORM (E**-I) IS CALCULATED.
C  INITIALIZATION
	N2=N/2
	NU1=NU-1
	K=0
	DO 100 L=1,NU
 102	DO 101 I=1,N2
	P=IBITR(K/2**NU1,NU)
C  THE FUNCTION IBITR EFFECTS A BIT REVERSAL, E.G.,1011 REVERSED IS 1101
	ARG=6.283185*P/FLOAT(N)
C  THIS IS THE MAIN TWIDDLE PHASE SHIFT
	C=COS(ARG)
	S=SIN(ARG)
	IF (IE.GT.0) S=-S
	K1=K+1
	K1N2=K1+N2
	TPK=PK(K1N2)*C+PKI(K1N2)*S
	TPKI=PKI(K1N2)*C-PK(K1N2)*S
	PK(K1N2)=PK(K1)-TPK
	PKI(K1N2)=PKI(K1)-TPKI
	PK(K1)=PK(K1)+TPK
	PKI(K1)=PKI(K1)+TPKI
 101	K=K+1
	K=K+N2
	IF (K.LT.N) GO TO 102
	K=0
	NU1=NU1-1
 100	N2=N2/2
	DO 103 K=1,N
	I=IBITR(K-1,NU)+1
	IF (I.LE.K) GO TO 103
	TPK=PK(K)
	TPKI=PKI(K)
	PK(K)=PK(I)
	PKI(K)=PKI(I)
	PK(I)=TPK
	PKI(I)=TPKI
 103	CONTINUE
	IF (IE.LT.0) GO TO 104
	DO 105 K=1,N
	PK(K)=PK(K)/N
	PKI(K)=PKI(K)/N
 105	CONTINUE
 104	CONTINUE
	RETURN
	END
	FUNCTION IBITR(J,NU)
	J1=J
	IBITR=0
	DO 200 I=1,NU
	J2=J1/2
	IBITR=IBITR*2+(J1-2*J2)
 200	J1=J2
	RETURN
	END
c
c  find top average 
c
	subroutine findtop(avevep,avebase)
	common /deegpass/peeg(1000,2),deeg(1000,2),psize(2)
	real dtop(1000),aver(2)
c
c routine to average the top itop number of eeg intensities
c in both the vep range and in the baseline range
c
	do k=1,2
	aver(k) = 0
	itop = psize(k)
	do j=1,itop
	rmax = -1000000
	do i=1,psize(k)
	rmax = max(deeg(i,k),rmax)
	if(rmax.eq.deeg(i,k))imax = i
	enddo
	dtop(j) = deeg(imax,k)
	aver(k) = aver(k) + dtop(j)
	deeg(imax,k) = -100000
	enddo
	r1 = itop
		if(k.eq.1)avevep = aver(k)/r1
		if(k.eq.2)avebase = aver(k)/r1
	enddo
	return
	end
	

C
C	SUB FOR APODIZATION OF FID
C
	subroutine smooth
c
c  only works on the real half of the data
C
	include 'nmrpar.f'
c	write(6,*)'enter the number to average for each point '
c	read(5,*)naver
	naver = 10
C
C
	IDIM=ISIZE
	DO 10 I=1,IDIM-naver
	sum=0
		do ii=1,naver
		sum=dnmr(i+ii-1)+sum
		enddo
	raver = naver
	DNMR(I)=sum/raver
 10	continue
C
C
	RETURN
	END
C
c  find top average 
c
	subroutine findtop2(avevep,avebase)
	common /deegpass/peeg(1000,2),deeg(1000,2),psize(2)
	real dtop(1000),aver(2)
	itop = 5
c
c routine to average the top itop number of eeg intensities
c in both the vep range and in the baseline range
c
	do k=1,2
	sum = 0
	rinc = 0
		do i=1,psize(k)
			if(deeg(i,k).gt.0)then
			sum = sum+deeg(i,k)
			rinc = rinc+1
			endif
		enddo
		if(k.eq.1)avevep = sum/rinc
		if(k.eq.2)avebase = sum/rinc
	enddo
	return
	end
	
c
c
c  multiple regression
c
	subroutine mregression
	real sum(20,20),sums(20),sumsquare(20),a(30,30),b(30)
	real ab(30,30),stdev(30),bb(30),aver(30),r1
	real matrix1(30,30), matrix2(30,30), matrix3(30,30)
	real data(512,20),aparam
	common /arxpass/data,aparam,bb
c
c  put the x values in the first columns put the y values in the last column
c  for example if there are 4 columns of x put them in columns 1-4 and put y in 5
c
c
c	open(11,file = 'example4.2',status = 'old')
	icol = 14
	irow = 500
c	icol = 4
c	irow = 20
	do j=1,icol
	do i=1,irow
c	read(11,*)data(i,j)
c	write(6,*)'data ',data(i,j)
	enddo
	enddo
	
	do j2=1,icol
	do j1 = 1,icol
	sum(j1,j2) = 0
	sums(j1) = 0
	sumsquare(j1) = 0
	enddo
	enddo
	
	do j2 = 1,icol
	do j1 = 1,icol
	do i=1,irow
	r1 = data(i,j1)*data(i,j2)
	sum(j1,j2) = r1 + sum(j1,j2)
	enddo
	enddo
	enddo
	
	do j1=1,icol
	do i=1,irow
	sums(j1) = sums(j1)+data(i,j1)
	enddo
	enddo
	
	do j1=1,icol
	do i=1,irow
	sumsquare(j1) = sumsquare(j1)+(data(i,j1)**2)
	enddo
	enddo
	rn = irow
	do j1=1,icol
	r1 = sumsquare(j1)-(sums(j1)*sums(j1)/rn)
	stdev(j1) = sqrt(r1/(rn-1))
	aver(j1) = sums(j1)/rn
c	write(6,*)'stdev ',stdev(j1),j1
	enddo
c
c here is the matrix of correlation coefficients
c
	rn = irow
	do j2=1,icol
	do j1 = 1,icol
	r1 = sums(j1)
	r2 = sums(j2)
	r3 = sumsquare(j1)- (sums(j1)*sums(j1)/rn)
	r4 = sumsquare(j2)- (sums(j2)*sums(j2)/rn)
	r5 = sqrt(r3*r4)
c	write(6,*)'r1 ',r1,r2,r3,r4,r5,j1,j2
c	if(r5.ne.0)then
c	a(j1,j2) = (sum(j1,j2) -(r1*r2/rn))/r5
c	else
c	a(j1,j2) = 0
c	endif
c	write(6,*)'before ',(sum(j1,j2) -(r1*r2/rn))/r5,j1,j2
	a(j1,j2) = (sum(j1,j2) -(r1*r2/rn))/r5
	enddo
	enddo
	np = icol
c	do j2 = 1,icol
c	write(6,*)'beforein ',(a(j1,j2),j1=1,icol)
c	enddo
	call matrix_inversion ( A, NP )
c	write(6,*)'here is the inversion '
c	do j2 = 1,icol
c	write(6,*)'inverions ',(a(j1,j2),j1=1,icol)
c	enddo
c
c here is the matrix of correlation coefficients
c
	rn = irow
	do j2=1,icol
	do j1 = 1,icol
	r1 = sums(j1)
	r2 = sums(j2)
	r3 = sumsquare(j1)- (sums(j1)*sums(j1)/rn)
	r4 = sumsquare(j2)- (sums(j2)*sums(j2)/rn)
	r5 = sqrt(r3*r4)
	ab(j1,j2) = (sum(j1,j2) -(r1*r2/rn))/r5
c	write(6,*)(sum(j1,j2) -(r1*r2/rn))/r5,j1,j2
	enddo
	enddo
	np = icol-1
	do j2=1,icol
	do j1 = 1,icol
	a(j1,j2) = ab(j1,j2)
	enddo
	enddo
	call matrix_inversion ( A, NP )
c	write(6,*)'here is the inversion2'
	do j2 = 1,icol-1
c	write(5,*)(a(j1,j2),j1=1,icol-1)
	enddo
	
	l = icol-1
	n=l
	m=l
c  Calculate C = A * B
      DO 50 i = 1, L
          DO 40 j = 1, N
              Cij = 0
              DO 30 k = 1, M
                  Cij = Cij + (A(i,k) * ab(k,j))
   30         CONTINUE
              matrix3(i,j) = Cij
   40     CONTINUE
   50 CONTINUE

	sum2 = 0
	do j=1,icol
	do i=1,icol
	r1 = matrix3(i,j)*matrix3(i,j)
	if(i.ne.j)then
	sum2 =sum2 + r1
	endif
	enddo
	enddo
c	write(6,*)'sum2 ',sum2

	do j1 = 1,icol-1
	b(j1) = 0
	enddo
	
	do j2 = 1,icol-1
	do j1 = 1,icol-1
	b(j2) = b(j2)+ (a(j1,j2)*ab(j1,icol))
	enddo
	enddo
	
	do j2 = 1,icol-1
c	write(6,*)'b ',b(j2),j2
	bb(j2) = b(j2)*(stdev(icol)/stdev(j2))
c	write(6,*)'bb ',bb(j2),j2
	enddo
	sumt = 0
	do j2 = 1,icol-1
	sumt = sumt + (aver(j2)*bb(j2))
	enddo
	aparam = aver(icol) - sumt
c	write(6,*)'aparam ',aparam
	sumt2 = 0
	sumt3 = 0
	sumssreg = 0
	open(21,file = 'testarx.out',status = 'new')
	do i=1,irow
		sumt1= 0
	do j1 = 1,icol-1
	sumt1 = sumt1 + (bb(j1)*data(i,j1))
	enddo
	sumt1 = sumt1 + aparam
	sub = data(i,icol)-sumt1
	sumt2 = (sub*sub)+sumt2
	sumt3 = (sumt1*sumt1)+sumt3
	sumssreg = sumssreg + ((sumt1 - aver(icol))**2)
c	write(6,*)'yprime ',sumt3,sumt1,i
c	write(21,*)i,sumt1
	enddo
	close(21)
c	write(6,*)'sumt2 sumt3 ',sumt2,sumt3,sumssreg
	
	
	return
	end

	subroutine matrix_inversion ( A, NP )
      !-------------------------------------------------------------------------
      !
      !	      Taken from "Numeric recipes".  The original program was
      !       GAUSSJ which solves linear equations by the Gauss_Jordon
      !       elimination method.  Only the parts required to invert
      !	      matrices have been retained.
      !
      !	      J.P. Griffith  6/88
      !
      !-------------------------------------------------------------------------

      PARAMETER (NMAX=50)

      DIMENSION IPIV(30), INDXR(30), INDXC(30)
	  real a(30,30)

      n = np

      DO 11 J=1,N
        IPIV(J)=0
11    CONTINUE
      DO 22 I=1,N
        BIG=0.
        DO 13 J=1,N
          IF(IPIV(J).NE.1)THEN
            DO 12 K=1,N
              IF (IPIV(K).EQ.0) THEN
                IF (ABS(A(J,K)).GE.BIG)THEN
                  BIG=ABS(A(J,K))
                  IROW=J
                  ICOL=K
                ENDIF
              ELSE IF (IPIV(K).GT.1) THEN
                PAUSE 'Singular matrix'
              ENDIF
12          CONTINUE
          ENDIF
13      CONTINUE

        IPIV(ICOL)=IPIV(ICOL)+1
        IF (IROW.NE.ICOL) THEN
          DO 14 L=1,N
            DUM=A(IROW,L)
            A(IROW,L)=A(ICOL,L)
            A(ICOL,L)=DUM
14        CONTINUE
        ENDIF
        INDXR(I)=IROW
        INDXC(I)=ICOL
        IF (A(ICOL,ICOL).EQ.0.) PAUSE 'Singular matrix.'
        PIVINV=1./A(ICOL,ICOL)
        A(ICOL,ICOL)=1.
        DO 16 L=1,N
          A(ICOL,L)=A(ICOL,L)*PIVINV
16      CONTINUE
        DO 21 LL=1,N
          IF(LL.NE.ICOL)THEN
            DUM=A(LL,ICOL)
            A(LL,ICOL)=0.
            DO 18 L=1,N
              A(LL,L)=A(LL,L)-A(ICOL,L)*DUM
18          CONTINUE
          ENDIF
21      CONTINUE
22    CONTINUE
      DO 24 L=N,1,-1
        IF(INDXR(L).NE.INDXC(L))THEN
          DO 23 K=1,N
            DUM=A(K,INDXR(L))
            A(K,INDXR(L))=A(K,INDXC(L))
            A(K,INDXC(L))=DUM
23        CONTINUE
        ENDIF
24    CONTINUE
      RETURN
      END

	subroutine bldc (a,b,u,c)
c
cINPUT:
c	b	the beta's associated with the ensemble average
c	a	the beta's associated with this epoch's data
c	u	the ensemble average -- our template
c
cOUTPUT:
c	c	the estimated signal
c
c
	real b(7), a(6), u(512), c(512)
c
c
c We want to constuct a signal value 'c(t)' from 't' = 1 to 509
c
	do it = 1, 509
c
c	initialize c(it)
	c(it) = 0.0
c
c	The span of values from the ensemble average is
c	 from (it + 3) to (it - 3)
	istart = it + 3
c
c	but (it-3) may be < 1
	istop = MAX(1,(it-3))
	inc = 1
	do j = istart, istop, -1
		c(it) = c(it) + (b(inc) * u(j))
		inc = inc + 1
	enddo
c
c	The span of values from the output is
c	 from (it-1) to (it - 6)
	istart = it -1
c
c	If istart < 1 we dont use any output values
	if (istart .ge. 1) then
c
c	Now control for the number of values below ic that we should use
		istop = MAX(1,(it-6))
		inc = 1
		do j = istart, istop, -1
			c(it) = c(it) - (a(inc) * c(j))
			inc = inc + 1
		enddo
	endif
	enddo
	return
	end
c
c 
	subroutine receiver(ich8,icall,av)
	character*8 ich8
	character*40 cfn,cfnin
	integer*1 iheader(128),iset1(48),iset2(48)
	integer*2 ifin(64),iraw(512000,24),aver(512,24),iend(384)
	integer*2 iraw2(512,24,64,5),iselect(5)
	real iraw2p(512,64,5),rsave(10000)
	common /rsavepass/rsave
	common /iraw2pass/iraw2p
	real iraw3(512,24,512),irawtmp(512,24)
	real cja(6),cjb(7),cjc(512),cju(512),stdev(2)
	real arx(512,20),bb(30),aparam
	common /deegpass/peeg(1000,2),deeg(1000,2),psize(2)
	real aver2(512,24),denom,r1,r2,phi2sq ,phi1,phi2
	real iraw5(64,4,2), sum(24,4,2),sumsq(24,4,2),t(24,4)
	real flicker(192,2),falpha(192),static(192,2),salpha(192)
	common /fstatuspass/fstatus(5,2)
	common /arxpass/arx,aparam,bb
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /critpass/critical
	common /size/imsize1,imsize2
	common /aver3pass/aver3(512,6,4)
	common /istartpass/istartsav
	common /cfnpass/cfnp
	character*40 cfnp
	real sumft(5),sumfth(5)
	integer iflickertest(5)
	character*40 cfnsav,cfnsav2
	character*2 ich2
	character*3 ich3
	character*7 c7
	include 'nmrpar.f'
	equivalence(ifin,iset2)
c
c create the file name
c
	if(icall.eq.1)then
	cfnin(1:27)='MacintoshHD:net1:masterlist'
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(1:4)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(5:8)
	cfn(31:34) = ich8(1:4)
	cfn(30:30) = '2'
	cfn(34:34) = '2'
	cfn(35:38) = '.DAT'
	cfn(39:40) ='  '
	endif
	if(icall.eq.2)then
		cfnin(1:27)='MacintoshHD:net1:masterlist'
	cfn(1:17)= cfnin(1:17)
	cfn(18:21) = ich8(5:8)
	cfn(22:25) = '.ZI0'
	cfn(26:26) = ':'
	cfn(27:30) = ich8(1:4)
	cfn(31:34) = ich8(5:8)
	cfn(35:38) = '.DAT'
	cfn(39:40) ='  '
	endif
	write(6,*)cfn
	write(39,*)cfn
	cfnsav = cfn
	open(11,file = cfn,form='unformatted', status = 'old',
	1	recordtype = 'stream',readonly)
	read(11)iheader
c
c  initialize average
c
	isizebig = 512000
	isize = 512
	isizehalf = isize/2
	do if=1,isize
	do i=1,24
	aver(if,i) = 0
	enddo
	enddo
	
	iaversize = 250
	numep = 2
	
	ifinc = 1
	do it = 1,500
c	write(6,*)'it ',it

	do if=1,isize
	read(11)iset1
	inc = 0
		do i=1,24
			do ii=1,2
			iset2(ii+inc)=iset1(3-ii+inc)
			enddo
		inc=inc+2
		enddo	!i
		
		do i=1,24
		iraw(ifinc,i) = ifin(i)
		if(it.eq.50)irawtmp(if,i)=ifin(i)
c		if(it.eq.1)write(6,*)i,ifin(i),if
c		if(i.eq.24)write(6,*)i,ifin(i),if
		enddo	!i
		ifinc = ifinc+1
		if(if.eq.isizehalf)then
		do ii = 1,8
		read(11)iset1
		enddo	!ii
		endif
	enddo	!if
		do ii = 1,8
		read(11)iset1
		enddo	!ii
	if(it.eq.50)then
		open(27,file = 'a1offset',status = 'new')
		do if=1,isize
		write(27,*)if,char(9),irawtmp(if,22)
		enddo
		close(27)
	endif

	enddo	!it
c
c average the flips
c
c
	open(26,file = 'a2channel.1',status = 'new')
	do if = 6000,9000
	write(26,100)if,char(9),iraw(if,21),char(9),iraw(if,22),
	1	char(9),iraw(if,23),char(9),iraw(if,24)
c	if(iraw(if,22).gt.70)write(6,*)'over',if,iraw(if,22)
	enddo
 100	format(1x,i6,4(a1,f10.3))
	close(26)
c
	do if=1,isizebig
	iraw(if,22) = iraw(if,22)+iraw(if,23)+iraw(if,24)
	enddo
c
c
c  first find the on conditions
c
	numskip = (512*64)

	if(icall.eq.1)isset = 2
	if(icall.eq.2)isset = 1
	do i=1,5
	iflickertest(i) = fstatus(i,isset)
	enddo

c  now sort for iraw
c
	icontinue = istartsav
	write(6,*)'istartsav ',istartsav
	icond = 1
 1003	continue
c
	if(iflickertest(icond).eq.32)then
	do if=icontinue,icontinue+20000
		if(iraw(if,22).gt.130)then
		itmp = if
		go to 1005
		endif
	enddo
 1005	continue
	imax = 0
	do i=itmp-540,itmp-480
	imax = max(iraw(i,22),imax)
	if(imax.eq.iraw(i,22))istart = i
	enddo
	endif	!iflicker on
c
	if(iflickertest(icond).eq.1)then
	itmp=icontinue
		imax=0
		do i=itmp+numskip-100,itmp+numskip+5000
		imax = max(iraw(i,22),imax)
		if(imax.eq.iraw(i,22))iendd = i
		enddo
c		write(6,*)'iendd ',iendd
		imax = 0
		do i=iendd-32790,iendd-32700
		imax = max(iraw(i,22),imax)
		if(imax.eq.iraw(i,22))istart = i
		enddo
	endif
	
 	icheck = istart
	 	icount = 0
 1000	continue
		if(iraw(icheck,22).gt.130)then
			icount = icount+1
			icheck = icheck+800
		endif
	icheck = icheck+1
	if(icheck.gt.istart+numskip+100)go to 1002
	go to 1000
 1002 continue
 	write(6,*)'icount istart imax ',icount,istart,imax,icond
 	write(39,*)'icount istart imax ',icount,istart,imax,icond
	ic = istart
	do it2=1,64
	do if2=1,512
		do i=1,24
		iraw2(if2,i,it2,icond) = iraw(ic,i)
		enddo
		ic = ic+1
	enddo	!if2
	enddo	!it2
	icontinue = ic+1000
	icond = icond+1
	if(icond.eq.6)go to 1004
	go to 1003

 1004	continue
c
c test output
c
c
c  test for static only
 322	continue
	write(6,*)'iflickertest ',iflickertest
c
c	do icond=1,5
c	if(icond.le.3)ifstart = 48996+(icond*200)
c	if(icond.gt.3)ifstart = 156315+(icond*200)
c	if = ifstart
c	do it2=1,64
c	do if2=1,512
c		do i=1,24
c		iraw2(if2,i,it2,icond) = iraw(if,i)
c		enddo
c		if = if+1
c	enddo
c	enddo
c	enddo
c
	incflick = 1
	incstat = 1
	do icond = 1,5
c
c average before the hit rate is taken
c
c
c convert to microvolts
	do i=1,24
	do it=1,64
	do if = 1,isize
	iraw3(if,i,it) = iraw2(if,i,it,icond)*.076
	enddo
	enddo
	enddo

	iav = av
	itinc = 1
	do it=1,64,iav
	do if = 1,isize
		sumav = 0
		do itav=1,iav
		itst = itav+it-1
		r1 = iraw3(if,5,itst)-iraw3(if,11,itst)
		r3 = iraw3(if,17,itst)-iraw3(if,11,itst)
		temp = (r1+r3)/2.0
		sumav = temp+sumav
		enddo	!itav
	iraw2(if,5,itinc,icond) = sumav/av
	iraw2p(if,itinc,icond) = iraw2(if,5,itinc,icond)
	enddo	!if
	itinc=itinc+1
 	enddo	!it
	
	enddo	!isub
	
	call monte(av)

	
	incflick = 1
	incstat = 1
	do icond = 1,5

	cfn(36:38) = 'avg'
	if(icond.eq.1) cfn(36:36) = '1'
	if(icond.eq.1) cfnsav(36:36) = '1'
	if(icond.eq.2) cfn(36:36) = '2'
	if(icond.eq.2) cfnsav(36:36) = '2'
	if(icond.eq.3) cfn(36:36) = '3'
	if(icond.eq.3) cfnsav(36:36) = '3'
	if(icond.eq.4) cfn(36:36) = '4'
	if(icond.eq.4) cfnsav(36:36) = '4'
	if(icond.eq.5) cfn(36:36) = '5'
	if(icond.eq.5) cfnsav(36:36) = '5'
	write(6,*)cfnsav
c	
	do it=1,64/iav
c
c
c	
c peak
	sump = 0
	do if=1,isize
		sump = sump + (iraw2(if,5,it,icond)**2)
	enddo
	
	rsize1 = 512
c	write(6,*)'isize for 80 to 180 ',rsize1
	
	call monte2(sump,pvalue)
c	write(6,*)'pvalue it ',pvalue, it
c
	if(fstatus(icond,icall).eq.32)then
	flicker(incflick,1) = sump
	flicker(incflick,2) = pvalue
	incflick = incflick+1
	endif	!ctest.eq.F
	
	if(fstatus(icond,icall).eq.1)then
	static(incstat,1) = sump
	static(incstat,2) = pvalue
	incstat = incstat+1
	endif	!ctest.eq.F
c
 198	format(1x,a10,i4,8f9.2)
c

	enddo	!do it
c	close(31)
	
	write(6,*)'incflick isub ',incflick,isub
c
	enddo 	!icond
c
	isizepass = 192/iav
	call pcombine(flicker,fchisq,isizepass)
	isizepass = 128/iav
	call pcombine(static,schisq,isizepass)
	write(6,*)'chisq ',fchisq,schisq
	do i=1,10000
	dnmr(i)= rsave(i)
	enddo
	isize = 10000
	call average(averp,stdevp,stem)
	do i=1,128/iav
	dnmr(i)= static(i,1)
	enddo
	isize = 128/iav
	call average(averst,stdevst,stem)
	write(6,*)'averst stdevst',averst,stdevst
	write(6,*)'averp stdevp',averp,stdevp

c
c  output file 
c
	fsumstat = 0
	do i=1,192/iav
	ietype = 1
	eff_size = (flicker(i,1)-averp)/stdevp
	fsumstat=fsumstat+flicker(i,1)
	write(45,105)cfnsav(27:38),ietype,i,flicker(i,1),eff_size,flicker(i,2)
	write(6,105)cfnsav(27:38),ietype,i,flicker(i,1),eff_size,flicker(i,2)
	enddo
	ssumstat = 0
	do i=1,128/iav
	ietype = 2
	eff_size = (static(i,1)-averp)/stdevp
	ssumstat = ssumstat+static(i,1)
	write(45,105)cfnsav(27:38),ietype,i,static(i,1),eff_size,static(i,2)
	write(6,105)cfnsav(27:38),ietype,i,static(i,1),eff_size,static(i,2)
	enddo
	write(46,104)cfnsav(27:38),averp,stdevp,fsumstat,fchisq,ssumstat,schisq
 104	format(1x,a11,6f12.2)
 105	format(1x,a11,2i5,3f10.2)
	if(icall.eq.1)cfnp(1:11) = cfnsav(27:38)
	if(icall.eq.2)cfnp(12:23) = cfnsav(27:38)
	return
	end
c
	subroutine heartmath
	integer*2 ixreg(2000)
	real xreg(2000)
	include 'nmrpar.f'
c
c
c find the heart beats
c
	ioutrange = 512*64
	rmax = 1300
	inc = 1
 		if = 1
 988	if(dnmr(if).gt.rmax)then
	ixreg(inc) = if
	inc = inc+1
c	write(6,*)'ixreg if',if
	if = if+250
	if(if.gt.ioutrange-10)go to 989
	endif
	if= if+1
	if(if.gt.ioutrange-10)go to 989
	go to 988
 989	continue
	isizeix = inc-1
c	open(22,file = 'testxreg',status = 'new')
	do i=1,isizeix-1
	xreg(i) = ixreg(i+1)-ixreg(i)
c	write(22,*)i,xreg(i)
	enddo
c	close(22)
c
	do ii=1,isizeix-1
		diff = xreg(ii+1)-xreg(ii)
		rinc = diff/xreg(ii)
	do if=ixreg(ii),ixreg(ii+1)
	r1 = (if-ixreg(ii))
	dnmr(if) = xreg(ii)+(r1*rinc)
	enddo
	enddo
c
	sum = 0
	do i=1001,30000
	sum = sum+dnmr(i)
	enddo
	aver = sum/(29000.0)
	do if=1,ixreg(1)
	dnmr(if) = xreg(1)
	enddo
	do if=1,ioutrange
	dnmr(if) = dnmr(if)-aver
	enddo
	do if=ioutrange+1,ioutrange*2
	dnmr(if) = 0
	enddo
	do if=30000,ioutrange
	dnmr(if) = 0
	enddo
	
	return
	end
C
C
	SUBROUTINE POWER
C
	include 'nmrpar.f'
C
	TC=-LB
C
	DO 10 I=1,ISIZE
 10     DNMR(I)=(DNMR(I)**2  + DNMR(I+ISIZE)**2)**.5
C
C
	RETURN
	END
c
c sort routine
c
	subroutine meandiff(static,flicker,isizepass1,isizepass2,qdiff)
	real static(192), flicker(192)
	
c
	sum = 0
	do i=1,isizepass1
	sum = sum+static(i)
	enddo
	rsize1 = isizepass1
	aver1 = sum/rsize1
c
	sum = 0
	do i=1,isizepass2
	sum = sum+flicker(i)
	enddo
	rsize2 = isizepass2
	aver2 = sum/rsize2
c
	qdiff = aver2-aver1

	return
	end
	
	subroutine sort1(apass,isize,itest)
	real apass(192),rtmp(192),outarray(192)
	common /critpass/critical
	
c
c load rtmp
c
	do i=1,isize
	rtmp(i) = apass(i)
c	if(isize.eq.128.and.i.eq.50)write(6,*)'i rtmp input ',i,rtmp(i)
c	if(isize.eq.128.and.i.eq.51)write(6,*)'i rtmp input ',i,rtmp(i)
c	if(isize.eq.128.and.i.eq.52)write(6,*)'i rtmp input ',i,rtmp(i)
	enddo
c

	do inc = 1,isize
	rmax = 0
	do i=1,isize
		rmax = max(rmax,rtmp(i))
		if(rmax.eq.rtmp(i))itake = i
	enddo		!do i
	outarray(inc) = rtmp(itake)
	rtmp(itake) = 0
	
	enddo		!do inc 
	
	if(isize.eq.128)then
		critical = outarray(6) + (0.4*(outarray(7)-outarray(6)))
	endif
	itest = 1
	do i=1,isize
	if(outarray(i).gt.critical)itest = i
	enddo
	

	return
	end
	
c
c sort routine
c
	subroutine runtest(apass,isize,itest,zobs)
	real apass(192),rtmp(192),outarray(192)
	common /critpass/critical
	
c
c load rtmp
c
	do i=1,isize
	rtmp(i) = apass(i)
	enddo
c
	critical = .01

	rinc= 0
	tot = isize
	do i=1,isize
	if(apass(i).le.critical)then
		rtmp(i) = 1
		rinc = rinc+1
	endif
	if(apass(i).gt.critical)rtmp(i) = 0
	enddo		!do i
	test = rtmp(1)
	run = 1
	do i=2,isize
	if(rtmp(i).ne.test)then
	run = run+1
	test = rtmp(i)
	endif
c	write(6,*)'rtmp ',rtmp(i),i,run
	enddo
c
c calculate z score observed
	
	rn1 = rinc
	rn2 = tot - rn1
	r1 = 2*rn1*rn2
	rmean = (r1/tot) + 1
	r2 = (2*rn1*rn2) - rn1 -rn2
	r3 = tot*tot
	r4 = tot -1
	sd = sqrt((r1*r2)/(r3*r4))
	if(sd.ne.0)then
		zobs = (run - rmean)/sd
	else
		zobs = 0
	endif
c	write(6,*)'obs rn1 rmean sd run',rn1,rmean,sd,run
c
c calculate z score theoretical
c
	rn1 = 9.6
	rn2 = tot - rn1
	r1 = 2*rn1*rn2
	rmean = (r1/tot) + 1
	r2 = (2*rn1*rn2) - rn1 -rn2
	r3 = tot*tot
	r4 = tot -1
	sd = sqrt((r1*r2)/(r3*r4))
	if(sd.ne.0)then
		ztheor = (run - rmean)/sd
	else
		ztheor = 0
	endif
	ztheor = (run - rmean)/sd
c	write(6,*)'theor rn1 rmean sd run',rn1,rmean,sd,run
		

	return
	end
	
	
c
	subroutine ttest(t)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
C	CALCULATER AVERAGE AND STANDARD DEVIATION FOR INPUT
c	and student t
c
	real incv(2)
	dimension sdv(2),averv(2)
C
	isize1sav = isize1
	isize2sav = isize2
	df = isize1+isize2-2
	write(6,*)'degrees of freedom ',df
	incv(1) = isize1
	incv(2) = isize2
	call average2(averv(1),sdv(1),stem)
	write(6,*)'aver1 sdv, stem ',averv(1),sdv(1),stem,incv(1)
	isize1=isize2
	do i=1,isize1
	dmnmr(i)=dmnmr2(i)
	enddo
	call average2(averv(2),sdv(2),stem)
	write(6,*)'aver2 sdv, stem ',averv(2),sdv(2),stem,incv(2)
	sdv(1)=sdv(1)**2
	sdv(2)=sdv(2)**2
	ssqu=( incv(1) -1 )*sdv(1) + (incv(2) - 1) * sdv(2)
	ssqu= ssqu/(incv(1) + incv(2) -2)
	t = averv(1) - averv(2)
	denom = sqrt( (ssqu/incv(1)) + (ssqu/incv(2)) )
	t =abs( t/denom)
c	write(6,*)'ttest t value = ',t
	if(df.eq.4)then
		if(t.ge.2.77)write(6,*)'SIGINIFICANT '
	endif
	if(df.eq.7)then
		if(t.ge.2.365)write(6,*)'significant '
	endif
	if(df.eq.8)then
		if(t.ge.2.306)write(6,*)'significant '
	endif
	if(df.eq.9)then
		if(t.ge.2.262)write(6,*)'significant '
	endif
	if(df.eq.10)then
		if(t.ge.2.228)write(6,*)'significant '
	endif
	if(df.eq.11)then
		if(t.ge.2.201)write(6,*)'significant '
	endif
	if(df.eq.12)then
		if(t.ge.2.179)write(6,*)'significant '
	endif
	if(df.eq.13)then
		if(t.ge.2.160)write(6,*)'significant '
	endif
	if(df.eq.14)then
		if(t.ge.2.145)write(6,*)'significant '
	endif
	if(df.eq.15)then
		if(t.ge.2.131)write(6,*)'significant '
	endif
	if(df.eq.16)then
		if(t.ge.2.120)write(6,*)'significant '
	endif
	if(df.eq.28)then
		if(t.ge.2.048)write(6,*)'p<.05 '
		if(t.ge.2.467)write(6,*)'p<.02 '
		if(t.ge.2.763)write(6,*)'p<.01 '
		if(t.ge.3.047)write(6,*)'p<.005 '
		if(t.ge.3.408)write(6,*)'p<.002 '
		
	endif
	isize1 = isize1sav
	isize2 = isize2sav
	return
	end
c
	subroutine average2(aver,stdev,stem)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
c
c
c
c	calculate the average
c
	sum=0
	risize1 = isize1
	do 40 i=1,isize1
c	write(6,*)'dmnmr in aver ',dmnmr(i),i
 40	sum=dmnmr(i)+sum
c
	aver=sum/risize1
c	write(6,*)'average and size = ',aver,isize1
c
c	calculate the standart deviation
c
	sum=0
	do 50 i=1,isize1
 50	sum=sum + ((dmnmr(i)-aver)**2)
c
	risize1 = isize1
	stdev=sum/(risize1-1)
	stdev = sqrt(stdev)
	stem = stdev/sqrt(risize1)
c	write(6,*)'standard deviation = ',stdev
c	write(6,*)'standard error in the mean = ',stem
c
	return
	end

	subroutine mwtest(u1,u2,z)
	dimension area(1000,10),isize(10),size(2)
	dimension rank(1000,10),sum(10),sumr(10)
	dimension rank1(1000,10),sumr1(10),rank2(1000),area2(1000)
	dimension rnewrank(1000),areasav(1000,10),area3(1000),count(1000)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isizep,isizep2
	isize(1) = isizep
	isize(2) = isizep2
c
c	write(6,*)'areas here ',isize(1),isize(2)
	igroups = 2
	do if=1,igroups
		do i=1,isize(if)
		if(if.eq.1)area(i,if) = dmnmr(i)
		if(if.eq.2)area(i,if) = dmnmr2(i)
c		write(6,*)'area isize i',area(i,if),isize(if),i
		enddo
	enddo
	size(1)=isize(1)
	size(2)=isize(2)
c
c save
c
	do if=1,igroups
	do i=1,isize(if)
	areasav(i,if) = area(i,if)
c	write(6,*)'area i if',areasav(i,if),i,if
	enddo
	enddo
c
c
c find the rank
c
c
	itot=isize(1)+isize(2)
c	write(6,*)'itot ',itot
	do 190 irank=1,itot
	ymax=-1000000.
	do if=1,igroups
	  do  i=1,isize(if)
	  ymax=max(area(i,if),ymax)
	  if(area(i,if).eq.ymax)then
	    itmp=i
	    iftmp=if
	  endif
	enddo
	enddo
c
c	write(6,*)'irank area ',irank,areasav(itmp,iftmp),itot-irank+1
	rank2(irank) = irank
	area2(irank) = area(itmp,iftmp)
	rank(itmp,iftmp)=irank
	rank1(itmp,iftmp)=itot-irank+1
	area(itmp,iftmp) = -10000
 190	continue
 	do if=1,igroups
	do i=1,isize(if)
	area(i,if) = areasav(i,if)
c	write(6,*)'area i if',areasav(i,if),i,if
	enddo
	enddo

	jinc=1
	do 90 irank=1,itot
	ymax=-1000000.
	do 100 if=1,igroups
	  do 101 i=1,isize(if)
	  ymax=max(area(i,if),ymax)
	  if(area(i,if).eq.ymax)then
	    itmp=i
	    iftmp=if
	  endif
 101	continue
 100	continue
c
c count how many of each
	inc=0
	do if=1,igroups
	do i=1,isize(if)
	if(area(i,if).eq.ymax)then
		area(i,if)= -10000
		inc=inc+1
	endif
	enddo
	enddo
	if(ymax.ne.-10000)then
	area3(jinc) = ymax
	count(jinc) = inc
c	write(6,*)'area3 count jinc ',area3(jinc),count(jinc),jinc
	jinc=jinc+1
	endif
 90	continue
	do i=1,itot
c	write(6,*)'rank area ',rank2(i),area2(i)
	enddo
c
c  find the number of ties
c
	jsize = jinc-1
c  find the number of ties
c
	do j=1,jsize
	sum2 = 0
	rinc = 0
		do i=1,itot
		if(area2(i).eq.area3(j))then
		sum2 = sum2 + rank2(i)
		rinc = rinc+1
		endif
		enddo
	rnewrank(j) = sum2/rinc
	do if=1,2
	do i=1,isize(if)
		if(areasav(i,if).eq.area3(j))then
		rank(i,if) = rnewrank(j)
		rank1(i,if) = itot - rank(i,if) +1
		endif
	enddo
	enddo
	enddo
c
c
	do if=1,2
	do i=1,isize(if)
c	write(6,*)'area rankf ',areasav(i,if),rank(i,if)
	enddo
	enddo
c
c  sum the ranks
c
	do 15 if=1,igroups
	sumr(if)=0
	sumr1(if)=0
	do 110 i=1,isize(if)
c	write(6,*)'rank ',rank(i,if),i,if
c	write(6,*)'rank1 ',rank1(i,if),i,if
 	sumr(if)=sumr(if)+rank(i,if)
 110	sumr1(if)=sumr1(if)+rank1(i,if)
 15	continue
c
c	write(6,*)'sumr ', sumr(1),sumr(2)
c	write(6,*)'sumr1 ', sumr1(1),sumr1(2)
c	write(6,*)'isize ', isize(1),isize(2)
c
c
c  calculate U values
c
	u1= (size(1)*size(2)) + (size(1)*((size(1)+1)/2)) - sumr(1)
	u1b= (size(1)*size(2)) + (size(1)*((size(1)+1)/2)) - sumr1(1)
c
	u2 = (size(1)*size(2)) - u1
	u2b = (size(1)*size(2)) - u1b
	r1 = size(1)*size(2)*(size(1)+size(2)+1)
	bottom = sqrt(r1/12.0)
	if(u1.lt.u2)top = (u1- (size(1)*size(2)/2.0))
	if(u1.gt.u2)top = (u2- (size(1)*size(2)/2.0))
	z = top/bottom
c
c	write(6,*)'Use the largest of the 4 values for table page 550 '
c	write(6,*)'in Zar'
c	write(6,*)'u1 u2 ',u1,u2
c	write(6,*)'u1b u2b ',u1b,u2b
c
	if(isize(1).eq.15.and.isize(2).eq.15)then
	if(u1.ge.161.or.u2.ge.161)write(6,*)'significant '
	endif
	if(isize(1).eq.14.and.isize(2).eq.15)then
	if(u1.ge.151.or.u2.ge.151)write(6,*)'significant '
	endif
	if(isize(1).eq.15.and.isize(2).eq.14)then
	if(u1.ge.151.or.u2.ge.151)write(6,*)'significant '
	endif
	if(isize(1).eq.14.and.isize(2).eq.14)then
	if(u1.ge.141.or.u2.ge.141)write(6,*)'significant '
	endif
	return
	end
c
c
c  sub to output the average ensemble for all 4 
c
	subroutine averoutput
	common /aver3pass/aver3(512,6,4)
	common /cfnpass/cfnp
	character*40 cfnsav,cfn,cfnp
	
c
	do j=1,2

	if(j.eq.2)cfn(1:11) = cfnp(1:11)
	if(j.eq.1)cfn(1:11) = cfnp(12:23)
	cfn(12:15)= '.av3'
	do i=16,40
	cfn(i:i) = ' '
	enddo

	open(18+j,file = cfn,status = 'new',recl = 256)
 	enddo
 100	format(1x,f8.3,10(a1,f8.3))
 	do j=1,4
 	do i=1,512
c	aver3(i,1,j) = (aver3(i,1,j)+aver3(i,3,j)+aver3(i,5,j))/3.0
	aver3(i,1,j) = (aver3(i,1,j)+aver3(i,3,j))/2.0
	aver3(i,2,j) = (aver3(i,2,j)+aver3(i,4,j))/2.0
	enddo
	enddo

	
	do j=1,2
	if(j.eq.1)ire = 4
	if(j.eq.2)ire = 3
	do if=1,512
	write(18+j,100)aver3(if,6,1),((char(9),aver3(if,ii,j)), ii=1,2),
	1	((char(9),aver3(if,ii,ire)), ii=1,2)
	enddo	!if
	enddo	!j
	close(19)
	close(20)
	return
	end

c
c  subroutine to calculate the monte carlo of the static conditions
c
	subroutine monte(av)	
	common /iraw2pass/iraw2p
	common /rsavepass/rsave
	real iraw2p(512,64,5)
	real staticall(65536)
	real rsave(10000)
	
	iav = av
	inc=1
	do it = 1,64/iav
	do if=1,512
	staticall(inc) = iraw2p(if,it,2)
	inc=inc+1
	enddo
	enddo
	
	do it = 1,64/iav
	do if=1,512
	staticall(inc) = iraw2p(if,it,4)
	inc = inc+1
	enddo
	enddo
	
c  now  take out random samples 
c
	open(28,file='rndnumb.txt',status = 'old')
	scalefactor = 64000/av
	do iter=1,10000
	read(28,*)rand1
	rand1 = (rand1*scalefactor)+1
	istart = rand1
	inc2 = 0
	sum = 0
		do if=istart,istart+511
		sum = sum + (staticall(if)**2)
		inc2 = inc2+1
		enddo
	rsave(iter) = sum
c	write(6,*)'iter rsave inc2 ',iter,rsave(iter),inc2
	enddo		!iter
	close(28)
	return
	end
	
c
c  subroutine to calculate the monte carlo of the static conditions
c
	subroutine monte2(sum,pvalue)	
	common /iraw2pass/iraw2p
	common /rsavepass/rsave
	real iraw2p(512,64,5)
	real staticall(65536)
	real rsave(10000)
	
	rinc = 0
	do i=1,10000
	if(rsave(i).ge.sum)rinc = rinc+1
	enddo
	total = 10000
	pvalue = rinc/total
	if(pvalue.eq.0)pvalue = 0.0001
	return
	end

c
c  use fishers combined p value equation
c
	subroutine pcombine(apass,chisq,isize)
	real apass(192,2)
	sum = 0
	do i=1,isize
	sum = sum + log(apass(i,2))
c	write(6,*)'sum apass ',sum,apass(i),i
	enddo
	chisq = -2.0 * sum
	return
	end

