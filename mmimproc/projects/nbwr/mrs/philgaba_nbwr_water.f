

	integer*1 inmr(32768),inmr2(32768),inmr8(16384)
	character*1 cnmr(32768),chchold(2769),cnum,c2nmr(32768)
	equivalence (inmr,cnmr)
	integer*1 chold(2769)
	equivalence (chold,chchold)
	real nmr(8192),subsav(4096)
	equivalence (nmr,inmr2)
	equivalence (nmr,c2nmr)
	real imagef(8192,160),im2(8192,160)
	character*80 cfn,cfnout
	character*80 ctext(100)
	character*1 con(100),con200(1800)
	integer*1 icon(100),icon200(1800)
	integer*2 nrowsav(100)
	equivalence (con,icon)
	equivalence (con200,icon200)
	include 'nmrpar.f'
	  character*1 cend,cisl,cecho
	character*6 cline1
	character*11 cline2
	character*18 cline3
	character*34 cline4
	character*5 cline5
	character*4 c4,ans1,ans2
	character*9 c8
	character*1 c1
	common /pkc/pk(100000),pki(100000)
	common /gf/ gfilter(2048)
        logical ibtest
        real t2f(500)
        open(61,file='shift.txt')
	
	it2counter = 1
	jpass = 1
	open(31,file = 't2values.txt')

	rlb = 1
	open(12,file = './filesdat.txt',form='unformatted')
	do i=1,1800
	call FGETC(12,con200(i),istate)
	if(icon200(i).eq.13)icon200(i)=32
	enddo
	close(12)
	open(12,file='./filesdat2.txt',form='unformatted')
		do i=1,1800
	call FPUTC(12,con200(i),istate)
	enddo
	close(12)
	open(21,file='./filesdat2.txt')

 98	continue
	do i=1,80
	cfn(i:i)=' '
	cfn2(i:i) = ' '
	cfnout(i:i) = ' '
	enddo


 	read(21,*)cfn,isize,nrows,sf,te,tr,ans1,ans2

	sf = 2000
	isize = 2048

 	write(6,*)'dat ',isize,nrows,sf,te,tr,ans1,ans2
	nrowsav(it2counter)= nrows
	isizeold = isize

	rinfo(2) = sf

	do i=1,80
	if(cfn(i:i).eq.'.')iper= i
	enddo
c
c read in par file to change rows
c
	cfn2 = cfn
	write(6,*)'cfn ',cfn
	open(41,file=cfn,form='unformatted')
	do irow = 1,nrows
	isize2 = isize*4
	do i=1,isize*8
	call FGETC(41,cnmr(i),istate)
	enddo
c	if(isize.eq.2048)read(41)inmr
	inc=1
	do i=1,isize*2
	inmr2(inc)=inmr(inc+3)
	inmr2(inc+1)=inmr(inc+2)
	inmr2(inc+2)=inmr(inc)
	inmr2(inc+3)=inmr(inc+1)
	inc=inc+4
	enddo

	do i=1,isize*2
	imagef(i,irow) = nmr(i)
	enddo
	write(6,*)'imagef1 ',imagef(2,irow),irow
	enddo	!nrows
	close(41)
	open(22,file = '2doutpre.img',form='unformatted')
	do irow = 1,nrows
	   do i=1,isize*2
	      nmr(i)=imagef(i,irow)
	      enddo
	do i=1,isize*8
	call FPUTC(22,c2nmr(i),istate)
	enddo  !i
	enddo  !irow
	close(22)
	open(23,file = 'testpre.txt')
	do i=1,isize*2,2
	   write(23,*)imagef(i,2)
	   enddo
	   close(23)
	open(23,file = 'testpre3.txt')
	do i=1,isize*2,2
	   write(23,*)imagef(i,3)
	   enddo
	   close(23)
c
c pair wise subtraction
c
	do irow=1,nrows
	inc=1
	   do i=2,isize*2,2
	      im2(inc,irow)= imagef(i,irow)
	      inc = inc+1
	      enddo
		inc = 1
	   do i=1,isize*2,2
	      im2(inc+isize,irow)= imagef(i,irow)
	      inc = inc+1
	      enddo
	enddo
	open(23,file = 'testpair.txt')
	do irow=1,nrows,2
	do i=1,isize*2
c	dnmr(i) = (im2(i,irow)-im2(i,irow+1))+dnmr(i)
	dnmr(i) = (im2(i,irow))
	enddo
	rlb = 0.5
	call apod
	call fourier3
	call phasenaa(inaa)

	do i=900,1100
	write(23,*)dnmr(i)
	enddo

	enddo

	close(23)
c
c average for the two types of signals
c
	do i=1,isize*2
	dsav(i) = im2(i,1)
	enddo


c
c output as separate lcmo files
c
c**
 31	format(2e15.6)
	open(22,file = 'water.lcmo')
	cline1 = '$NMID'
	cline2 = "ID='e1001'"
	cline3 = "fmtdat='(2e15.6)'"
	cline4 = 'volume=3.608e+02, tramp=4.477e+00'
	cline5 = '$END'
	write(22,*)cline1
	write(22,*)cline3
	write(22,*)cline4
	write(22,*)cline5	
	rlb = 1.0
c	call apod
		do ii=1,isize
		write(22,31)dsav(ii),dsav(ii+isize)
		enddo
	close(22)



c	write(6,*)'imagef test ',imagef(20,2),ifil
c
c 1st ft dimension
c
c	   call sinebellfilter2(isize)
	   open(17,file='filter.txt')
	   do i=1,isize
	      write(17,*)gfilter(i)
	      enddo
	      close(17)
	do irow = 1,nrows
	   inc=1
	   do i=2,isize*2,2
	      dnmr(inc)= imagef(i,irow)
	      inc = inc+1
	      enddo
		inc = 1
	   do i=1,isize*2,2
	      dnmr(inc+isize)= imagef(i,irow)
	      inc = inc+1
	      enddo

	   call gaussfilter(isize)
c	   open(17,file='filter.txt')
c	   do i=1,isize
c	      write(17,*)gfilter(i)
c	      enddo
c	      close(17)
c	pause 'filter '

c	      do i=1,isize
c		 dnmr(i) = dnmr(i)*gfilter(i)
c		 dnmr(i+isize) = dnmr(i+isize)*gfilter(i)
c		 enddo

c	      do i=1,isize
c		 dnmr(i) = gfilter(i)
c		 dnmr(i+isize) = gfilter(i)
c		 enddo

c	   call sinebellfilter2(isize)
c	      do i=1,isize
c		 dnmr(i) = dnmr(i)*gfilter(i)
c		 dnmr(i+isize) = dnmr(i+isize)*gfilter(i)
c		 enddo

c	rlb = 0.65
	rlb = 2
	call apod
	call fourier3
c	call phasenaa(inaa)
	write(6,*)'inaa ',inaa,irow
c	if(irow.eq.2)angcor = 0
c	call phasec(angcor)
	do i=1,isize*2
	   imagef(i,irow) = dnmr(i)
	   enddo  !i

	   rmax = -1e11
	   do i=600,750
	      rmax = max(rmax,dnmr(i))
	      if(rmax.eq.dnmr(i))iimax = i
	      enddo
c	      write(6,*)iimax,rmax,irow

		 enddo   !irow


	open(22,file = '2douta.img',form='unformatted')
	do irow = 1,nrows
	   do i=1,isize/2
	      nmr(i)=imagef(i,irow)
	      enddo
	do i=1,(isize/2)*4
	call FPUTC(22,c2nmr(i),istate)
	enddo  !i
	enddo  !irow
	close(22)
	open(23,file = 'test1.txt')
	do irow = 1,48
	do i=1,900
	   write(23,*)imagef(i,irow)
	   enddo
	enddo
	   close(23)
c
c average for the two types of signals
c
	do i=1,isize/2
	dsav(i) = 0
	do irow=1,nrows,2
	dsav(i) = dsav(i)+imagef(i,irow)
	enddo
	enddo
c
	open(23,file = 'testavg1.txt')
	do i=300,900
	write(23,*)dsav(i)
	enddo
	do i=1,isize/2
	dsav(i) = 0
	do irow=2,nrows,2
	dsav(i) = dsav(i)+imagef(i,irow)
	enddo
	enddo
	do i=300,900
	write(23,*)dsav(i)
	enddo
	close(23)




	
	
c	write(6,*)'imagef test 2 ',imagef(20,2),ifil


c 2ndst ft dimension
c
	   isizeold = isize
	   isize48 = 48

	do i=1,isizeold
	   call gaussfilter2(isize48)

	   do irow =1,nrows
		 dnmr(irow) = imagef(i,irow)*gfilter(irow)
		 dnmr(irow+64) = imagef(i+isizeold,irow)*gfilter(irow)
		 enddo

	do irow = 49,64
	   dnmr(irow) = 0
	   dnmr(irow+64) = 0
	   enddo  !irow
	   isize = 64

	   do ii=1,64
c	     if(i.eq.500) write(6,*)'dnmr ',dnmr(ii),ii
	      enddo

	      isize = 64
	call fourier3
	call power
	do irow = 1,isize
	   imagef(i,irow) = dnmr(irow)
	   imagef(i+isizeold,irow) = dnmr(irow+64)
	   enddo  !irow
	   enddo   !i
c output
c
	open(22,file = '2doutb.img',form='unformatted')
	do irow = 1,64
	inc = 1
	   do i=1,1024
	      nmr(inc)=imagef(i,irow)
	inc = inc+1
	      enddo
	do i=1,1024*4
	call FPUTC(22,c2nmr(i),istate)
	enddo  !i
	enddo  !irow
	close(22)
	open(12,file = 'test32.txt')
	inc = 1
	do i=1+512,1024+512
	write(12,*)imagef(i,32)
	enddo
	close(12)
	open(12,file = 'test592.txt')
	inc = 1
	do irow = 1,64
	write(12,*)imagef(442+512,irow)
	enddo
	close(12)
	open(12,file = 'gabatestxa.txt')
	open(13,file = 'gabatestya.txt')
	do j=707,709
	do i=24,30
	write(12,*)i
	write(13,*)imagef(j,i)
	enddo
	enddo
	close(12)
	close(13)
	open(12,file = 'gabatestxb.txt')
	open(13,file = 'gabatestyb.txt')
	do j=26,28
	do i=706,712
	write(12,*)i
	write(13,*)imagef(i,j)
	enddo
	enddo
	close(12)

c	write(6,*)'imagef test 3 ',imagef(679,31),imagef(708,26),ifil

c
c calculate gaba to naa ratio
c
	rnaa = 0
	rsize = 0
	do irow = 30,31
	do i=650,900
	rnaa = rnaa+imagef(i,irow)
	rsize = rsize+1
	enddo
	enddo
	rnaa2 = rnaa/rsize
	write(6,*)'total demon = ',rnaa2
c
c gln set
c
	rgaba = 0
	do irow = 26,27
	do i=729,730
	rgaba = rgaba+imagef(i,irow)
	enddo
	enddo
	write(6,*)'gaba = ',rgaba/4.0
	rgaba2 = rgaba/4.0
	write(6,*)'gln/tot = ',rgaba2/rnaa2,ifil
	open(11,file = 'glnnaa.txt')
	write(11,*)cfn
	write(11,*)rgaba2,rnaa2,rgaba2/rnaa2
	close(11)


	write(6,*)'finished '
	stop
	end

c
	subroutine average(aver,stdev,stem)
	common /dat1/ dnmr(100000),dnmr2(1000),dnmr3(1000)
	common /size/isize,isize2
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
c  inverse fourier transform with ie = 1 and with spectral shifting
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
	N=ISIZE
	RN=N+1
	is2 = isize*2
	DO 11 I=1,ISIZE
	PK(I)=DNMR(isize-I+1)
 11	PKI(I)=DNMR(is2-i+1)
C	TYPE *,'PK,PKI',PK(I),PKI(I)
C
	nhalf = n/2
	do  13 i=1,n
	pnmr(i+nhalf)=PK(i)
 13     dsav(i+nhalf)=PKI(i)
 
 	do  12 i=1,N/2
	PK(i)=pnmr(i+n)
 12     PKI(i)=dsav(i+n)
 
 	do i=1,nhalf
 	pk(i+nhalf) = pnmr(i+nhalf)
 	pki(i+nhalf) = dsav(i+nhalf)
 	enddo


c testing output of shifting
c
c	open(11,file='nmrshift.txt')
c	do i=1,isize
c	write(11,*)pk(i)
c	enddo
c	do i=1,isize
c	write(11,*)pki(i)
c	enddo
c
c	close(11)


	ie=1
C	TYPE *,'ISIZE INFFT',ISIZE

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


c       sub for automatic phasing zeroth order
c
        subroutine phasenaa(inaa)
C
c water phasing based on ileft and iright
c
        include 'nmrpar.f'
        common /phase/angsum,angbsum
        common /subsav/subsav(8192)
	common /passder/idermax
	common /savest/angmax,angm
	common /rnaasav/rnaaheight
	common /waterpass/iwaterscan
	common /phasepass/iphasepeak,iechopass,angoffset1,angoffset2
	common /phoutpass/iphout(32,32)
	dimension deriv(8192)
        radcon=3.14159265/180.
c
        do 10 i=1,isize*2
        subsav(i)=dnmr(i)
 10     continue
	
c
c
        ang1 = 45.
        angx = ang1 * radcon
        temp = 0.
c
c find naa
c
	ibaseleft = 1
	ibaseright = 3
c
c first find the maximum and set to 2ppm
c  whether or not it is naa or lipids
c
	ishalf = isize/2
	ileft = 600
	iright = 770
		rmax = -1e11
		rmin = 1e11
		jtest = 15
		ktest = 8
		do i=1,isize
		if(i.gt.ileft.and.i.lt.iright)then
			r1 = dnmr(i)**2 + dnmr(i+isize)**2
			if(jpass.eq.jtest.and.kpass.eq.ktest)write(23,*)pnmr(i),r1
			rmax = max(rmax,r1)
			rmin = min(rmin,r1)
			if(rmax.eq.r1)inaa = i
		endif
		enddo

	inc = 7
	rmax = -1e6
	ang1 = 0.
	
	smin = 1e6
	diffmax = -1e6
	n  = id
c	open(33,file = 'sss')
	incc =1
	smax = -1e6
	do 30 i=1,inc
	ang1 = ang1 + 60
	angx = ang1 * radcon
	sum = 0
	rcount=0

	do id=inaa-10,inaa+10

		if(id.gt.ileft.and.id.lt.iright)then
		dnmr(id) = (subsav(id) * cos(angx)) - (subsav(id+isize) * sin(angx)
     &)
c		write(33,*)incc,char(9),dnmr(n)
		incc = incc+1
c		write(6,*)'dnmr n angx ',dnmr(id),id,angx
		smax = max(smax,dnmr(id))
		if(smax.eq.dnmr(id))then
		angm = angx
		endif
		sum = sum+dnmr(id)
		rcount = rcount+1
		endif
	enddo
	

 30	continue
c 	close(33)
 

c/*  apply the best phase angle for the final phase correction
c */
	angm1 = angm			!to save intermediate angle
	do i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize) * sin(angm)
     &)
 	dnmr(i + isize) = (subsav(i+isize) * cos(angm)) + (subsav(i) * sin(angm)
     &)
	enddo
	
	do i=1,isize*2
	subsav(i) = dnmr(i)
	enddo
	

c
c what is the height of the naa peak subtracted form baseline
c
	inc = 360
	rmin = 1e16
	ang1 = -90
	do 130 j=1,inc
c	do 130 j=1,2
	ang1 = ang1 + 0.5
	angx = ang1 * radcon
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'ang1,angx,j ',ang1,angx,j,inaa
	endif
	
	do 140 i=inaa-20,inaa+20
	dnmr(i)=(subsav(i)*cos(angx))-(subsav(i+isize)*sin(angx))
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'subsav(i) cos(angx) ',subsav(i),cos(angx),i,dnmr(i)
 	endif
	
 140	continue
 	if(jpass.eq.1.and.kpass.eq.16)then
c 	write(6,*)'dnmr(inaa+6+1) ',dnmr(inaa+6+1),inaa,j,cos(angx)
 	endif
c	
c
c  find average baseline on both sides
c
	sum1 = 0
c	do i=inaa+ibaseleft,inaa+ibaseright
	do i=inaa,inaa

	sum1 = sum1+dnmr(i+4)
	enddo
	averbase1 = sum1/1.0
c
c
c  find average baseline on both sides
c
	sum2 = 0
c	do i=inaa+ibaseleft,inaa+ibaseright
	do i=inaa,inaa
	sum2 = sum2+dnmr(i-4)
	enddo
	averbase2 = sum2/1.0
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'averbase1, averbase2 ',averbase1, averbase2,angm
	endif
	diff = abs(averbase2-averbase1)
	rmin = min(rmin,diff)
	if(rmin.eq.diff)angm = angx
 130	continue
	
c/*  apply the best phase angle for the final phase correction
c */

	do 240 i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize)*sin(angm)
     &)
 240	dnmr(i + isize) = (subsav(i+isize)*cos(angm)) + (subsav(i)*sin(angm)
     &)
 
   
c

	sum1 = 0
	do i=1+inaa,5+inaa
	sum1 = sum1+dnmr(i+5)
	enddo
	averbase1 = sum1/5.0
	rnaaheight = dnmr(inaa) - averbase1
c	write(6,*)'rnaaheight ', rnaaheight
c
c now check to see if this rmax peak is really naa 
c
c
		rmax = -1e11
		rmin = 1e11

		do i=1,isize
		if(i.gt.ileft.and.i.lt.iright)then
			r1 = dnmr(i)
			rmax = max(rmax,r1)
			rmin = min(rmin,r1)
			if(rmax.eq.r1)inaa = i
		endif
		enddo


	return
	end
c       sub for automatic phasing zeroth order
c
        subroutine phasenaa2(inaa,jpass)
C
        include 'nmrpar.f'
        common /phase/angsum,angbsum
        common /subsav/subsav(8192)
	common /passder/idermax
	common /savest/angmax,angm
	common /rnaasav/rnaaheight
	common /waterpass/iwaterscan
	common /phasepass/iphasepeak,iechopass,angoffset1,angoffset2
	common /phoutpass/iphout(32,32)
	dimension deriv(8192)
        radcon=3.14159265/180.
c
        do 10 i=1,isize*2
        subsav(i)=dnmr(i)
 10     continue
	
c
c
        ang1 = 45.
        angx = ang1 * radcon
        temp = 0.
c
c find naa
c
	ibaseleft = 1
	ibaseright = 3
c
c first find the maximum and set to 2ppm
c  whether or not it is naa or lipids
c
	ishalf = isize/2
c	ileft = 800
	ileft = 2049-(1050+400)
	iright = 2049-(1050+280)
c	ileft = ishalf-100
c	iright = 1200
c	iright = ishalf+100
		rmax = -1e11
		rmin = 1e11
		jtest = 15
		ktest = 8
		if(jpass.eq.jtest.and.kpass.eq.ktest)open(23,file='testph1')
		    
	write(6,*)'isize phasenaa',isize
		do i=1,isize
		if(i.gt.ileft.and.i.lt.iright)then
			r1 = dnmr(i)**2 + dnmr(i+isize)**2
c			write(6,*)'r1 inphasenaa ',r1,i,pnmr(i)
			if(jpass.eq.jtest.and.kpass.eq.ktest)write(23,*)pnmr(i),r1
			rmax = max(rmax,r1)
			rmin = min(rmin,r1)
			if(rmax.eq.r1)inaa = i
		endif
		enddo
		if(jpass.eq.jtest.and.kpass.eq.ktest)close(23)
	
c

	write(6,*)'inaa 1st ',inaa

	inc = 7
	rmax = -1e6
	ang1 = 0.
	
	smin = 1e6
	diffmax = -1e6
	n  = id
c	open(33,file = 'sss')
	incc =1
	smax = -1e6
	do 30 i=1,inc
	ang1 = ang1 + 60
	angx = ang1 * radcon
	sum = 0
	rcount=0

	do id=ileft,iright

		if(id.gt.ileft.and.id.lt.iright)then
		dnmr(id) = (subsav(id) * cos(angx)) - (subsav(id+isize) * sin(angx)
     &)
c		write(33,*)incc,char(9),dnmr(n)
		incc = incc+1
c		write(6,*)'dnmr n angx ',dnmr(id),id,angx
		smax = max(smax,dnmr(id))
		if(smax.eq.dnmr(id))then
		angm = angx
		endif
		sum = sum+dnmr(id)
		rcount = rcount+1
		endif
	enddo
	
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'dnmr 1st ang ',dnmr(inaa),angm,smax,inaa
	endif

 30	continue
c 	close(33)
 

c/*  apply the best phase angle for the final phase correction
c */
	angm1 = angm			!to save intermediate angle
	do i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize) * sin(angm)
     &)
 	dnmr(i + isize) = (subsav(i+isize) * cos(angm)) + (subsav(i) * sin(angm)
     &)
	enddo
	
	do i=1,isize*2
	subsav(i) = dnmr(i)
	enddo
	
c
c what is the height of the naa peak subtracted form baseline
c
	inc = 180
	rmin = 1e16
	ang1 = -90
	do 130 j=1,inc
c	do 130 j=1,2
	ang1 = ang1 + 1
	angx = ang1 * radcon
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'ang1,angx,j ',ang1,angx,j,inaa
	endif
	
	do 140 i=inaa-20,inaa+20
	dnmr(i)=(subsav(i)*cos(angx))-(subsav(i+isize)*sin(angx))
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'subsav(i) cos(angx) ',subsav(i),cos(angx),i,dnmr(i)
 	endif
	
 140	continue
 	if(jpass.eq.1.and.kpass.eq.16)then
c 	write(6,*)'dnmr(inaa+6+1) ',dnmr(inaa+6+1),inaa,j,cos(angx)
 	endif
c	
c
c  find average baseline on both sides
c
	sum1 = 0
	do i=inaa+ibaseleft,inaa+ibaseright
	sum1 = sum1+dnmr(i+4)  !invivo
	enddo
	averbase1 = sum1/3.0
c
c
c  find average baseline on both sides
c
	sum2 = 0
	do i=inaa+ibaseleft,inaa+ibaseright
	sum2 = sum2+dnmr(i-5)
	enddo
	averbase2 = sum2/3.0
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'averbase1, averbase2 ',averbase1, averbase2,angm
	endif
	diff = abs(averbase2-averbase1)
	rmin = min(rmin,diff)
	if(rmin.eq.diff)angm = angx
 130	continue
	
c/*  apply the best phase angle for the final phase correction
c */

	do 240 i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize)*sin(angm)
     &)
 240	dnmr(i + isize) = (subsav(i+isize)*cos(angm)) + (subsav(i)*sin(angm)
     &)
 
   
c
	if(jpass.eq.199999.and.kpass.eq.16)then
	open(11,file = 'test0116c.txt' )
	do i=600,750
	write(11,*)i,dnmr(i)
	enddo
	close(11)
	endif

	sum1 = 0
	do i=1+inaa,5+inaa
	sum1 = sum1+dnmr(i+5)
	enddo
	averbase1 = sum1/5.0
	rnaaheight = dnmr(inaa) - averbase1
c	write(6,*)'rnaaheight ', rnaaheight
c
c now check to see if this rmax peak is really naa 
c
c
		rmax = -1e11
		rmin = 1e11

		do i=1,isize
		if(i.gt.ileft.and.i.lt.iright)then
			r1 = dnmr(i)
c			write(6,*)'r1 inphasenaa ',r1,i,pnmr(i)
			rmax = max(rmax,r1)
			rmin = min(rmin,r1)
			if(rmax.eq.r1)inaa = i
		endif
		enddo


	return
	end
c       sub for automatic phasing zeroth order
c
        subroutine phasenaa3(inaa,jpass)
C
        include 'nmrpar.f'
        common /phase/angsum,angbsum
        common /subsav/subsav(8192)
	common /passder/idermax
	common /savest/angmax,angm
	common /rnaasav/rnaaheight
	common /waterpass/iwaterscan
	common /phasepass/iphasepeak,iechopass,angoffset1,angoffset2
	common /phoutpass/iphout(32,32)
	dimension deriv(8192)
        radcon=3.14159265/180.
c
        do 10 i=1,isize*2
        subsav(i)=dnmr(i)
 10     continue
	
c
c
        ang1 = 45.
        angx = ang1 * radcon
        temp = 0.
c
c find naa
c
	ibaseleft = 1
	ibaseright = 3
c
c first find the maximum and set to 2ppm
c  whether or not it is naa or lipids
c
	ishalf = isize/2
c	ileft = 800
	ileft = 674-30
	iright = 674+30
		rmax = -1e11
		rmin = 1e11
		jtest = 15
		ktest = 8
		if(jpass.eq.jtest.and.kpass.eq.ktest)open(23,file='testph1')
		    
c	write(6,*)'isize phasenaa',isize
		do i=1,isize
		if(i.gt.ileft.and.i.lt.iright)then
			r1 = dnmr(i)**2 + dnmr(i+isize)**2
c			write(6,*)'r1 inphasenaa ',r1,i,pnmr(i)
			if(jpass.eq.jtest.and.kpass.eq.ktest)write(23,*)pnmr(i),r1
			rmax = max(rmax,r1)
			rmin = min(rmin,r1)
			if(rmax.eq.r1)inaa = i
		endif
		enddo
		if(jpass.eq.jtest.and.kpass.eq.ktest)close(23)
	
c

c	write(6,*)'inaa 1st ',inaa

	inc = 7
	rmax = -1e6
	ang1 = 0.
	
	smin = 1e6
	diffmax = -1e6
	n  = id
c	open(33,file = 'sss')
	incc =1
	smax = -1e6
	do 30 i=1,inc
	ang1 = ang1 + 60
	angx = ang1 * radcon
	sum = 0
	rcount=0

	do id=ileft,iright

		if(id.gt.ileft.and.id.lt.iright)then
		dnmr(id) = (subsav(id) * cos(angx)) - (subsav(id+isize) * sin(angx)
     &)
c		write(33,*)incc,char(9),dnmr(n)
		incc = incc+1
c		write(6,*)'dnmr n angx ',dnmr(id),id,angx
		smax = max(smax,dnmr(id))
		if(smax.eq.dnmr(id))then
		angm = angx
		endif
		sum = sum+dnmr(id)
		rcount = rcount+1
		endif
	enddo
	
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'dnmr 1st ang ',dnmr(inaa),angm,smax,inaa
	endif

 30	continue
c 	close(33)
 

c/*  apply the best phase angle for the final phase correction
c */
	angm1 = angm			!to save intermediate angle
	do i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize) * sin(angm)
     &)
 	dnmr(i + isize) = (subsav(i+isize) * cos(angm)) + (subsav(i) * sin(angm)
     &)
	enddo
	
	do i=1,isize*2
	subsav(i) = dnmr(i)
	enddo
	
c
c what is the height of the naa peak subtracted form baseline
c
	inc = 180
	rmin = 1e16
	ang1 = -90
	do 130 j=1,inc
c	do 130 j=1,2
	ang1 = ang1 + 1
	angx = ang1 * radcon
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'ang1,angx,j ',ang1,angx,j,inaa
	endif
	
	do 140 i=inaa-20,inaa+20
	dnmr(i)=(subsav(i)*cos(angx))-(subsav(i+isize)*sin(angx))
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'subsav(i) cos(angx) ',subsav(i),cos(angx),i,dnmr(i)
 	endif
	
 140	continue
 	if(jpass.eq.1.and.kpass.eq.16)then
c 	write(6,*)'dnmr(inaa+6+1) ',dnmr(inaa+6+1),inaa,j,cos(angx)
 	endif
c	
c
c  find average baseline on both sides
c
	sum1 = 0
	do i=inaa+ibaseleft,inaa+ibaseright
	sum1 = sum1+dnmr(i+4)    
	enddo
	averbase1 = sum1/3.0
c
c
c  find average baseline on both sides
c
	sum2 = 0
	do i=inaa+ibaseleft,inaa+ibaseright
	sum2 = sum2+dnmr(i-5)
	enddo
	averbase2 = sum2/3.0
	if(jpass.eq.1.and.kpass.eq.16)then
c	write(6,*)'averbase1, averbase2 ',averbase1, averbase2,angm
	endif
	diff = abs(averbase2-averbase1)
	rmin = min(rmin,diff)
	if(rmin.eq.diff)angm = angx
 130	continue
	
c/*  apply the best phase angle for the final phase correction
c */

	do 240 i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize)*sin(angm)
     &)
 240	dnmr(i + isize) = (subsav(i+isize)*cos(angm)) + (subsav(i)*sin(angm)
     &)
 
   
c
	if(jpass.eq.199999.and.kpass.eq.16)then
	open(11,file = 'test0116c.txt' )
	do i=600,750
	write(11,*)i,dnmr(i)
	enddo
	close(11)
	endif

	sum1 = 0
	do i=1+inaa,5+inaa
	sum1 = sum1+dnmr(i+5)
	enddo
	averbase1 = sum1/5.0
	rnaaheight = dnmr(inaa) - averbase1
c	write(6,*)'rnaaheight ', rnaaheight
c
c now check to see if this rmax peak is really naa 
c
c
		rmax = -1e11
		rmin = 1e11

		do i=1,isize
		if(i.gt.ileft.and.i.lt.iright)then
			r1 = dnmr(i)
c			write(6,*)'r1 inphasenaa ',r1,i,pnmr(i)
			rmax = max(rmax,r1)
			rmin = min(rmin,r1)
			if(rmax.eq.r1)inaa = i
		endif
		enddo


	return
	end
	
	SUBROUTINE FOURIER3
C       ROUTINE USED IN 2DFT ... THIS ROUTINE DOES NOT ZERO EXTENT
C
C
	include 'nmrpar.f'
	common /pkc/pk(100000),pki(100000)
C       TYPE *,'DNMR',(DNMR(I),I=1,30)
C
C       ZERO FILL
C
	rdiv=1
c       DO 10 I=1,isize
c       PK(I)=0.
c 10    PKI(I)=0.
C
C       LOAD FID
C
	DO 11 I=1,isize
	PK(I)=DNMR(I)
 11     PKI(I)=DNMR(I+(isize))
C       TYPE *,'PK,PKI',PK(I),PKI(I)
		if(j.eq.16.and.k.eq.16)write(6,*)'pk 1',(pk(ii),ii=1,10)
C
	ie=-1
c       	write(6,*)'isize INFFT',isize
	N=isize
	RN=N+1
	nu=alog(rn)/alog(2.)
C       TYPE *,'N',N,NU,IE
	call FFT(n,NU,IE)
c	write(6,*)'pk 2 ',(pk(ii),ii=1,10)
C
c       prepare fft output
c
	ifshift=1
	if(ifshift.eq.1)then
	do  12 i=1,N/2
	PK(i+n)=PK(i)
 12     PKI(i+n)=PKI(i)
C
	do  13 i=1,n
	PK(i)=PK(n/2+i)
 13     PKI(i)=PKI(n/2+i)

	DO  14 I=1,N
	DNMR(I)=PK(N-I+1)/rdiv
 14     DNMR(I+ISIZE)=PKI(N-I+1)/rdiv
	else
	DO  16 I=1,N
	DNMR(I)=PK(i)/rdiv
 16     DNMR(I+ISIZE)=PKI(i)/rdiv
	endif
c
	RETURN
	END
C
C       SUB FOR APODIZATION OF FID
C
	SUBROUTINE APOD
C
	include 'nmrpar.f'
C
c
c       to convert from hertz to pixels
c
	pi = 3.1428
	factor= pi * rlb / (rinfo(2))
c       write(6,*)factor
C
	IDIM=ISIZE
	DO 10 I=1,IDIM
	RIN=(I-1)*factor
	DNMR(I)=DNMR(I) * EXP(-RIN)	     
c       write(6,*)i,exp(rin)
c   !REAL PART
	DNMR(I+IDIM)=DNMR(I+IDIM) * EXP(-RIN)
c       !IMAG PART
 10     continue
C
C
	RETURN
	END
C       SUB FOR APODIZATION OF FID
C
	SUBROUTINE undoapod
C
	include 'nmrpar.f'
C
c
c       to convert from hertz to pixels
c
	pi = 3.1428
	factor= pi * rlb / (rinfo(2))
c       write(6,*)factor
C
	IDIM=ISIZE
	DO 10 I=1,IDIM
	RIN=(I-1)*factor
	DNMR(I)=DNMR(I) * EXP(RIN)	     
c       write(6,*)i,exp(rin)
c   !REAL PART
	DNMR(I+IDIM)=DNMR(I+IDIM) * EXP(RIN)
c       !IMAG PART
 10     continue
C
C
	RETURN
	END
c

c fit t1 or t2 to data areas file

c

c	functions subroutine
	subroutine function2

	common /ch/chi,p,n

	common /xx/x,ysum

	common /funct/ifunc

	common /gauss/gg

	common /tepass/te
	common /nrespass/nres

	common /trpass/tr

	dimension p(60)

	include 'nmrpar.f'

c

	if(ifunc.eq.1)then

	ysum = p(1) + (p(2) *x) + (p(3)*(x**2))

c	ysum = p(1) + (p(2)*x)

	endif

c	lorentzian function

c

	if(ifunc.eq.2)then

	ysum=0.

	gg = p(nres*3+1)

c	write(6,*)'nres',nres,x,base

c	write(6,*)'p',p

	do 10 i=1,nres

	inc=(i-1)*3

	inc=inc+1

	conta=(x-p(inc+2))/p(inc+1)

	conta=conta**2

	contb=(1 + 4*conta)

	y1=(1-gg) * p(inc)/contb

	contc=-4. * alog(2.)*conta

	y2= gg * p(inc) * exp(contc)

c	write(6,*)conta,contb,contc,y1,y2

	ysum=ysum+y1+y2

 10	continue

c  	ysum=ysum + p(n-1) + (p(n)*x)

c	write(6,*)'ysum',x,ysum

	endif

c

	if(ifunc.eq.3)then

	ysum = p(1)

	endif

	if(ifunc.eq.4)then

	ysum = p(1) + (p(2) *x)

	endif

c
c   t2 single exponential
c

	if(ifunc.eq.5)then

	ysum = p(1)*exp(-x/p(2))

	endif

	

	if(ifunc.eq.6)then

	r1 = exp(-x/p(2))

	r2 = (1-exp(-tr/p(2)))

	r3 = (1 - ((1 + (p(3)*r2)) *r1))

	ysum = p(1)*r3

	endif
c
c equation from Hurd Magn Reson Med 51:435-440,2004

	if(ifunc.eq.7)then

	r1 = exp(-x/p(2))

	r2 = 2*exp(-((x-(te/2))/p(2)))

	r3 = 1-r2+r1

	ysum = p(1)*r3

	endif
c
c equation from Harada et al, Neuroradiology 43: 448-452

	if(ifunc.eq.8)then
	t2b=80
	t2c= 800

	r1 = exp(-(2*x)/t2b)
	r2 = p(1)*r1
	r3 = exp(-(2*x)/t2c)
	r4 = p(2)*r3
	ysum = r2+r4

	endif

c

	return

	end

	subroutine showbox
	character*80 cfn(100),cpar,cout
	real apoff(100),rloff(100),ccoff(100),apsize(100),lrsize(100)
	real apang(100),rlang(100),ccang(100)
	real ccsize(100),rheader(87)
	integer*2 imagef(256,256,256),inmr(256),i2header(174)
	integer*2 imagerot(256,256,256)
	character*1 cnmr(512),con(1800),con200(1800)
	integer*1 icon(1800),icon200(1800)
	equivalence (con,icon)
	equivalence (cnmr,inmr)
	equivalence (con200,icon200)
	integer*1 header(348)
	character*1 cheader(348)
	equivalence (cheader,header)
	equivalence (header, i2header)
	equivalence (header,rheader)
	real height,depth

	open(14,file='c:/showbox2.hdr',form='unformatted')
c	open(14,file='F07312_AXMPRAGE_4_1.hdr',form='unformatted')
	do i=1,348
	call FGETC(14,cheader(i),istate)
	enddo
	close(14)
	do i=1,50
c	write(6,*)i2header(i),i
	enddo
	do i=1,87
c	write(6,*)rheader(i),i
	enddo

	
c
c load in location parameters for the 3D MPRAGE file
c
	open(12,file = './filespar.txt',form='unformatted')
	do i=1,1800
	call FGETC(12,con(i),istate)
	if(icon(i).eq.13)icon(i)=32
	enddo
	close(12)
	open(12,file='./filespar2.txt',form='unformatted')
		do i=1,1800
	call FPUTC(12,con(i),istate)
	enddo
	close(12)
	open(12,file='./filespar2.txt')

	read(12,*)cpar,ypar,zpar,xpar,ixsize,iysize,r1,r2,slthick,r3,
	1	pixsizex,pixsizey,izsize,angy1,angz1,angx1
	write(6,*)'par ',ypar,zpar,xpar,ixsize,iysize,r1,r2,slthick,r3,
	1	pixsizex,pixsizey,izsize,angy1,angz1,angx1

	slthick = slthick +r3
	close(12)
	i2header(22) = ixsize
	i2header(23) = iysize
	i2header(24) = izsize
	rheader(21) = pixsizex
	rheader(22) = pixsizey
	rheader(23) = slthick
	write(6,*)'slthick ',slthick

c 
c load in location parameters for spectral box
c
	open(12,file = './filesloc.txt',form='unformatted')
	do i=1,1800
	call FGETC(12,con200(i),istate)
	if(icon200(i).eq.13)icon200(i)=32
	enddo
	close(12)
	open(12,file='./filesloc2.txt',form='unformatted')
		do i=1,1800
	call FPUTC(12,con200(i),istate)
	enddo
	close(12)
	open(11,file='./filesloc2.txt')

	inc = 1
 98	read(11,*,end=99)cfn(inc),apoff(inc),rloff(inc),ccoff(inc),
 	1	lrsize(inc),apsize(inc),ccsize(inc),apang(inc),rlang(inc),ccang(inc)
 	write(6,*)'loc ',apoff(inc),rloff(inc),ccoff(inc),
 	1	lrsize(inc),apsize(inc),ccsize(inc),apang(inc),rlang(inc),ccang(inc)
 
 	inc = inc+1
	go to 98
  99	close(11)
	
	nfils = inc-1
	do ifil = 1,nfils
		angy = angy1 - apang(ifil)
		angx = angx1 - rlang(ifil)
		angz = angz1 - ccang(ifil)

	write(6,*)'angx y z ',angx,angy,angz,apang(ifil),rlang(ifil),ccang(ifil)
c
c calculate box position
c
c
c  these dimension parameters have to be rearranged because the original MPRAGE was
c in sagittal orientation and the output from PARtoNIFTY is axial LAS file
c
	xoffset = xpar
	yoffset = ypar
	zoffset = zpar
	pixfinalz = slthick
	pixfinalx = pixsizex
	pixfinaly = pixsizey
	xsize = ixsize
	ysize = iysize
	zsize = izsize
	apoff1= apoff(ifil)
	rloff1= rloff(ifil)
	ccoff1= ccoff(ifil)
	width = lrsize(ifil)
	height = apsize(ifil)
	depth = ccsize(ifil)

	rlpixel = ((xsize/2)-((rloff1+xoffset)/pixfinalx))
	write(6,*)'rl ',rlpixel,rloff1,xoffset,pixfinalx,xsize

	appixel = (((ysize/2) - ((apoff1+yoffset)/pixfinaly)))
c	write(6,*)'apoff1 yoffset pixfinaly ',apoff1,yoffset,pixfinaly,appixel
c	ccpixel = ((zsize/2)-(-(ccoff1-zoffset)/pixfinalz))
	ccpixel = ((zsize/2)-(-(ccoff1-zoffset)/pixfinalz))
c	write(6,*)'rlpixel,appixel,ccpixel',rlpixel,appixel,ccpixel
c
c  rlpixel is the center of the voxel in the right-left direction
c appixel is the center of the voxel in the ap direction
c ccpixel is the center of the voxel in the superior-inferior direction

	rl_start = rlpixel-(width/(pixfinalx*2))
c	write(6,*)'rl ',rl_start,rlpixel,width
	rl_end = rlpixel + (width/(pixfinalx*2))
	ap_start = appixel - (height/(pixfinaly*2))
	ap_end = appixel + (height/(pixfinaly*2))
	cc_start = ccpixel - (depth/(pixfinalz*2))
	cc_end = ccpixel + (depth/(pixfinalz*2))
c	write(6,*)'depth ', width, pixfinalx,height,pixfinaly,depth, pixfinalz
	write(6,*)'start ',rl_start,ap_start,cc_start
c	write(6,*)'end ',rl_end,ap_end,cc_end
c 
c now calculate the 3D MPRAGE image center offsets
c
c
	offirl = xoffset/pixfinalx
	offiap = yoffset/pixfinaly
	officc = zoffset/pixfinalz
	ixsize2 = xsize
	iysize2 = ysize
	izsize2 = zsize
	do k=1,izsize2
	do j=1,iysize2
	do i=1,ixsize2
	imagef(i,j,k) = 0
	enddo
	enddo
	enddo
	
	ikstart = cc_start
	ikend = cc_end
	ijstart = (ap_start)
	ijend =(ap_end)
c	write(6,*)'apstart offiap ',ap_start,offiap,ijstart,ijend,appixel
 
	istart = rl_start
c		write(6,*)'rlpixel ',istart,rlpixel,rl_start,offirl
	iend = rl_end
c
	write(6,*)'ikstart ijstart istart ',ikstart,ijstart,istart
	do k=ikstart,ikend
	do j=ijstart,ijend
	do i=istart,iend
	imagef(i,j,k) = 100
	imagerot(i,j,k)= 100
	enddo
	enddo
	enddo
	r1 = ikstart
	r2 = ikend
	rmidk = ((r2-r1)/2.0)+r1
	midk = rmidk
	r1 = ijstart
	r2 = ijend
	rmidj = ((r2-r1)/2.0)+r1
	midj = rmidj
	r1 = istart
	r2 = iend
	rmidi = ((r2-r1)/2.0)+r1
	midi = rmidi
c
c
c imagef now has the spectra box without rotation
c  now we will rotate the box in three dimensions
	angle1 = angz
	radcon = 3.141593/180.0
	angle = radcon*angle1

	do k=1,izsize2
	   do j=1,iysize2
	   do i=1,ixsize2
	      imagerot(i,j,k)=0
	      enddo
	      enddo
	      enddo
	do k=1,izsize2
	   do j=1,iysize2
	   do i=1,ixsize2
	      ri1 = i-midi
	      rj1 = j-midj
	      r2 = (cos(angle)*ri1) + (sin(angle)*rj1)
	      r3 = (-sin(angle)*ri1) + (cos(angle)*rj1)
c	      if(k.eq.50.and.j.eq.128)then
c		 write(6,*)'r2 r3 ri1 rj1 ',r2,r3,ri1,rj1,i
c		 endif
	      rr2 = r2+midi
	      inew = r2+midi
	      diff = rr2-inew
	      if(diff.gt.0.5)inew=inew+1
	      rr3 = r3+midj
	      jnew = r3+midj
	      diff = rr3-jnew
	      if(diff.gt.0.5)jnew=jnew+1
	      if(inew.ge.1.and.inew.le.ixsize2)then
		if(jnew.ge.1.and.jnew.le.iysize2)then
	      imagerot(i,j,k)=imagef(inew,jnew,k)
	      endif
	      endif
	      enddo
	      enddo
	      enddo
c
	do k=1,izsize2
	   do j=1,iysize2
	   do i=1,ixsize2
	      imagef(i,j,k)=0
	      enddo
	      enddo
	      enddo

	angle1 = angx
	radcon = 3.141593/180.0
	angle = radcon*angle1
	ratio = pixfinalz/pixfinaly
	do k=1,izsize2
	   do j=1,iysize2
	   do i=1,ixsize2
	      r2 = (cos(angle)*(j-midj)*pixfinaly)+(sin(angle)*(k-midk)*pixfinalz)
	      r3 = (-sin(angle)*(j-midj)*pixfinaly) + (cos(angle)*(k-midk)*pixfinalz)
	      jnew = (r2/pixfinaly)+midj
	      rr2 = (r2/pixfinaly)+midj
	      knew = (r3/pixfinalz)+midk
	      rr3 = (r3/pixfinalz)+midk
	      diff = rr3-knew
	      if(diff.gt.0.5)knew=knew+1
	      diff = rr2-jnew
	      if(diff.gt.0.5)jnew=jnew+1
	      if(jnew.lt.1)jnew = 1
	      if(knew.lt.1)knew = 1
	      if(jnew.gt.iysize2)jnew = iysize2
	      if(knew.gt.izsize2)knew = izsize2
	      imagef(i,j,k)=imagerot(i,jnew,knew)
	      enddo
	      enddo
	      enddo
c
	do k=1,izsize2
	   do j=1,iysize2
	   do i=1,ixsize2
	      imagerot(i,j,k)=0
	      enddo
	      enddo
	      enddo

	angle1 =angy
c
c	write(6,*)'pixfinalx, pixfinalz ',pixfinalx, pixfinalz
	radcon = 3.141593/180.0
	angle = radcon*angle1
	do k=1,izsize2
c	   write(6,*)'k ',k
	   do j=1,iysize2
	   do i=1,ixsize2
	      r2 = (cos(angle)*(i-midi)*pixfinalx) + (sin(angle)*(k-midk)*pixfinalz)
	      r3 = (-sin(angle)*(i-midi)*pixfinalx) + (cos(angle)*(k-midk)*pixfinalz)
	      inew = (r2/pixfinalx) + midi
	      rr2 = (r2/pixfinalx) + midi
	      knew = (r3/pixfinalz) + midk
	      rr3 = (r3/pixfinalz) + midk
	      diff = rr2-inew
	      if(diff.gt.0.5)inew=inew+1
	      diff = rr3-knew
	      if(diff.gt.0.5)knew=knew+1

	      if(inew.ge.1.and.inew.le.ixsize2)then
		if(knew.ge.1.and.knew.le.izsize2)then
	      imagerot(i,j,k)=imagef(inew,j,knew)
	      endif
	      endif
	      enddo
	      enddo
	      enddo


	cout = cfn(ifil)
	do i=1,80
	if(cout(i:i).eq.'.')iper = i
	enddo
	cout(iper:iper+4) = 'x.img'
	write(6,*)cout
	open(14,file=cout,form='unformatted')

	do k=1,izsize2
	do j=1,iysize2
	do i=1,ixsize2
	inmr(i) = imagerot(i,j,k)
	enddo
	do i=1,ixsize2*2
	call FPUTC(14,cnmr(i),istate)
	enddo  !i
	enddo  !j
	enddo  !k

	close(14)
	cout(iper:iper+4) = 'x.hdr'
	open(14,file=cout,form='unformatted')
	do i=1,348
	call FPUTC(14,cheader(i),istate)
	enddo
	close(14)
	
	
	enddo	!ifil

	write(6,*)'finished showbox'

	return
	end


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
C
	subroutine sinebellfilter(isize)
	common /gf/ gfilter(2048)
	risize = (isize*3/2)-1
	pi = 3.1415926535
	rinc = pi/risize
	r1 = risize/3
	inc = 1
	do i=1,isize
	x = (i+r1)-1
	ang = x*rinc
	gfilter(inc) = sin(ang)
	write(6,*)'gfilter ',gfilter(inc),inc,x,rinc
	inc = inc+1
	enddo
 10     continue
c
	return
	END
c
	subroutine sinebellfilter2(isize)
	common /gf/ gfilter(2048)
	risize = (isize*2/2)-1
	pi = 3.1415926535
	rinc = pi/risize
c	r1 = risize/2
	r1 = 0
	inc = 1
	do i=1,isize
	x = (i+r1)-1
	ang = x*rinc
	gfilter(inc) = sin(ang)
c	write(6,*)'gfilter ',gfilter(inc),inc,x,rinc
	inc = inc+1
	enddo
 10     continue
c
	return
	END


c
	subroutine gaussfilter(isize)
	common /gf/ gfilter(2048)
	common /filterpass/ifilter,iechomode
c       gaussian function
c
c       write(6,*)'enter resonance number and line width in points '
c       read(5,*)xref,xlin
	rfilterdiv = 3.0   !width
	xref = isize/5.0   !pos
	xlin = (isize/rfilterdiv)
c		write(6,*)'xlin ',xlin
	do i=1,isize
	x=i
	conta=(x-xref)/xlin
	conta=conta**2
	contb=(1 + 4*conta)
	contc=-4. * alog(2.)*conta
	gfilter(i)= exp(contc)
c	write(6,*)'gfilter ',gfilter(i),i
	enddo
 10     continue
c
	return
	END
c
	subroutine gaussfilter2(isize)
	common /gf/ gfilter(2048)
	common /filterpass/ifilter,iechomode
c       gaussian function
c
c       write(6,*)'enter resonance number and line width in points '
c       read(5,*)xref,xlin
	rfilterdiv = 3    !width
	xref = isize/5    !position
	xlin = (isize/rfilterdiv)

	do i=1,isize
	x=i
	conta=(x-xref)/xlin
	conta=conta**2
	contb=(1 + 4*conta)
	contc=-4. * alog(2.)*conta
	gfilter(i)= exp(contc)
c	write(6,*)'gfilter ',gfilter(i),i
	enddo
 10     continue
c
	return
	END
c
	subroutine phasec(angcor)
	real subsav(8192)
c
c this subroutine was written to cause balance of the force
c
	include 'nmrpar.f'
	do i=1,isize*2
	subsav(i) = dnmr(i)
	enddo

	angm = angcor			
	do i=1,isize
	dnmr(i) = (subsav(i) * cos(angm)) - (subsav(i+isize) * sin(angm)
     &)
 	dnmr(i + isize) = (subsav(i+isize) * cos(angm)) + (subsav(i) * sin(angm)
     &)
	enddo
	
	return
	end
