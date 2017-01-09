c
c read DTI fiber track vtk and quantify the FA and several other parameters
c read vtk binary file
c
	character*40 cfn,cfnin,cfnin2
	character*1 vtk(200000000),c10(10),cspace(1)
	character*5 c6
	character*37 c37
	character*11 c11
	character*60 c40
	character*1 a1,cnmr(1000000),cint(1000000),cnmr11(1000000)
	integer*1 inmr(1000000),inmr2(1000000),icint(1000000),icint2(1000000)
	integer*1 isav(1000000)
	real nmr(25000)
	integer iint(25000)
	equivalence (icint2,iint)
	equivalence (cint,icint)
	equivalence (nmr,inmr2)
	equivalence (inmr,cnmr)
	real poly(9),dnmrsav(200000,10), polysav(2000000,5,4),tensors(200000,9)
	real polyfinal(2000000,5)
	real final(10),rotation(18)
	common /rot/rotation
	integer line(6000,50000),linesav(50000)
	common /dat1/ dnmr(200000),dnmr2(1000),dnmr3(1000)
	common /size/isize,isize2
	  DOUBLE PRECISION A(3,3)
	  DOUBLE PRECISION Q(3,3)
	  DOUBLE PRECISION W(3)
	real psavx(4),psavy(4),psavz(4),rmindistance(4),imindistance1(4),imindistance2(4)
	real distancesav(200000)
	open(11,file = 'filesize.txt')
	read(11,*)ivtksize
	close(11)
c

	idiff = 1
	open(11,file = 'input1.vtk')
	open(21,file = 'input2.vtk')


	do i=1,4
	read(11,*)cfn
	read(21,*)cfn

c	write(6,*)cfn,i
	enddo
	read(11,*)c6, numpointsa
	read(21,*)c6, numpointsb

	write(6,*)c6, numpointsa
	rnum = numpointsa
	rdiv = rnum/3
	idiv = numpoints/3
	rsub = rdiv-idiv
	extra = rsub*3
	iextra = nint(extra)
	close(11)
	close(21)
	close(22)
	close(23)

	open(11,file = 'input1.vtk',form='unformatted')
	open(21,file = 'input2.vtk',form='unformatted')


c
c f.vtk
	do ifil =1,2
	do i=1,89-6
	if(ifil.eq.1)call fgetc(11,cnmr(i),istate)
	if(ifil.eq.2)call fgetc(21,cnmr(i),istate)

	if(inmr(i).eq.10.and.i.gt.70)then
	write(6,*)'found the end marker ',i
	go to 97
	endif
c	write(6,*)'test for float ',cnmr(i),inmr(i),i
	enddo  !i
 97	continue

	inc = 1
	if(ifil.eq.1)numpoints = numpointsa
	if(ifil.eq.2)numpoints = numpointsb

	do i=1,numpoints
c	do i=1,10

	do ii=1,3*4
	if(ifil.eq.1)call fgetc(11,cnmr(ii),istate)
	if(ifil.eq.2)call fgetc(21,cnmr(ii),istate)

	enddo
	incs = 1
	do ii=1,3
	inmr2(incs) = inmr(incs+3)
	inmr2(incs+1) = inmr(incs+2)
	inmr2(incs+2) = inmr(incs+1)
	inmr2(incs+3) = inmr(incs)
	incs = incs+4
	enddo
c	do ii=1,9
c	write(6,*)'inmr ',inmr(ii),ii
c	enddo
c	pause

	do ii=1,3
	poly(ii) = nmr(ii)
	enddo
	polysav(inc,1,ifil) = poly(1)
	polysav(inc,2,ifil) = poly(2)
	polysav(inc,3,ifil) = poly(3)
	polysav(inc,4,ifil) = inc
	if(i.eq.1)then
	write(6,*)'poly1 ',poly(1),poly(2),poly(3),inc
	endif
	inc = inc+1
	enddo
c
	write(6,*)poly(1),poly(2),poly(3),inc
	
c	read(11)c6
c	write(6,*)'enter offset '
c	read(5,*)ioffset
	ioffset=19
	do ii=1,ioffset
	if(ifil.eq.1)then
		call fgetc(11,cnmr(ii),istate)
		cnmr11(ii) = cnmr(ii)
	endif
	if(ifil.eq.2)call fgetc(21,cnmr(ii),istate)

	if(inmr(ii).eq.10.and.ii.gt.10)then
	write(6,*)'found the end marker for line index ',ii
c	write(6,*)'after numpoints1',inmr(ii),cnmr(ii),ii
	go to 199
	endif
	enddo
 199	continue

	enddo  !ifil for each vtk file
	close(21)
	close(22)
	close(23)
 
	open(12,file='templines.txt')
	do ii=2,14
	call fputc(12,cnmr11(ii),istate)
	enddo
	close(12)
	open(12,file='templines.txt')
	read(12,*)c6,ilines,i1
	close(12)


	write(6,*)'number of fibers ',c6,ilines,iend

	write(6,*)'number of fibers iend idiff ',c6,ilines,iend,idiff


	do i=1,ilines
c	do i=1,1

	do ii=1,1*4
	call fgetc(11,cint(ii),istate)
	call fgetc(21,cint(ii),istate)

c	write(6,*)'after fibers ',cint(ii),icint(ii),ii
	enddo
	inc = 1
	icint2(inc) = icint(inc+3)
	icint2(inc+1) = icint(inc+2)

	icint2(inc+2) = icint(inc+1)
	icint2(inc+3) = icint(inc)


	isublines = iint(1)
c	write(6,*)'isublines ',isublines,i
c	if(isublines.lt.2.or.isublines.gt.10000)then
c	idiff = idiff+1
c	write(6,*)'finding the offset automatically '
c	
c	close(11)
c	close(12)
c	go to 99
c	endif
c
	if(i.eq.1)write(6,*)'isublines ',isublines,i
	line(i,1) = isublines
	do ii=1,(isublines)*4
	call fgetc(11,cint(ii),istate)
	enddo

	inc = 1
	do ii=1,isublines
	icint2(inc) = icint(inc+3)
	icint2(inc+1) = icint(inc+2)
	icint2(inc+2) = icint(inc+1)
	icint2(inc+3) = icint(inc)

	inc = inc+4
	line(i,ii+1) = iint(ii)
	enddo
	if(i.eq.112)then
c	write(6,*)'line ',line(i,1),(line(i,ii),ii=2,line(i,1)+1)

	endif
c	write(6,*)'line ',line(i,1),line(i,2),i
c	if(i.eq.1)then
c	write(6,*)'first line ',line(i,1),(line(i,ii),ii=2,line(i,1)+1)
c	endif
c	pause


	enddo  !lines main

	write(6,*)'this is indexing for the last line '
	write(6,*)line(ilines,1),(line(ilines,ii),ii=2,line(ilines,1)+1)
	

c
c	write(6,*)line(500,1),(line(500,ii),ii=2,line(500,1)+1)
c
c find the length of each line
c
	open(12,file = 'poly1.txt')
	open(13,file = 'poly2.txt')
	open(33,file = 'poly3.txt')
	open(14,file = 'polynum.txt')
	open(22,file = 'polysub1.txt')
	open(23,file = 'polysub2.txt')
	open(34,file = 'polysub3.txt')

	open(24,file = 'polysubnum.txt')
	open(25,file = 'polytot.txt')
	open(26,file = 'testchannel.txt')
	open(27,file = 'survivinglines.txt')
	open(28,file = 'survivingcount.txt')
	write(25,*)ilines
c	write(25,*)'1'
	close(25)

	ibad = 0
	igood = 0
	ifinalinc = 1
	write(6,*)'ilines numpointsb numpointc ', ilines, numpointsb, numpointsc
	write(26,*)ilines
	do i=1,ilines
c	do i=280,280
	do ifil=2,4
	if(ifil.eq.2)numpoints = numpointsb
	if(ifil.eq.3)numpoints = numpointsc
	if(ifil.eq.4)numpoints = numpointsd

	sum = 0
	if(ifil.eq.2)ipsize = 0
c	write(6,*)'line ',line(i,1)+1,numpoints/3
	rmaxz = -10000.0
	rminz = 10000.0
	rmindistance(ifil) = 100000.0
	icountone = 0
	countsubline = 0
	do ii=2,line(i,1)+1
	icountone = icountone+1
	enddo

	if(ifil.eq.4)write(26,*)icountone
	do ii=2,line(i,1)+1
c	write(6,*)'inside line ',line(i,ii),ii

c	write(6,*)'polysav(ip,4) ',polysav(ip,4),ip
	dx = polysav(line(i,ii+4)+1,1,1)- polysav(line(i,ii)+1,1,1)
	dy = polysav(line(i,ii+4)+1,2,1)- polysav(line(i,ii)+1,2,1)
	dz = polysav(line(i,ii+4)+1,3,1)- polysav(line(i,ii)+1,3,1)
	rmaxz = max(polysav(line(i,ii)+1,3,1),rmaxz)
	rminz = min(polysav(line(i,ii)+1,3,1),rminz)
	if(rmaxz.eq.polysav(line(i,ii)+1,3,1))imaxz=ii
	if(rminz.eq.polysav(line(i,ii)+1,3,1))iminz=ii
	if(ifil.eq.2)then
	write(12,*)polysav(line(i,ii)+1,1,1)
	write(13,*)polysav(line(i,ii)+1,2,1)
	write(33,*)polysav(line(i,ii)+1,3,1)
	ipsize = ipsize+1
	endif


	distance = sqrt((dx**2)+(dy**2)+(dz**2))
	polysav(line(i,ii)+1,5,1)= distance
c	if(ii.le.600)write(6,*)'distance ',distance,line(i,ii)+1,i,ii
	sum = sum+distance
	countsubline = countsubline+1
	endif

	enddo  !ifil


	enddo  !ii within lines within the fiber tract
	rcountone = icountone
	rfraction_subline = countsubline/rcountone   !this is the fraction of points within the line that stay within channel

c  write model line to disk
c
c  for the rmaxz find the closest cortex model point
c


c	write(6,*)'distance ',dnmr(i),i,ipsize
	write(14,*)ipsize

	enddo  !between lines with index i
	close(26)
	close(27)
	write(28,*)igood
	close(28)


	ifinalcount = ifinalinc-1
	close(12)
	close(13)
	close(14)


	write(6,*)'mark 1'
	close(12)
	close(13)
	close(14)
	close(22)
	close(23)
	close(24)
	close(33)
	close(34)
	open(25,file = 'polytotsub.txt')
	write(25,*)incpass-1
	close(25)


	write(6,*)'the number of fibers is ', ilines
c	write(6,*)'update 40-3 '
	if(numpointsa.gt.10000)then
	do i=1,42
	call fgetc(11,cnmr(i),istate)
	if(inmr(i).eq.10.and.i.gt.30)then
	write(6,*)'found endmarker for tensor ',i
	go to 299
	endif
c	write(6,*)'tensor ',cnmr(i),inmr(i),i
	enddo
 299 	continue
	endif
c
	if(numpointsa.lt.10000)then
	do i=1,40
	call fgetc(11,cnmr(i),istate)
	if(inmr(i).eq.10.and.i.gt.30)then
	write(6,*)'found endmarker for tensor ',i
	go to 2999
	endif
c	write(6,*)'tensor ',cnmr(i),inmr(i),i
	enddo
 2999 	continue
	endif


	open(12,file='temp.txt')
	do ii=1,17
	call fputc(12,cnmr(ii),istate)
	enddo
	close(12)
	open(12,file='temp.txt')
	read(12,*)c6,itensors
	close(12)
	write(6,*)'number of tensors ',c6,itensors
c	read(11,*)c6,itensors
c	write(6,*)'number of tensors ',c6,itensors
c	read(11,*)c6
c	write(6,*)c6

c
c now read in the tensors
c
	do i=1,itensors
	do ii=1,9*4
	call fgetc(11,cnmr(ii),istate)
	enddo
	incs = 1
	do ii=1,9
c	inmr2(incs) = inmr(incs+3)
c	inmr2(incs+1) = inmr(incs+2)
c	inmr2(incs+2) = inmr(incs+1)
c	inmr2(incs+3) = inmr(incs)
	inmr2(incs+3) = inmr(incs)
	inmr2(incs+2) = inmr(incs+1)
	inmr2(incs+1) = inmr(incs+2)
	inmr2(incs) = inmr(incs+3)

	incs = incs+4
	enddo

	do ii=1,9
	tensors(i,ii) = nmr(ii)
c	write(6,*)'tensor ',nmr(ii),ii
	enddo
	diff = abs(tensors(i,1)-0.00018878)
c	if(i.eq.16)write(6,*)'found evil tensor ',i
	enddo  !ilines
	do ii=1,9
c	write(6,*)'tensor ',tensors(16,ii),i
	enddo
c
c test output 
	do ii=1,9
c	write(6,*)'tensors 1 ',tensors(1,ii),ii
	enddo
	do ii=1,9
c	write(6,*)'tensors end ',tensors(itensors,ii),ii
	enddo

c
c now loop through ONLY the fibers that passed through the box
c
	inc = 1
	rmaxr1 = 0
	rmaxr2 = 0
	rmaxr3 = 0
	do i=1,itensors
	
	a(1,1) = abs(tensors(i,1))
	a(1,2) = abs(tensors(i,2))
	a(1,3) = abs(tensors(i,3))
	a(2,1) = abs(tensors(i,4))
	a(2,2) = abs(tensors(i,5))
	a(2,3) = abs(tensors(i,6))
	a(3,1) = abs(tensors(i,7))
	a(3,2) = abs(tensors(i,8))
	a(3,3) = abs(tensors(i,9))
c	if(i.eq.4533)write(6,*)'a ',a
	call DSYEVJ3(A, Q, W)
	r1 = w(2)
	r2 = w(1)
	r3 = w(3)
	if(a(1,1).eq.0.1.and.a(2,2).eq.0.1)then
	call fa_calc(r1,r2,r3,rfa1,axial,radial,rmd,volumeratio)
	else
	r1 = 0
	r2 =0
	r3 = 0
	rfa1=0
	axial =0
	radial = 0
	rmd = 0
	volumeratio=0
	endif

c
c for each set of tensors calculate FA
c
	dnmrsav(inc,1) = rfa1
	dnmrsav(inc,2) = axial
	dnmrsav(inc,3) = radial
	dnmrsav(inc,4) = rmd
	dnmrsav(inc,5) = volumeratio

	inc = inc+1
c	write(6,*)'rfa1 axial radial rmd volumeratio ',r1,r2,r3,rfa1,axial,radial,rmd,volumeratio,i
c	if(rfa1.lt.0.15)write(6,*)'fa ',rfa1,inc
	rmaxr1 = max(rmaxr1,abs(r1))
	rmaxr2 = max(rmaxr2,abs(r2))
	rmaxr3 = max(rmaxr3,abs(r3))
	enddo  !tensors
	isizeb = inc-1
	write(6,*)'did you make it this far isizeb rmaxr1',isizeb,rmaxr1,rmaxr2,rmaxr3

	do ifil=1,5
	inc2 = 1
		do i=1,isizeb
		do ii=1,ifinalcount
		ipoly = polyfinal(ii,1)
		if(i.eq.ipoly.and.dnmrsav(i,1).ne.0)then
		dnmr(inc2) = dnmrsav(i,ifil)
c		write(6,*)'dnmr(inc2) ',dnmr(inc2),inc2,i,ii

		inc2 = inc2+1
		endif
		enddo   !ii
		enddo  !i

	isize = inc2-1
	if(isize.gt.0)then
	call average(aver,stdev,ste)
	final(ifil) = aver
	else
	aver = 0
	stdev = 0
	final(ifil)=0
	endif
	write(6,*)'average stdev ',aver,stdev,ifil,final(ifil),isize
	enddo
	final(6) = averlength
	final(7) = igood
	final(8) = igood+ibad
	open(20,file = 'dti_header.txt')
	open(19,file = 'dti_results.txt')
	write(20,*)'fa ','ax ','ra ','md ','vo ','len ','fnum '
	write(19,*)(final(ii),ii=1,8)
	close(19)
	close(20)
	write(6,*)'fa = DTI fractional anisotropy '
	write(6,*)'ax = DTI axial diffusivity '
	write(6,*)'ra = DTI radial diffusivity '
	write(6,*)'md = DTI mean diffusivity '
	write(6,*)'vo = DTI volume ratio '
	write(6,*)'len = average DTI fiber length '
	write(6,*)'fnum = number of DTI fiber '

	close(11)
	close(12)
	close(13)
c
c  this is the part to write out the new vtk file 
c
	isize = ivtksize
	open(11,file = 'f.vtk')
	open(31,file = 'fnew.vtk',form='unformatted')
	do i=1,isize
	call fgetc(11,vtk(i),istate)
	enddo
	do i=1,isize
	if(vtk(i).eq.'T'.and.vtk(i+1).eq.'E'.and.vtk(i+2).eq.'N')then
	iset = i
	endif
	enddo
c
c write to new file everything up to the point of the tensor part
c
	do i=1,iset+22
	call fputc(31,vtk(i),istate)
	enddo

	write(6,*)'iset ',iset
	do i=iset,iset+40
	write(6,*)'vtk ',vtk(i),i
	enddo
	close(11)
c
c
c now write out the tensors to new vtk file with conditional colors based on channel pass through
c
	do i=1,itensors   !between tensors
c
c this part below will repaint the tensor a different color if the fiber 
c went through the channel
c  if the fiber does not pass through the channel it will remain
c with its normal tensor color
c
		do ii=1,ifinalcount
		ipoly = polyfinal(ii,1)
		if(i.eq.ipoly.and.dnmrsav(i,1).ne.0)then
		poly(1) = 0.5
		poly(2) = 0
		poly(3) = 0
		poly(4) = 0
		poly(5) = 0.5
		poly(6) = 0
		poly(7) = 0
		poly(8) = 0
		poly(9) = 0.5
		do it=1,9
		tensors(i,it) = poly(it)
		enddo
	endif
		enddo   !ii

	do ii=1,9         !within tensor
	nmr(ii)= tensors(i,ii)
	enddo
	incs = 1
	do ii=1,9        !within tensor
	inmr(incs+3)= inmr2(incs)
	inmr(incs+2)= inmr2(incs+1) 
	inmr(incs+1)= inmr2(incs+2)
	inmr(incs)  = inmr2(incs+3)
	incs = incs+4
	enddo  !within tensor

	do ii=1,9*4
	call fputc(31,cnmr(ii),istate)
	enddo  !within tensor

	enddo  !between tensor

	close(31)

	stop
	end
c
c  calculate the fractional anisotropy
c
	subroutine fa_calc(r1,r2,r3, rfa,axial,radial,rmd,volumeratio)
	r1 = abs(r1)
	r2 = abs(r2)
	r3 = abs(r3)
c
	trace = (r1+r2+r3)/3.0
	axial = r1
	radial = (r2+r3)/2.0
	rmd = trace

	rnum = ((r1-r2)**2) + ((r2-r3)**2) + ((r3-r1)**2)
	rnum2 =rnum
	rdenom = (r1**2) + (r2**2) + (r3**2)
	rdenom2 = (2.0*rdenom)
	rfa = sqrt( rnum2 / rdenom2)
	if(trace.ne.0.0)then
	volumeratio = (r1*r2*r3)/(trace**3)
	else
	volumeratio = 0
	endif
	volumeratio = 1.0
c	write(6,*)(r1*r2*r3),trace**3

	return
	end

	subroutine average(aver,stdev,stem)
	common /dat1/ dnmr(200000),dnmr2(1000),dnmr3(1000)
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

* ----------------------------------------------------------------------------
* Numerical diagonalization of 3x3 matrcies
* Copyright (C) 2006  Joachim Kopp
* ----------------------------------------------------------------------------
* This library is free software; you can redistribute it and/or
* modify it under the terms of the GNU Lesser General Public
* License as published by the Free Software Foundation; either
* version 2.1 of the License, or (at your option) any later version.
*
* This library is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
* Lesser General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public
* License along with this library; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
* ----------------------------------------------------------------------------


* ----------------------------------------------------------------------------
	  SUBROUTINE DSYEVJ3(A, Q, W)
* ----------------------------------------------------------------------------
* Calculates the eigenvalues and normalized eigenvectors of a symmetric 3x3
* matrix A using the Jacobi algorithm.
* The upper triangular part of A is destroyed during the calculation,
* the diagonal elements are read but not destroyed, and the lower
* triangular elements are not referenced at all.
* ----------------------------------------------------------------------------
* Parameters:
*   A: The symmetric input matrix
*   Q: Storage buffer for eigenvectors
*   W: Storage buffer for eigenvalues
* ----------------------------------------------------------------------------
*     .. Arguments ..
	  DOUBLE PRECISION A(3,3)
	  DOUBLE PRECISION Q(3,3)
	  DOUBLE PRECISION W(3)

*     .. Parameters ..
	  INTEGER          N
	  PARAMETER        ( N = 3 )

*     .. Local Variables ..
	  DOUBLE PRECISION SD, SO
	  DOUBLE PRECISION S, C, T
	  DOUBLE PRECISION G, H, Z, THETA
	  DOUBLE PRECISION THRESH
	  INTEGER          I, X, Y, R

*     Initialize Q to the identitity matrix
*     --- This loop can be omitted if only the eigenvalues are desired ---
	  DO 10 X = 1, N
		Q(X,X) = 1.0D0
		DO 11, Y = 1, X-1
		  Q(X, Y) = 0.0D0
		  Q(Y, X) = 0.0D0
   11   CONTINUE
   10 CONTINUE

*     Initialize W to diag(A)
	  DO 20 X = 1, N
		W(X) = A(X, X)
   20 CONTINUE

*     Calculate SQR(tr(A))  
	  SD = 0.0D0
	  DO 30 X = 1, N
		SD = SD + ABS(W(X))
   30 CONTINUE
	  SD = SD**2
 
*     Main iteration loop
	  DO 40 I = 1, 50
*       Test for convergence
		SO = 0.0D0
		DO 50 X = 1, N
		  DO 51 Y = X+1, N
			SO = SO + ABS(A(X, Y))
   51     CONTINUE
   50   CONTINUE
		IF (SO .EQ. 0.0D0) THEN
		  RETURN
		END IF

		IF (I .LT. 4) THEN
		  THRESH = 0.2D0 * SO / N**2
		ELSE
		  THRESH = 0.0D0
		END IF

*       Do sweep
		DO 60 X = 1, N
		  DO 61 Y = X+1, N
			G = 100.0D0 * ( ABS(A(X, Y)) )
			IF ( I .GT. 4 .AND. ABS(W(X)) + G .EQ. ABS(W(X)).AND. ABS(W(Y)) + G .EQ. ABS(W(Y)) ) THEN
			  A(X, Y) = 0.0D0
			ELSE IF (ABS(A(X, Y)) .GT. THRESH) THEN
*             Calculate Jacobi transformation
			  H = W(Y) - W(X)
			  IF ( ABS(H) + G .EQ. ABS(H) ) THEN
				T = A(X, Y) / H
			  ELSE
				THETA = 0.5D0 * H / A(X, Y)
				IF (THETA .LT. 0.0D0) THEN
				  T = -1.0D0 / (SQRT(1.0D0 + THETA**2) - THETA)
				ELSE
				  T = 1.0D0 / (SQRT(1.0D0 + THETA**2) + THETA)
				END IF
			  END IF

			  C = 1.0D0 / SQRT( 1.0D0 + T**2 )
			  S = T * C
			  Z = T * A(X, Y)

*             Apply Jacobi transformation
			  A(X, Y) = 0.0D0
			  W(X)    = W(X) - Z
			  W(Y)    = W(Y) + Z
			  DO 70 R = 1, X-1
				T       = A(R, X)
				A(R, X) = C * T - S * A(R, Y)
				A(R, Y) = S * T + C * A(R, Y)
   70         CONTINUE
			  DO 80, R = X+1, Y-1
				T       = A(X, R)
				A(X, R) = C * T - S * A(R, Y)
				A(R, Y) = S * T + C * A(R, Y)
   80         CONTINUE
			  DO 90, R = Y+1, N
				T       = A(X, R)
				A(X, R) = C * T - S * A(Y, R)
				A(Y, R) = S * T + C * A(Y, R)
   90         CONTINUE

*             Update eigenvectors
*             --- This loop can be omitted if only the eigenvalues are desired ---
			  DO 100, R = 1, N
				T       = Q(R, X)
				Q(R, X) = C * T - S * Q(R, Y)
				Q(R, Y) = S * T + C * Q(R, Y)
  100         CONTINUE
			END IF
   61     CONTINUE
   60   CONTINUE
   40 CONTINUE

	  PRINT *, "DSYEVJ3: No convergence."

	  END SUBROUTINE
* End of subroutine DSYEVJ3
c
	subroutine rotate
	real rotation(18)
	common /rot/rotation

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

	cosrotx = rotation(5)
	sinrotx = rotation(6)
	rx = rotation(13)
	ry = rotation(14)
	rz = rotation(15)
	rxwid = rotation(16)
	rywid = rotation(17)
	rzwid = rotation(18)
	rmidrotx = 0
	rmidroty = 0
	rmidrotz = 0
	rpointx = rx+rxwid
	rpointy = ry+rywid
	rpointz = rz-rzwid
		  r2y = (cosrotx*(rpointy-rmidroty))+(sinrotx*(rpointz-rmidrotz))
		  r3z = (-sinrotx*(rpointy-rmidroty)) + (cosrotx*(rpointz-rmidrotz))
	write(6,*)rpointx,rpointy,rpointz,rpointx,r2y,r3z
	  r4x = (cosroty*(rpointx-rmidrotx))+(sinroty*(r3z-rmidrotz))
		  r5z = (-sinroty*(rpointx-rmidrotx)) + (cosroty*(r3z-rmidrotz))
	write(6,*)rpointx,rpointy,rpointz,rx4,r2y,r5z
	  r6x = (cosrotz*(r4x-rmidrotx))+(sinrotz*(r2y-rmidroty))
		  r7y = (-sinrotz*(r4x-rmidrotx)) + (cosrotz*(r2y-rmidroty))
	write(6,*)rpointx,rpointy,rpointz,r6x,r7y,r5z

	return
	end

