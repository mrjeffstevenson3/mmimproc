c fitting program
c program to create t1image map from 3 different flip angle images
c here it compile command
c gfortran t1flip_with3_with3differentoutputs.f -o t1flip_with3_with3differentoutputs -ffixed-line-length-none
c input files:  t1flip_all.hdr, t1flip_all.img, out_image.hdr, out_image.img
c output files: t1image_b1corr.hdr, t1image_b1corr.img, s0image_b1corr.hdr, s0image_b1corr.img, t1image_intensitycorr.hdr, t1image_intensitycorr.img
c output files: t1image_uncorr.hdr, t1image_uncorr.img
c The t1flip_all.* contains the combined images of all of the different flip angle images
c out_image.* contains the coregistered B1map 
c t1image_b1corr.* contains the t1image using the b1map correction - T1 relaxation time
c t1image_intensitycorr.* contains the t1image using an intensity corrected image
c t1image_uncorr.* contains the t1image using NO correction
c s0image_b1corr.* contains the MR amplitude image with b1map correction

	equivalence (ihead,chead)
	character*1 chead(348)
	integer*2 ihead(174)

	character*40 cfn,cfnout
	character*1 cnmr(1024),cout(1024)
	integer*1 inmr1(1024),inmr2(1024)
	real nmr(256),imagef(256,256,136,5),outimages(256,256,136,10)
	real b1map(256,256,136)
	real out(256),cplasma(42)
	equivalence(out,cout)
	equivalence (cnmr,nmr)
	integer*2 inmr(512)
	character*1 cinmr(512)
	equivalence (inmr,inmr2)

	dimension cho(20),cr(20),rnaa(20),y(20,20),height(20)

	common /funct/ifunc

	common /xx/x,ysum

	common /fitacc/fa

	common /baseline/pbase(1000),dbase(1000),nsize

	common /flagpass/ijflag,icflag
	common /gauss/gg

	common /nrespass/nres


	common /trpass/tr

	dimension e(60),par(60)
	common /ch/chi,par,n
	character*7 c5
	character*1 c1
	include 'nmrpar.f'




	write(6,*)'enter the input flip file with all flip angles merged together .hdr '
c	read(5,*)cfn
	cfn='t1flip_all.hdr'
	do i=1,40
	if(cfn(i:i).eq.'.')iper = i

	enddo

	open(12,file = cfn,form = 'unformatted')
	do i=1,348
	call fgetc(12,chead(i),istate)
	enddo
	close(12)
	
	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	itsize = ihead(25)
	write(6,*)ixsize,iysize,izsize,itsize

c 
c read in the t1 flip data
c
	cfn(iper+1:iper+3) = 'img'
	open(11,file = cfn,form = 'unformatted')
	do it = 1,itsize
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	imagef(i,j,k,it) = nmr(i)
	if(k.eq.2.and.j.eq.128)write(6,*)'nmr ',nmr(i),i
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)
c
	open(11,file = 'out_image.img',form = 'unformatted')
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	b1map(i,j,k) = nmr(i)
	enddo  !i
	enddo  !j
	enddo  !k

	close(11)
c
c output the b1corrected t1flip maps before t1 calculations
c
	open(12,file = 't1flip_all_b1corr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)

	open(11,file = 't1flip_all_b1corr.img',form = 'unformatted')
	do it=1,itsize
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	nmr(i) = (imagef(i,j,k,it)/b1map(i,j,k))*100.0
	if(it.eq.1.and.k.eq.50.and.j.eq.120.and.i.eq.120)write(6,*)'test ',nmr(i),b1map(i,j,k),imagef(i,j,k,it)
	enddo  !i
	do i=1,ixsize*4
	call fputc(11,cnmr(i),istate)
	enddo
	enddo  !j
	enddo  !k
	enddo  !it

	close(11)


c

	isize = 3
	psav(1) = 2
	psav(2) = 10
	psav(3) = 20
c	tr = 9.5
	tr = 11.0
	pi = 3.14159
	rfactor = pi/180.0
c  intercept = s0(1-slope)
c  s0=a/(1-b)
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
c	do k=68,68
c	do j=166,166
c	do i=75,75

	if(imagef(i,j,k,1).ge.5.0)then
	do it=1,isize
c	write(6,*)'b1map ',b1map(i,j,k),psav(it),imagef(i,j,k,it),i,j,k,it
	dnmr(it) = imagef(i,j,k,it)/sin(((b1map(i,j,k)*psav(it))/100.0)*rfactor)
	pnmr(it) = imagef(i,j,k,it)/tan(((b1map(i,j,k)*psav(it))/100.0)*rfactor)
	enddo
	call linearreg(a,b)
	r1=log(b)
	r2 = -tr/r1
	outimages(i,j,k,1) = r2
	outimages(i,j,k,2) = a/(1-b)
	outimages(i,j,k,3) = b
	else
	outimages(i,j,k,1) = 0
	outimages(i,j,k,2) = 0
	outimages(i,j,k,3) = 0
	endif
	enddo
	enddo
	enddo 
c	write(6,*)'a b ',a,b,r2

	iflag1 = 0
	if(iflag1.eq.1)then
 	c5 = 'yw0.txt'
 	open(51,file = c5)
 	c5 = 'xw0.txt'
 	open(52,file = c5)
 	
	do i=1,isize
	r1 = i
	x = pnmr(i)	
	
	ysum = a + (b*x)
	write(51,*)ysum
	write(52,*)x
	enddo
	
 	c5 = 'aw0.txt'
 	open(51,file = c5)
 	c5 = 'bw0.txt'
 	open(52,file = c5)
 	
 	do i=1,isize
 	write(51,*)pnmr(i)
 	write(52,*)dnmr(i)
 	enddo
 	close(51)
 	close(52)
	endif	!iflag1
c
	open(12,file = 't1image_b1corr.img',form='unformatted')
	open(13,file = 's0image_b1corr.img',form='unformatted')
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	out(i) = outimages(i,j,k,1)
	enddo
	do i=1,ixsize*4
	call fputc(12,cout(i),istate)
	enddo
	enddo
	enddo  !k
	close(12)
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	out(i) = outimages(i,j,k,2)
	enddo
	do i=1,ixsize*4
	call fputc(13,cout(i),istate)
	enddo
	enddo
	enddo  !k
	close(13)

	ihead(25) = 1

c
	open(12,file = 't1image_b1corr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)
	open(12,file = 's0image_b1corr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)
c
c
c this is the intensity corrected t1flip without correcting the flipangles
c
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
c	do k=68,68
c	do j=166,166
c	do i=75,75

	if(imagef(i,j,k,1).ge.5.0)then
	do it=1,isize
c	write(6,*)'b1map ',b1map(i,j,k),psav(it),imagef(i,j,k,it),i,j,k,it
	dnmr(it) = (imagef(i,j,k,it)/b1map(i,j,k))*100.0/sin(psav(it)*rfactor)
	pnmr(it) = (imagef(i,j,k,it)/b1map(i,j,k))*100.0/tan(psav(it)*rfactor)
	enddo
	call linearreg(a,b)
	r1=log(b)
	r2 = -tr/r1
	outimages(i,j,k,1) = r2
	outimages(i,j,k,2) = a/(1-b)
	outimages(i,j,k,3) = b
	else
	outimages(i,j,k,1) = 0
	outimages(i,j,k,2) = 0
	outimages(i,j,k,3) = 0
	endif
	enddo
	enddo
	enddo 
c	write(6,*)'a b ',a,b,r2

	iflag1 = 0
	if(iflag1.eq.1)then
 	c5 = 'yw0.txt'
 	open(51,file = c5)
 	c5 = 'xw0.txt'
 	open(52,file = c5)
 	
	do i=1,isize
	r1 = i
	x = pnmr(i)	
	
	ysum = a + (b*x)
	write(51,*)ysum
	write(52,*)x
	enddo
	
 	c5 = 'aw0.txt'
 	open(51,file = c5)
 	c5 = 'bw0.txt'
 	open(52,file = c5)
 	
 	do i=1,isize
 	write(51,*)pnmr(i)
 	write(52,*)dnmr(i)
 	enddo
 	close(51)
 	close(52)
	endif	!iflag1
c
	open(12,file = 't1image_intensitycorr.img',form='unformatted')
	open(13,file = 's0image_intensitycorr.img',form='unformatted')
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	out(i) = outimages(i,j,k,1)
	enddo
	do i=1,ixsize*4
	call fputc(12,cout(i),istate)
	enddo
	enddo
	enddo  !k
	close(12)
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	out(i) = outimages(i,j,k,2)
	enddo
	do i=1,ixsize*4
	call fputc(13,cout(i),istate)
	enddo
	enddo
	enddo  !k
	close(13)

	ihead(25) = 1

c
	open(12,file = 't1image_intensitycorr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)
	open(12,file = 's0image_intensitycorr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)
c
c this is the uncorrected version for debugging
c
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
c	do k=68,68
c	do j=166,166
c	do i=75,75

	if(imagef(i,j,k,1).ge.5.0)then
	do it=1,isize
c	write(6,*)'b1map ',b1map(i,j,k),psav(it),imagef(i,j,k,it),i,j,k,it
	dnmr(it) = imagef(i,j,k,it)/sin(psav(it)*rfactor)
	pnmr(it) = imagef(i,j,k,it)/tan(psav(it)*rfactor)
	enddo
	call linearreg(a,b)
	r1=log(b)
	r2 = -tr/r1
	outimages(i,j,k,1) = r2
	outimages(i,j,k,2) = a/(1-b)
	outimages(i,j,k,3) = b
	else
	outimages(i,j,k,1) = 0
	outimages(i,j,k,2) = 0
	outimages(i,j,k,3) = 0
	endif
	enddo
	enddo
	enddo 
c	write(6,*)'a b ',a,b,r2

	iflag1 = 0
	if(iflag1.eq.1)then
 	c5 = 'yw0.txt'
 	open(51,file = c5)
 	c5 = 'xw0.txt'
 	open(52,file = c5)
 	
	do i=1,isize
	r1 = i
	x = pnmr(i)	
	
	ysum = a + (b*x)
	write(51,*)ysum
	write(52,*)x
	enddo
	
 	c5 = 'aw0.txt'
 	open(51,file = c5)
 	c5 = 'bw0.txt'
 	open(52,file = c5)
 	
 	do i=1,isize
 	write(51,*)pnmr(i)
 	write(52,*)dnmr(i)
 	enddo
 	close(51)
 	close(52)
	endif	!iflag1
c
	open(12,file = 't1image_uncorr.img',form='unformatted')
	open(13,file = 's0image_uncorr.img',form='unformatted')
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	out(i) = outimages(i,j,k,1)
	enddo
	do i=1,ixsize*4
	call fputc(12,cout(i),istate)
	enddo
	enddo
	enddo  !k
	close(12)
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	out(i) = outimages(i,j,k,2)
	enddo
	do i=1,ixsize*4
	call fputc(13,cout(i),istate)
	enddo
	enddo
	enddo  !k
	close(13)

	ihead(25) = 1

c
	open(12,file = 't1image_uncorr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)
	open(12,file = 's0image_uncorr.hdr',form = 'unformatted')
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)



c
c
c
	stop
	end

c

	subroutine opti

	dimension p(60)

	common /ch/chi,p,n

C

	include 'nmrpar.f'

	common /parm/base1,nres1

	common /funct/ifunc1

	common /fitacc/fa

	common /ee/e

C

c

C	AUTHOR: TR 

C	PROGRAM TO FIT A SET OF POINTS TO ANY FUNCTION SPECIFIED

C	IN FUNCTION2.FOR

c

C

	nres1=n

c	WRITE(6,*)'p',(P(i),i=1,n),isize

c	write(6,*)'dnmr',(dnmr(i),i=1,isize)

	call cxfit

c

c	write(6,82)(p(i),i=1,n)

c	write(6,*)'chi ',chi

82	format(' FITTED PARAMETER VALUES P(I)= ',7F10.2,

     1 ' FITTED CHI-SQUARE  CHI= ',F10.4)

c

 1001	continue

 1000	continue

c

	return

	end

c  file name -- calcfid.for

c

	subroutine calcfid

c

c

	dimension p(60)

c

C

	include 'nmrpar.f'

	common /xx/xv,func

	common /parm/d5,nres

	common /funct/ifunc

	common /ch/chi,p,n

	common /cc/c1,i

c

	chi=0.

c	write(6,9)p

 9	format(1x,'p',6f10.4)

c 	write(6,*)'param ',p(1),P(2),P(3)

	do 10 i=1,isize

	xv = pnmr(i)

	CALL FUNCTION2

c	TYPE *,'PARM',P(1),P(2),p(3)

C	FUNC=FUNC+P(3)

c	write(6,*)'pnmr,func,dnmr',xv,func,dnmr(i)

	c1=(func - dnmr(i))**2

	chi=chi+c1

c	write(6,*)'chi ',chi

10	continue

c

c	write(6,*)'chi ',chi

	return

	end

c  file name -- cxfit.for

c  author -- W R HOLLEY

c  date -- 7 nov 80

c

	subroutine cxfit

c

c  Program to call general least square fitting routine VA04A

c	x -- parameters of fit -- initialized with "best" guess values -- 

c	     returned with fitted values

c	e -- "accuracy" required of fit

c	n -- Number of parameters to be fit

c	chi -- value of fitted chi-square

c	escale -- factor determining stepsize ( =escale*e(i)? )

c	iprint -- flag for print out (0,1,2) -- 0 for minimum P O

c	icon -- flag for convergence -- try =1

c	maxit -- maximum number of iterations allowed

c

c

	dimension e(60),x(60)

	common /fitacc/fa

	common /ch/chi,x,n

	common /ee/e

c

	escale=1.

	iprint=2

	icon=1

	maxit=50

c

c	write(6,*)'e,x in cx',e,x,n

	do 110 i=1,n

 	e(i)=abs(x(i)/fa)

c 	write(6,*)e(i),i,n

 110	continue

c

	do 120 i=1,n

 120	if(e(i).eq.0.)e(i)=.01

c

c	write(6,*)'n in cx#2',n

c

	call va04a(escale,iprint,icon,maxit)

	return

	end

C  FILE NAME -- VA04A.FOR

C  SUBROUTINE TO DO NON-LINEAR LEAST SQUARES FITTING

C

	SUBROUTINE VA04A(escale,iprint,icon,maxit)

c

	dimension e(60),x(60)

	common /fitacc/fapass

	common /ch/f,x,n

	common /ee/e

	common /ww/ w(10000)	

c  ! Workspace dim =n*n+3*n (n=30 ok)

	dimension delx(30)	

c  ! OK for n up to 20

c

	lto=6		 

c  ! Lun for message OP -- set for terminal here

c

c	write(6,*)'p in va ',x,n

	fa = fapass

	ddmag=0.1*escale

	scer=0.05/escale

	jj=n*n+n

	jjj=jj+n

	k=n+1

	nfcc=1

	ind=1

	inn=1

c

	do 1 i=1,n

	do 2 j=1,n

	w(k)=0.

	if(i-j)4,3,4

3	w(k)=abs(e(i))

	w(i)=escale

4	k=k+1

2	continue

	iterc=1

1	continue

c

	isgrad=2

	call calcfid	

c  ! Initial calc of chi-sq

	fkeep=abs(f)+abs(f)

5	itone=1

	fp=f

	sum=0.

	ixp=jj

c

	do 6 i=1,n

	ixp=ixp+1

	w(ixp)=x(i)

6	continue

c

	idirn=n+1

	iline=1

7	dmax=w(iline)

	dacc=dmax*scer

	dmag=min(ddmag,0.1*dmax)

	dmag=max(dmag,20.*dacc)

	ddmax=10.*dmag

	go to (70,70,71), itone

70	dl=0.

	d=dmag

	fprev=f

	is=5

	fa=f

	da=dl

8	dd=d-dl

	dl=d

58	k=idirn

c

	do 9 i=1,n

	x(i)=x(i)+dd*w(k)

	k=k+1

9	continue

c

	fstore=f

	call calcfid

c  ! Calculate chi-sq

	nfcc=nfcc+1
	if(nfcc.gt.500)return

	go to (10,11,12,13,14,96), is

14	if(f-fa)15,16,24

16	if(abs(d)-dmax)17,17,18

17	d=d+d

	go to 8

18	write(lto,19)

19	format(5x,44hVA04A maximum change does not alter function)

	go to 20

15	fb=f

	db=d

	go to 21

24	fb=fa

	db=da

	fa=f

	da=d

21	go to (83,23), isgrad

23	d=db+db-da

	is=1

	go to 8

83	d=0.5*(da+db-(fa-fb)/(da-db))

	is=4

	if((da-d)*(d-db))25,8,8

25	is=1

	if(abs(d-db)-ddmax)8,8,26

26	d=db+sign(ddmax,db-da)

	is=1

	ddmax=ddmax+ddmax

	ddmag=ddmag+ddmag

	if(ddmax-dmax)8,8,27

27	ddmax=dmax

	go to 8

13	if(f-fa)28,23,23

28	fc=fb

	dc=db

29	fb=f

	db=d

	go to 30

12	if(f-fb)28,28,31

31	fa=f

	da=d

	go to 30

11	if(f-fb)32,10,10

32	fa=fb

	da=db

	go to 29

71	dl=1.

	ddmax=5.

	fa=fp

	da=-1.

	fb=fhold

	db=0.

	d=1.

10	fc=f

	dc=d

30	ak=(db-dc)*(fa-fc)

	b=(dc-da)*(fb-fc)

	if((ak+b)*(da-dc))33,33,34

33	fa=fb

	da=db

	fb=fc

	db=dc

	go to 26

34	d=0.5*(ak*(db+dc)+b*(da+dc))/(ak+b)

	di=db

	fi=fb

	if(fb-fc)44,44,43

43	di=dc

	fi=fc

44	go to (86,86,85), itone

85	itone=2

	go to 45

86	if(abs(d-di)-dacc)41,41,93

93	if(abs(d-di)-0.03*abs(d))41,41,999

999	if(abs(f-fstore)-0.01*abs(f))41,41,45

45	if((da-dc)*(dc-d)) 47,46,46

46	fa=fb

	da=db

	fb=fc

	db=dc

	go to 25

47	is=2

	if((db-d)*(d-dc)) 48,8,8

48	is=3

	go to 8

41	f=fi

	d=di-dl

	dd=sqrt((dc-db)*(dc-da)*(da-db)/(ak+b))

c

	do 49 i=1,n

	x(i)=x(i)+d*w(idirn)

	w(idirn)=dd*w(idirn)

c

c  **************

c	delx(i)=w(idirn)

c  **************

c

	idirn=idirn+1

49	continue

c

	w(iline)=w(iline)/dd

	iline=iline+1

	if(iprint-1)51,50,51

c50	write(lto,52) iterc,nfcc,f,(x(i),i=1,n)

50	CONTINUE

52	format(/1x,9hiteration,i5,i15,16h function values,

     1 10x,'f=',e16.7/(1x,8e16.7))

	go to (51,53),iprint

51	go to (55,38), itone

55	if(fprev-f-sum) 94,95,95

95	sum=fprev-f

	jil=iline

94	if(idirn-jj) 7,7,84

84	go to (92,72), ind

92	fhold=f

	is=6

	ixp=jj

c

	do 59 i=1,n

	ixp=ixp+1

	w(ixp)=x(i)-w(ixp)

59	continue

c

	dd=1.

	go to 58

96	go to (112,87), ind

112	if(fp-f)37,37,91

91	d=2.*(fp+f-2.*fhold)/(fp-f)**2

	if(d*(fp-fhold-sum)**2-sum) 87,37,37

87	j=jil*n+1

	if(j-jj) 60,60,61

c

60	do 62 i=j,jj

	k=i-n

	w(k)=w(i)

62	continue

c

	do 97 i=jil,n

	w(i-1)=w(i)

97	continue

c

61	idirn=idirn-n

	itone=3

	k=idirn

	ixp=jj

	aaa=0.

c

	do 65 i=1,n

	ixp=ixp+1

	w(k)=w(ixp)

	if(aaa-abs(w(k)/e(i))) 66,67,67

66		aaa=abs(w(k)/e(i))

67	k=k+1

65	continue

c

	ddmag=1.

	w(n)=escale/aaa

	iline=n

	go to 7

37	ixp=jj

	aaa=0.

	f=fhold

c

	do 99 i=1,n

	ixp=ixp+1

	x(i)=x(i)-w(ixp)

	if(aaa*abs(e(i))-abs(w(ixp))) 98,99,99

98	aaa=abs(w(ixp)/e(i))

99	continue

c

	go to 72

38	aaa=aaa*(1.+di)

	go to (72,106), ind

72	if(iprint-2) 53,50,50

53	go to (109,88), ind

109	if(aaa-0.1) 89,89,76

89	go to (20,116), icon

116	ind=2

	go to (100,101),inn

100	inn=2

	k=jjj

c

	do 102 i=1,n

	k=k+1

	w(k)=x(i)

	x(1)=x(i)+10.*e(i)

102	continue

c

	fkeep=f

	call calcfid

c  ! Calc chi-sq again

	nfcc=nfcc+1

	ddmag=0.

	go to 108

76	if(f-fp) 35,78,78

c78	write(lto,80)
78	continue

80	format(5x,37hVA04A ACCURACY LIMITED BY ERRORS IN F)

	go to 20

88	ind=1

35	ddmag=0.4*sqrt(fp-f)

	isgrad=1

108	iterc=iterc+1

	if(iterc-maxit) 5,5,81

c

c  ****************

81	continue

c 81	write(lto,82) maxit

82	format(i5,' iterations completed by VA04A')

c  ****************

c

	if(f-fkeep) 20,20,110

110	f=fkeep

c

	do 111 i=1,n

	jjj=jjj+1

	x(i)=w(jjj)

111	continue

c

	go to 20

101	jil=1

	fp=fkeep

	if(f-fkeep)105,78,104

104	jil=2

	fp=f

	f=fkeep

105	ixp=jj

c

	do 113 i=1,n

	ixp=ixp+1

	k=ixp+n

	go to (114,115), jil

114	w(ixp)=w(k)

	go to 113

115	w(ixp)=x(i)

	x(i)=w(k)

113	continue

c

	jil=2

	go to 92

106	if(aaa-0.1) 20,20,107

20	continue

c

c  ***************

c	write(lto,1000)  (delx(i),i=1,n)

1000	format('0 final set of directions.'/(1p10e12.4))

c  ***************

c

	return

107	inn=1

	go to 35

	end

c

c	functions subroutine



	subroutine function2

	common /ch/chi,p,n

	common /xx/x,ysum

	common /funct/ifunc

	common /gauss/gg

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
c	if(p(inc+2).le.0)p(inc+2)=0.01
	if(p(inc+1).le.0)p(inc+1)=0.01
c	if(p(inc).le.0)p(inc)=0.01


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
c this is the equation for the dispersive part of Lorentzian
c
	
	if(ifunc.eq.7)then

	ysum=0.

	gg = p(nres*3+1)

c	write(6,*)'nres',nres,x,base

c	write(6,*)'p',p

	do 110 i=1,nres

	inc=(i-1)*3

	inc=inc+1
c	if(p(inc+2).le.0)p(inc+2)=0.01
	if(p(inc+1).le.0)p(inc+1)=0.01
c	if(p(inc).le.0)p(inc)=0.01

	conta=(x-p(inc+2))/p(inc+1)
	contfreq=(x-p(inc+2))

	conta2=conta**2

	contb=(1 + 4*conta2)

	y1=(1-gg) * (p(inc)*2*conta)/contb

	contc=-4. * alog(2.)*conta

	y2= gg * p(inc) * exp(contc)

c	write(6,*)conta,contb,contc,y1,y2

	ysum=ysum+y1+y2

 110	continue

c  	ysum=ysum + p(n-1) + (p(n)*x)

c	write(6,*)'ysum',x,ysum

	endif

c
	return

	end



c linear detrend
c
	subroutine linearreg(a,b)
	include 'nmrpar.f'
	real dtmp(1000),x(1000),y(1000)	
c
	sumx = 0
	sumy = 0
	sizex = isize
	do i=1,isize
	x(i) = pnmr(i)
	y(i) = dnmr(i)
	sumx = sumx+x(i)
	sumy = sumy+y(i)
	enddo
	averx = sumx/sizex
	avery = sumy/sizex
	sumxy = 0
	do i=1,isize
	sumxy = sumxy + ((x(i)-averx)*(y(i)-avery))
	enddo
	sumx2 = 0
	do i=1,isize
	sumx2 = sumx2+ (x(i)**2)
	enddo
	xpar1 = sumx2 - ((sumx**2)/sizex)
c	write(6,*)'averx avery sumx2 ',averx, avery, sumx2,sumxy,xpar1
	b = sumxy/xpar1
	a = avery - (b*averx)
c	write(6,*)'linear a b ',a,b
	do i=1,isize
	dtmp(i) = a + (b*x(i))
	enddo
	return
	end

