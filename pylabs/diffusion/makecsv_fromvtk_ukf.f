c
c read DTI fiber track vtk and quantify the FA and several other parameters
c read vtk binary file
c
	character*40 cfn,cfnin,cfnin2
	character*1 vtk(200000000),c10(10),cspace(1)
	integer*1  ivtk(200000000)
	equivalence (vtk,ivtk)
	character*1 chead(348)
	character*5 c6
	character*37 c37
	character*11 c11
	character*60 c40
	character*1 a1,cnmr(1000000),cint(1000000),cnmr11(1000000)
	integer*1 inmr(1000000),inmr2(1000000),icint(1000000),icint2(1000000)
	integer*1 isav(1000000)
	real nmr(25000),rsize(20)
	integer iint(25000)
	equivalence (icint2,iint)
	equivalence (cint,icint)
	equivalence (nmr,inmr2)
	equivalence (inmr,cnmr)
	real out(200)
	character*1 cout(800)
	equivalence (out,cout)
	real poly(9),dnmrsav(2000000,20), polysav(2000000,20),tensors(2000000,9,10)
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
	character*5 c6ufk

	open(11,file = 'filesize.txt')
	read(11,*)ivtksize
	close(11)
c

	idiff = 1
	open(11,file = 'f.vtk')

	do i=1,7
	read(11,*)cfn
	write(6,*)'ufk ',cfn,i
	enddo
	read(11,*)c6ufk, numpointsa

	itensors = numpointsa

	write(6,*)c6, numpointsa
	close(11)

c
c load in ukf tensors
c
	isize = ivtksize
	ivtkcounter=0
	open(31,file = 'fnew.vtk',form='unformatted')
	do i=1,isize
	call fgetc(31,vtk(i),istate)
	enddo
	close(31)
c
c  start section for FA1
	do i=1,isize
	if(vtk(i).eq.'F'.and.vtk(i+1).eq.'A'.and.vtk(i+2).eq.'1'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for fa1 with markers ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,3) = nmr(ii)  !slot 3 is for FA1 with markers for 10 sections
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors
	open(31,file = 'f.vtk',form='unformatted')
	do i=1,isize
	call fgetc(31,vtk(i),istate)
	enddo
	close(31)

c end section for FA1
c
c  start section for FA2
	do i=1,isize
	if(vtk(i).eq.'F'.and.vtk(i+1).eq.'A'.and.vtk(i+2).eq.'2'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for fa2 ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,4) = nmr(ii)  !slot 4 is for FA2
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors

c end section for FA2
c
c  start section for NormalizedSignalEstimationError
	do i=1,isize
	if(vtk(i).eq.'r'.and.vtk(i+1).eq.'o'.and.vtk(i+2).eq.'r'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+10)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+1,iset+80
	if(ivtk(i).eq.108.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for error ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,5) = nmr(ii)  !slot 5 is for NormalizedSignalEstimationError
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors

c end section for NormalizedSignalEstimationError
c  start section for tensor2
	do i=1,isize
	if(vtk(i).eq.'o'.and.vtk(i+1).eq.'r'.and.vtk(i+2).eq.'2'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for tensor2 ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,6) = nmr(ii)  !slot 6 is for tensor2
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors
c
c end section for tensor2
c  start section for EstimatedUncertainty
	do i=1,isize
	if(vtk(i).eq.'n'.and.vtk(i+1).eq.'t'.and.vtk(i+2).eq.'y'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for uncertainy ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,7) = nmr(ii)  !slot 7 is for EstimatedUncertainty
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors
c end section for EstimatedUncertainty
c  start section for trace1
	do i=1,isize
	if(vtk(i).eq.'c'.and.vtk(i+1).eq.'e'.and.vtk(i+2).eq.'1'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for trace1 ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,8) = nmr(ii)  !slot 8 is for trace1
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors
c end section for trace1
c  start section for trace2
	do i=1,isize
	if(vtk(i).eq.'r'.and.vtk(i+1).eq.'a'.and.vtk(i+2).eq.'c'.and.vtk(i+3).eq.'e'.and.vtk(i+4).eq.'2'.and.vtk(i+5).eq.' ')then
	iset = i
	write(6,*)'find float for trace2 ',iset,i,(vtk(ii),ii=i-15,i+5)
	go to 429
	endif
	enddo
 429	continue
	do i=iset,iset+30
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo

	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for trace2 ',i
	imarktensor = i+2
	endif
	enddo


c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,9) = nmr(ii)  !slot 9 is for trace2
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors

c end section for trace2
c  start section for Freewater
	do i=1,isize
	if(vtk(i).eq.'t'.and.vtk(i+1).eq.'e'.and.vtk(i+2).eq.'r'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for water ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,10) = nmr(ii)  !slot 10 is for freewater
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors

c end section for freewater
c
c  start section for tensor1
	do i=1,isize
	if(vtk(i).eq.'o'.and.vtk(i+1).eq.'r'.and.vtk(i+2).eq.'1'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for tensor1 ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,9*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (9*4)
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
	tensors(i,ii,1) = nmr(ii)  !slot 1 is for tensor1
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensors

c end section for tensor1
c
c  start section for tensor1
	do i=1,isize
	if(vtk(i).eq.'F'.and.vtk(i+1).eq.'A'.and.vtk(i+2).eq.'1'.and.vtk(i+3).eq.' ')then
	iset = i
	write(6,*)'find float ',iset,i,(vtk(ii),ii=i-15,i+5)
	endif
	enddo
	do i=iset,iset+100
c	write(6,*)'vtk ivtk ',vtk(i),ivtk(i),i,i-iset
	enddo
	do i=iset+5,iset+40
	if(ivtk(i).eq.97.and.ivtk(i+1).eq.116.and.ivtk(i+2).eq.10)then
	write(6,*)'found endmarker for FA1 ',i
	imarktensor = i+2
	endif
	enddo

c
c read in fa1 into the array tensor
c
	do i=1,itensors
	do ii=1,1*4
	cnmr(ii) = vtk(imarktensor+ii)
	enddo
	imarktensor = imarktensor + (1*4)
	incs = 1
	do ii=1,1
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

	do ii=1,1
	tensors(i,ii,2) = nmr(ii)  !slot 2 is for fa1 without markers
c	write(6,*)'tensor ',nmr(ii),ii
	enddo

	enddo  !itensoros

c end section for fa1 without markers

c
c calculate dti parameter for each of the 10 anatomical sections that
c were previously defined in readfiber_withchannel_ukf
c 10 regions and 12 dti parameters
	do ireg=1,10
	do ii=1,12
	dnmrsav(ireg,ii)= 0
	enddo
	enddo

	do ireg=1,10
	rsize(ireg) = 0
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
	testchannel1 = tensors(i,1,3)


c	write(6,*)'a ',a,testchannel1,testchannel2
c	pause
	call DSYEVJ3(A, Q, W)
	r1 = w(2)
	r2 = w(1)
	r3 = w(3)

	if(testchannel1.eq.ireg)then
	call fa_calc(r1,r2,r3,rfa1,axial,radial,rmd,volumeratio)
c	write(6,*)'rfa1 axial radial rmd volumeratio ',r1,r2,r3,rfa1,axial,radial,rmd,volumeratio,i
	dnmrsav(ireg,1)=rfa1+ dnmrsav(ireg,1)  !from tensor1 calculation
	dnmrsav(ireg,2)=axial+ dnmrsav(ireg,2) !from tensor1 calculation
	dnmrsav(ireg,3)=radial+dnmrsav(ireg,3) !from tensor1 calculation
	dnmrsav(ireg,4)=rmd+dnmrsav(ireg,4)    !from tensor1 calculation
	dnmrsav(ireg,5)=tensors(i,1,2)+ dnmrsav(ireg,5) !fa1
	dnmrsav(ireg,6)=tensors(i,1,4)+ dnmrsav(ireg,6) !fa2
	dnmrsav(ireg,7)=tensors(i,1,5)+ dnmrsav(ireg,7) !normalized error
	dnmrsav(ireg,8)=tensors(i,1,6)+ dnmrsav(ireg,8) !tensor2
	dnmrsav(ireg,9)=tensors(i,1,7)+ dnmrsav(ireg,9) !uncertainty
	dnmrsav(ireg,10)=tensors(i,1,8)+ dnmrsav(ireg,10) !trace1
	dnmrsav(ireg,11)=tensors(i,1,9)+ dnmrsav(ireg,11) !trace2
	dnmrsav(ireg,12)=tensors(i,1,10)+ dnmrsav(ireg,12) !freewater
	rsize(ireg) = rsize(ireg)+1
	endif

	enddo  !itensors
	enddo  !ireg
c
c output csv file ready for statistics
c
	open(12,file = "ukf_10regions.csv")
	write(12,*)'fa_tensor1 ad_tensor1 rd_tensor1 md_tensor1 fa1 fa2 error tensor2 uncertainty trace1 trace2 freewater'
	do ireg=1,10
	write(12,*)(dnmrsav(ireg,ii)/rsize(ireg),ii=1,12)
	enddo
	close(12)

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
