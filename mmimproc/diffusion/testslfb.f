c
	character*1 chead(348),cnmr(1024)
	integer*2 ihead(174)
	real nmr(256),imagef(256,256,256,72)
	real region(100)
	equivalence (chead,ihead)
	equivalence (cnmr,nmr)
	integer iy(10),iz(10)
	real rfa(10)
	iy(1) = 71
	iz(1) = 64
	iy(2) = 72
	iz(2) = 69
	iy(3) = 68
	iz(3) = 72
	iy(4) = 63
	iz(4) = 71
	iy(5) = 59
	iz(5) = 70
	iy(6) = 49
	iz(6) = 64


	open(11,file ='leftslftest.hdr',form='unformatted')
	open(12,file ='newcommonj.hdr',form='unformatted')
	do i=1,348
	call fgetc(11,chead(i),istate)
	enddo
	close(11)
	ixsize = ihead(22)
	iysize= ihead(23)
	izsize = ihead(24)
	itsize = ihead(25)
	do i=1,30
	write(6,*)'ihead ',ihead(i),i
	enddo
	write(6,*)'ixsize iysize izsize itsize ',ixsize,iysize,izsize,itsize

	ihead(22) = iysize
	ihead(23) = izsize
	ihead(24) = 16
	ihead(25) = 1
	do i=1,348
	call fputc(12,chead(i),istate)
	enddo
	close(12)

	open(11,file ='leftslftest.img',form='unformatted')
	open(12,file ='newcommonj.img',form='unformatted')
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

	do it=1,itsize,4
	do k=1,izsize
	write(6,*)'k ',k
	do j=1,iysize
	sum = 0
	do i=1,ixsize
	sum = sum + imagef(i,j,k,it)
	enddo !
	nmr(j) = sum
	enddo  !i
	do j=1,iysize*4
	call fputc(12,cnmr(j),istate)
	enddo  !j
	enddo  !k
	enddo !it
	close(12)	
c
c now extract out values for each point along the arcuate
c
	open(11,file = 'fa_slf.txt')
	do it=1,itsize,4
	do ip=1,6
	sum = 0
	size = 0	
	do k=iz(ip)-2,iz(ip)+2
	do j=iy(ip)-2,iy(ip)+2
	do i=1,ixsize
	if(imagef(i,j,k,it).gt.0)then
	sum = sum + imagef(i,j,k,it)
	size = size +1
	endif
	enddo !i
	enddo !j
	enddo !k
	rfa(ip) = sum/size
	enddo  !ip
	write(11,*)(rfa(ip),ip =1,6)
	enddo  !it
	close(11)
c
	open(11,file = 'ad_slf.txt')
	do it=2,itsize,4
	do ip=1,6
	sum = 0
	size = 0	
	do k=iz(ip)-2,iz(ip)+2
	do j=iy(ip)-2,iy(ip)+2
	do i=1,ixsize
	if(imagef(i,j,k,it).gt.0)then
	sum = sum + imagef(i,j,k,it)
	size = size +1
	endif
	enddo !i
	enddo !j
	enddo !k
	rfa(ip) = sum/size
	enddo  !ip
	write(11,*)(rfa(ip),ip =1,6)
	enddo  !it
	close(11)
c
	open(11,file = 'rd_slf.txt')
	do it=3,itsize,4
	do ip=1,6
	sum = 0
	size = 0	
	do k=iz(ip)-2,iz(ip)+2
	do j=iy(ip)-2,iy(ip)+2
	do i=1,ixsize
	if(imagef(i,j,k,it).gt.0)then
	sum = sum + imagef(i,j,k,it)
	size = size +1
	endif
	enddo !i
	enddo !j
	enddo !k
	rfa(ip) = sum/size
	enddo  !ip
	write(11,*)(rfa(ip),ip =1,6)
	enddo  !it
	close(11)
c
	open(11,file = 'md_slf.txt')
	do it=4,itsize,4
	do ip=1,6
	sum = 0
	size = 0	
	do k=iz(ip)-2,iz(ip)+2
	do j=iy(ip)-2,iy(ip)+2
	do i=1,ixsize
	if(imagef(i,j,k,it).gt.0)then
	sum = sum + imagef(i,j,k,it)
	size = size +1
	endif
	enddo !i
	enddo !j
	enddo !k
	rfa(ip) = sum/size
	enddo  !ip
	write(11,*)(rfa(ip),ip=1,6)
	enddo  !it
	close(11)


	
	write(6,*)'finished '
	stop
	end

	
	
	
