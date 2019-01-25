c
c
	character*1 chead(348),cnmr(1024)
	integer*2 ihead(174)
	real nmr(256),imagef(256,256,256,4)
	real region(100)
	equivalence (chead,ihead)
	equivalence (cnmr,nmr)
	regiondivisions=10.0

	open(11,file ='afile.hdr',form='unformatted')
	do i=1,348
	call fgetc(11,chead(i),istate)
	enddo
	close(11)
	ixsize = ihead(22)
	iysize= ihead(23)
	izsize = ihead(24)
	itsize = ihead(25)
	write(6,*)'ixsize iysize izsize itsize ',ixsize,iysize,izsize,itsize
	open(11,file ='afile.img',form='unformatted')
	do it=1,itsize
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	imagef(i,j,k,it)=nmr(i)
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)
c
c find the minimum and maximum z with signal
c
	rmin = 10000.0
	rmax = 0.0
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(imagef(i,j,k,1).gt.0)then
	rk=k
	rmin = min(rmin,rk)
	rmax = max(rmax,rk)
	endif
	enddo !i
	enddo !j
	enddo !k
	write(6,*)'rmin rmax ',rmin,rmax
c
c now divide up the tract into 10 pieces
c
	diff = rmax -rmin
	diffpart = diff/regiondivisions
	iregsize = regiondivisions
	open(11,file = 'fa.txt')
	open(12,file = 'ad.txt')
	open(13,file = 'rd.txt')
	open(14,file = 'md.txt')
	do it=1,itsize
	do ireg=1,iregsize
	rpart = ireg
	regstart = rmin+(diffpart*(rpart-1))
	regend = rmin+(diffpart*(rpart))
	iregstart = regstart
	iregend = regend
	write(6,*)'starting and ending ',iregstart,iregend
	sum = 0
	rcount = 0
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(k.ge.iregstart.and.k.lt.iregend)then
	if(imagef(i,j,k,1).ne.0)then
	sum = sum+imagef(i,j,k,it)
	rcount = rcount+1
	endif
	endif
	enddo  !i
	enddo  !j
	enddo !k
	region(ireg) = sum/rcount
	enddo !ireg
	write(10+it,*)(region(ii),ii=1,iregsize)
	enddo  !it
	close(11)
	close(12)
	close(13)
	close(14)


	stop
	end
