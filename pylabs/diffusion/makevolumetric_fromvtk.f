c
c read DTI fiber track vtk and quantify the FA and several other parameters
c read vtk binary file
c
	character*40 cfn,cfnin,cfnin2
	character*1 vtk(200000000),c10(10),cspace(1)
	character*1 chead(348)
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
	real out(200)
	character*1 cout(800)
	equivalence (out,cout)
	real poly(9),dnmrsav(2000000,10), polysav(2000000,5,2),tensors(2000000,9,2)
	real polyfinal(2000000,5)
	real final(10),rotation(18)
	common /rot/rotation
	integer line(6000,50000),linesav(50000)
	common /dat1/ dnmr(2000000),dnmr2(1000),dnmr3(1000)
	common /size/isize,isize2
	  DOUBLE PRECISION A(3,3)
	  DOUBLE PRECISION Q(3,3)
	  DOUBLE PRECISION W(3)
	real psavx(4),psavy(4),psavz(4),rmindistance(4),imindistance1(4),imindistance2(4)
	real distancesav(200000),imagef(200,200,200,4)
	equivalence (chead,ihead)
	equivalence (chead,rhead)
	integer*2 ihead(174)
	real rhead(87),thresh(10)

	open(11,file = 'filesize.txt')
	read(11,*)ivtksize
	close(11)
	open(11,file = 'offsets.txt')
	read(11,*)xoffset,yoffset,zoffset
	close(11)
		write(6,*)'offsets ',xoffset,yoffset,zoffset

	open(11,file = 'usechannel.txt')
	read(11,*)iusechannel
	close(11)
c

	idiff = 1
	open(11,file = 'f.vtk')
	open(21,file = 'fnew.vtk')


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

	open(11,file = 'f.vtk',form='unformatted')
	open(21,file = 'fnew.vtk',form='unformatted')


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
	call fgetc(21,cint(ii),istate)

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
	write(25,*)ilines
c	write(25,*)'1'
	close(25)



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
	if(numpointsa.gt.10000.and.numpointsa.lt.100000)then
	do i=1,42
	call fgetc(11,cnmr(i),istate)
	call fgetc(21,cnmr(i),istate)
	if(inmr(i).eq.10.and.i.gt.30)then
	write(6,*)'found endmarker for tensor ',i
	go to 299
	endif
c	write(6,*)'tensor ',cnmr(i),inmr(i),i
	enddo
 299 	continue
 	open(12,file='temp.txt')
	do ii=1,17
	call fputc(12,cnmr(ii),istate)
	enddo
	close(12)
	open(12,file='temp.txt')
	read(12,*)c6,itensors
	close(12)
	endif
c
	if(numpointsa.gt.100000)then
	do i=1,43
	call fgetc(11,cnmr(i),istate)
	call fgetc(21,cnmr(i),istate)
	if(inmr(i).eq.10.and.i.gt.30)then
	write(6,*)'found endmarker for tensor ',i
	go to 29
	endif
c	write(6,*)'tensor ',cnmr(i),inmr(i),i
	enddo
 29	continue
 	open(12,file='temp.txt')
	do ii=1,18
	call fputc(12,cnmr(ii),istate)
	enddo
	close(12)
	open(12,file='temp.txt')
	read(12,*)c6,itensors
	close(12)
	endif

c
	if(numpointsa.lt.10000)then
	do i=1,40
	call fgetc(11,cnmr(i),istate)
	call fgetc(21,cnmr(i),istate)
	if(inmr(i).eq.10.and.i.gt.30)then
	write(6,*)'found endmarker for tensor ',i
	go to 2999
	endif
c	write(6,*)'tensor ',cnmr(i),inmr(i),i
	enddo
 2999 	continue
 	open(12,file='temp.txt')
	do ii=1,16
	call fputc(12,cnmr(ii),istate)
	enddo
	close(12)
	open(12,file='temp.txt')
	read(12,*)c6,itensors
	close(12)
	endif


	write(6,*)'number of tensors ',c6,itensors
c	read(11,*)c6,itensors
c	write(6,*)'number of tensors ',c6,itensors
c	read(11,*)c6
c	write(6,*)c6
c
c now read in the s0 file 
c
	open(41,file = 'S0.hdr',form='unformatted')
	do i=1,348
	call fgetc(41,chead(i),istate)
	enddo

	close(41)


	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	itsize = ihead(25)
		
	write(6,*) 'ixsize ',ixsize,iysize,izsize,itsize
	write(6,*)'ihead(21) ',ihead(21)
	do i=1,30
c	write(6,*)rhead(i),ihead(i),i
	enddo
	rxdim = rhead(21)
	rydim = rhead(22)
	rzdim = rhead(23)
	ihead(21) = 4
	ihead(25) = 4
	ihead(36) = 16
	ihead(37) = 32
	open(41,file = 'newvolume.hdr',form='unformatted')
	do i=1,348
	call fputc(41,chead(i),istate)
	enddo

	close(41)


c
c now read in the tensors from input1
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
	tensors(i,ii,1) = nmr(ii)
c	write(6,*)'tensor ',nmr(ii),ii
	enddo
	diff = abs(tensors(i,1,1)-0.00018878)
c	if(i.eq.16)write(6,*)'found evil tensor ',i
	enddo  !tensors end read of tensor set 1
c
c now read in the tensors from input2
c
	do i=1,itensors
	do ii=1,9*4
	call fgetc(21,cnmr(ii),istate)
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
	tensors(i,ii,2) = nmr(ii)
c	write(6,*)'tensor ',nmr(ii),ii
	enddo
	enddo  !tensors end read of tensor set 2

c
c test output 
	do ii=1,9
c	write(6,*)'tensors 1 ',tensors(1,ii),ii
	enddo

c
c now loop through ONLY the fibers that passed through the channel
c
	inc = 1
	rmaxx = 0
	rmaxy = 0
	rmaxz = 0
	rminx = 1e10
	rminy = 1e10
	rminz = 1e10
c
c find the min and max x, y, z so I can make sure to offset properly
c  I cannot tolerate any negative numbers here once I have done the offset
c
	do it=1,4
	do iz=1,izsize
	do iy=1,iysize
	do ix=1,ixsize
	imagef(ix,iy,iz,it) = 0
	enddo
	enddo
	enddo
	enddo

	do i=1,itensors
c	if(i.gt.300000)write(6,*)'tensor test', polysav(i,1,1),i
		rminx = min(rminx,polysav(i,1,1))
		rminy = min(rminy,polysav(i,2,1))
	rminz = min(rminz,polysav(i,3,1))
	rmaxx = max(rmaxx,polysav(i,1,1))
	rmaxy = max(rmaxy,polysav(i,2,1))
	rmaxz = max(rmaxz,polysav(i,3,1))
    	enddo
	write(6,*)'rmin rmax ', rminx,rminy,rminz,rmaxx,rmaxy,rmaxz

	do i=1,itensors
	
	a(1,1) = abs(tensors(i,1,1))
	a(1,2) = abs(tensors(i,2,1))
	a(1,3) = abs(tensors(i,3,1))
	a(2,1) = abs(tensors(i,4,1))
	a(2,2) = abs(tensors(i,5,1))
	a(2,3) = abs(tensors(i,6,1))
	a(3,1) = abs(tensors(i,7,1))
	a(3,2) = abs(tensors(i,8,1))
	a(3,3) = abs(tensors(i,9,1))
	testchannel1 = tensors(i,1,2)
	testchannel2 = tensors(i,5,2)


c	write(6,*)'a ',a,testchannel1,testchannel2
c	pause
	call DSYEVJ3(A, Q, W)
	r1 = w(2)
	r2 = w(1)
	r3 = w(3)
	if(iusechannel.eq.1)then  ! when iusechannel eq 1
	if(testchannel1.eq.0.5.and.testchannel2.eq.0.5)then
	call fa_calc(r1,r2,r3,rfa1,axial,radial,rmd,volumeratio)
c	write(6,*)'rfa1 axial radial rmd volumeratio ',r1,r2,r3,rfa1,axial,radial,rmd,volumeratio,i
c	pause
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
	else  !for iusechannel for case of iusechannel eq 0
		call fa_calc(r1,r2,r3,rfa1,axial,radial,rmd,volumeratio)
	endif !for iusechannel


c
c for each set of tensors calculate FA
c

	rxsize = ixsize
	rysize = iysize
	rzsize = izsize
c	rx = (rxsize/(2.0))+(((polysav(i,1,1)/rxdim))+1)
	rx = ((polysav(i,1,1)/rxdim))+(xoffset)

c	ry = ((rysize/(2.0))+((polysav(i,2,1)/rydim))+1)-3
	ry = ((polysav(i,2,1)/rydim))+(yoffset)

	rz = ((polysav(i,3,1)/abs(rzdim))+zoffset)
c	rz = ((rzsize/2.0)+(polysav(i,3,1)/rzdim)+1)
c	rz = rzsize-((rzsize/2.0)+(polysav(i,3,1)/rzdim)-((rxsize*abs(rxdim))-(rzsize*rzdim))/(2.0)+1)
c	rz = (((rxsize/2.0)*rzdim)+polysav(i,3,1))/rzdim
c	rz = (rzsize/2.0)+(polysav(i,3,1)/rzdim)+1
	ix = nint(rx)
	iy = nint(ry)
	iz = nint(rz)

	if(i.lt.25)write(6,*)'ix iy iz ',ix,iy,iz,polysav(i,1,1),polysav(i,2,1),polysav(i,3,1),i,rzsize-((polysav(i,3,1)/abs(rzdim))+1)


c
c here is where I feed in to the new volumeric array
c
  	imagef(ix,iy,iz,1) = rfa1
    	imagef(ix,iy,iz,2) = axial
    	imagef(ix,iy,iz,3) = radial
    	imagef(ix,iy,iz,4) = rmd


	inc = inc+1

c	if(rfa1.lt.0.15)write(6,*)'fa ',rfa1,inc
	enddo  !tensors

	close(11)
	close(12)
	close(13)
c

	open(11,file= 'newvolume.img',form='unformatted')
	do it=1,4
	do iz=1,izsize
	do iy=1,iysize
	do ix=1,ixsize
	out(ix) = imagef(ix,iy,iz,it)
	enddo  !i
	do ix=1,ixsize*4
	call fputc(11,cout(ix),istate)
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)

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
	common /dat1/ dnmr(2000000),dnmr2(1000),dnmr3(1000)
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
