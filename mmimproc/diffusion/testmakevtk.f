c gfortran  -O3 -mcmodel=medium -g testmakevtk.f -o testmakevtk -ffixed-line-length-none
c read DTI fiber track vtk and quantify the FA and several other parameters
c read vtk binary file
c
	character*40 cfn,cfnin,cfnin2
	character*1 vtk(800000000),c10(10),cspace(1),chead(348)
	integer*1 ivtk(800000000)
	equivalence (vtk,ivtk)
	character*5 c6,c6ufk
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
	real poly(9),dnmrsav(6000000,10), polysav(7000000,5,4),tensors(7000000,9)
	real polyfinal(7000000,5)
	real final(10),rotation(18)
	common /rot/rotation
	integer line(600000,9000),linesav(90000)
	common /dat1/ dnmr(6000000),dnmr2(1000),dnmr3(1000)
	common /size/isize,isize2
	  DOUBLE PRECISION A(3,3)
	  DOUBLE PRECISION Q(3,3)
	  DOUBLE PRECISION W(3)
	real psavx(4),psavy(4),psavz(4),rmindistance(4),imindistance1(4),imindistance2(4)
	real distancesav(200000),xwall(100),ywall(100),zwall(100)


	idiff = 1
	open(11,file = 'f.vtk')

	do i=1,7
	read(11,*)cfn
	write(6,*)'ufk ',cfn,i
	enddo
	read(11,*)c6ufk, numpointsa

	write(6,*)'ufk ',c6ufk, numpointsa
	rnum = numpointsa
	rdiv = rnum/3
	idiv = numpoints/3
	rsub = rdiv-idiv
	extra = rsub*3
	iextra = nint(extra)
	close(11)

	open(11,file = 'f.vtk',form='unformatted')

	do i=1,200
	call fgetc(11,cnmr(i),istate)
	write(6,*)'ufk ',cnmr(i),inmr(i),i

	if(cnmr(i-4).eq.'I'.and.cnmr(i-3).eq.'N'.and.cnmr(i-2).eq.'T'.and.cnmr(i-1).eq.'S'.and.cnmr(i).eq.' ')then
	write(6,*)'found the end marker for ufk ',i
	go to 1197
	endif
	enddo  !i=1,200

 1197	continue

	stop
	end
