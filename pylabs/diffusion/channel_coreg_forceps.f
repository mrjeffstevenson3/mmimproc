c
c
	character*1 chead(348),cnmr(1024)
	integer*2 ihead(174)
	real nmr(256),imagef(256,256,256,4)
	real region(100)
	equivalence (chead,ihead)
	equivalence (cnmr,nmr)
	regiondivisions=5.0

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
c find the minimum and maximum in x and y with signal
c
	rminx = 10000.0
	rminy = 10000.0
	rmaxx = 0.0
	rmaxy = 0.0
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(imagef(i,j,k,1).gt.0)then
	rx=i
	rminx = min(rminx,rx)
	rmaxx = max(rmaxx,rx)
	ry=j
	rminy = min(rminy,ry)
	rmaxy = max(rmaxy,ry)
	endif
	enddo !i
	enddo !j
	enddo !k
	write(6,*)'rminx rmaxx rminy rmaxy ',rminx,rmaxx,rminy,rmaxy
c
c now divide up the tract into pieces
c
	diffx = rmaxx +rminx
	rmiddlex = diffx/2.0
	imiddlex = nint(rmiddlex)
	diff = rmaxy -rminy
	diffpart = diff/regiondivisions
	iregsize = regiondivisions
	open(11,file = 'fa.txt')
	open(12,file = 'ad.txt')
	open(13,file = 'rd.txt')
	open(14,file = 'md.txt')
	do it=1,itsize
	do ireg=1,iregsize
	rpart = ireg
	regstart = rminy+(diffpart*(rpart-1))
	regend = rminy+(diffpart*(rpart))
	iregstart = regstart
	iregend = regend
	write(6,*)'starting and ending ',iregstart,iregend
	sum1 = 0
	sum2 = 0
	rcount1 = 0
	rcount2 = 0
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize
	if(j.ge.iregstart.and.j.lt.iregend.and.i.ge.imiddlex)then
	if(imagef(i,j,k,1).ne.0)then
	sum1 = sum1+imagef(i,j,k,it)
	rcount1 = rcount1+1
	endif
	endif
	if(j.ge.iregstart.and.j.lt.iregend.and.i.lt.imiddlex)then
	if(imagef(i,j,k,1).ne.0)then
	sum2 = sum2+imagef(i,j,k,it)
	rcount2 = rcount2+1
	endif
	endif

	enddo  !i
	enddo  !j
	enddo !k
	region(ireg) = sum1/rcount1
	region(ireg+5)=sum2/rcount2
	enddo !ireg
	write(10+it,*)(region(ii),ii=1,iregsize*2)
	enddo  !it
	close(11)
	close(12)
	close(13)
	close(14)


	stop
	end
