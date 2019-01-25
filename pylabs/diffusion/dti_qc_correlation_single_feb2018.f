c
c program to reformat bvec from fsl to bioimage suite
c
	real x(160),y(160),z(160)
	character*40 cfn,cfn2
	character*2 c2
	character*6 c6
	character*1 cnmr(1000),chead(348),cout(1000)
	integer*2 ihead(174),plotindex(160,4),plotbad(10000,4),plotgood(10000,4)
	integer*2 ibadv(160,2),igoodv(160,2),ib(100)
	real plotbada(10000,3,4),plotgooda(10000,3,4),rmax,nmr(250)
	real imagef(160,160,90,128), plot(160,10000,4),out(250)
	equivalence (out,cout)
	equivalence (nmr,cnmr)
	equivalence (ihead,chead)
	real rhead(87)
	equivalence (rhead,chead)
	common /dat1/ dnmr(200000),dnmr2(1000),dnmr3(1000)
	common /size/isize,isize2
	integer index(160),sort(10,200),incs(10)
	integer sortbval(10,200),incb(10)
	real bval(150)         
c
c extract the number bvecs from nhdr
c
	open(11,file = 'dtishort.hdr',form = 'unformatted')
	do i=1,348
	call fgetc(11,chead(i),istate)
	enddo
	close(11)
	do i=1,30
c	write(6,*),ihead(i),i
	enddo
	ixsize = ihead(22)
	iysize = ihead(23)
	izsize = ihead(24)
	nvecs = ihead(25)
	write(6,*)'ixsize, iysize izsize nvecs ',ixsize,iysize,izsize,nvecs
	open(11,file = 'dimensions.txt')
	write(11,*)ixsize,iysize,izsize,nvecs
	close(11)
	rpixx = abs(rhead(21))
	rpixy = abs(rhead(22))
	rpixz = abs(rhead(23))
c
c read in dti data
c
	open(11,file = 'dtishort.img',form = 'unformatted')
	do it = 1,nvecs
	do k=1,izsize
	do j=1,iysize
	do i=1,ixsize*4
	call fgetc(11,cnmr(i),istate)
	enddo
	do i=1,ixsize
	imagef(i,j,k,it) = nmr(i)
c	if(j.eq.60.and.k.eq.30)write(6,*)'imagef ',imagef(i,j,k,it),i,j,k,it
	enddo  !i
	enddo  !j
	enddo  !k
	enddo  !it
	close(11)
c
c read in alphalevel
	open(22,file='alphalevel.txt')
	read(22,*)alphalevel
	close(22)
c
c
c
	isort = 1
	incit = 1
	do it=1,nvecs
	do k=5,izsize-1
	suma = 0
	sumb = 0
	sumsquarea = 0
	sumsquareb = 0
	sumab = 0
	rsize = 0
	do j=1,iysize
	do i=1,ixsize
	if(imagef(i,j,k,it).gt.0.and.imagef(i,j,k+1,it).gt.0)then
	suma = suma + imagef(i,j,k,it)
	sumb = sumb + imagef(i,j,k+1,it)
	sumsquarea = sumsquarea + (imagef(i,j,k,it)**2)
	sumsquareb = sumsquareb + (imagef(i,j,k+1,it)**2)

	sumab = sumab + (imagef(i,j,k,it)*imagef(i,j,k+1,it))
	rsize =rsize +1
	endif
	enddo !i
	enddo !j
	rmeana = suma/rsize
	rmeanb = sumb/rsize

c	write(6,*)'suma sumb sumab ',suma,sumb,sumab
	rdenominator = (sumsquarea**0.5)*(sumsquareb**0.5)
c	write(6,*)'suma sumb sumab ',suma,sumb,sumab,rdenominator
c	rdenominator = (suma*sumb)
	if(rdenominator.gt.0)then
c	write(6,*)'suma sumb sumab ',suma,sumb,sumab
c	rdenominator = (sumsquarea**0.5)*(sumsquareb**0.5)
c	write(6,*)'suma sumb sumab ',suma,sumb,sumab,rdenominator
	plot(k,incit,isort) = sumab/rdenominator
c	write(6,*) 'plot(k,incit) ',plot(k,incit),k,incit
c	plot(k,it) = sumab/rdenominator
c	write(6,*) 'plot(k,it) ',plot(k,incit,1),k,it,incit
	endif
	
	enddo  !k
	plotindex(incit,isort) = it
	incit = incit+1
	enddo  !it
	isizeit = incit-1

c
	if(isort.eq.1)open(12,file ='plotqc1',form='unformatted')
	do it =1,nvecs
	do k=1,izsize-1
	out(k) = plot(k,it,isort)
	enddo
	do k=1,(izsize-1)*4
	call fputc(12,cout(k),istate)
	enddo  !k
	enddo  !it
	close(12)
c
c find outliers and flag bad volumes
c
c first find average and standevation across all volumes for a given slice
c
	ibad = 0
	igood = 0
	itotal = 0
	do k=1,izsize-1

	do it=1,nvecs
	dnmr(it) = plot(k,it,isort)
c	if(k.eq.37)write(6,*)'dnmr(it) ',dnmr(it),it
	enddo
	isize = nvecs
	call average(aver,stdev,stem)
c	write(6,*)'aver stdev ', aver,k,it
	do it=1,nvecs
	alphacheck = abs(dnmr(it) -aver)/stdev
c	if(k.ge.36.and.k.le.40)write(6,*)'alphacheck ',alphacheck,it,k
	if(alphacheck.gt.alphalevel)then
c	if(dnmr(it).lt.0.9)then
	write(6,*)'this is bad gradient ',alphacheck,k,it-1,ibad
	plotbada(ibad,1,isort) = k
	plotbada(ibad,2,isort) = it
	plotbada(ibad,3,isort) = alphacheck
	plotbad(ibad,isort)=plotindex(it,isort)
	ibad = ibad +1
	else
	plotgooda(igood,1,isort) = k
	plotgooda(igood,2,isort) = it-1
	plotgooda(igood,3,isort) = alphacheck

	plotgood(igood,isort)= plotindex(it,isort)
	igood = igood+1
	endif
	itotal = itotal+1

	enddo  !it
	enddo  !k
	open(11,file = 'qc_report.txt')
	open(21,file = 'bad_vols_index.txt')
	write(6,*)'qc dti report '
	write(6,*)'there are ',ibad,' bad slices '
	write(6,*)'out of a total of ',itotal, 'slices checked '
	write(6,*)'total ',nvecs,'dti gradient direction volumes checked '
	write(11,*)'qc dti report '
	write(11,*)'there are ',ibad,' bad slices '
	write(11,*)'out of a total of ',itotal, 'slices checked '
	write(11,*)'total ',nvecs,'dti gradient direction volumes checked sorted '


	ibadvolume = 1
	do i=1,ibad
	rmax = 0.0
	do ii=1,ibad
	rmax = max(plotbada(ii,3,isort),rmax)
	if(rmax.eq.plotbada(ii,3,isort))isavebad = ii
	enddo   ! ii part 1 find the worse slice and volume
c	write(6,*)'rmax isavebad ',rmax,isavebad,i
	if(rmax.ne.0)then
c change to 1000 or 2000 seris
	ibtmp = plotbad(isavebad,isort)
	write(11,*)'alphacheck slice vol ',plotbada(isavebad,3,isort),plotbada(isavebad,1,isort),ibtmp,isort
	write(6,*)'alphacheck slice vol ',plotbada(isavebad,3,isort),plotbada(isavebad,1,isort),ibtmp
c
c output plotbad one volume at a time
c

	do ii=1,ibad
	if(plotbad(isavebad,isort).eq.plotbad(ii,isort))then
	write(11,*)'bad slice volume',plotbada(ii,3,isort),plotbada(ii,1,isort),plotbada(ii,2,isort)
c	write(6,*)'bad slice ',plotbada(ii,3),plotbada(ii,1)
	plotbada(ii,3,isort) = 0   ! set to 0 so it doesnt get recounted
	endif
	enddo   !ii part 2 add all bad slices for that volume
	ibadv(ibadvolume,1) = plotbad(isavebad,isort)
	ibadv(ibadvolume,2) = plotbada(isavebad,2,isort)
	ibadvolume = ibadvolume+1

	endif  !rmax.ne 0
	
	enddo  !increment over all bad slices and volumes
	close(11)
	close(13)
	if(isort.eq.1)open(13,file ='plotbad1',form='unformatted')
	do it=1,ibadvolume
	do k=1,izsize-1
	out(k) = plot(k,ibadv(it,2),isort)
	enddo
	do k=1,(izsize-1)*4
	call fputc(13,cout(k),istate)
	enddo  !k
	enddo  !it
	close(13)

	if(isort.eq.1)open(13,file = 'badvolumes1',form = 'unformatted')
	do i=1,ibadvolume
	ib(i)=ibadv(i,1)
c	write(6,*)'bad out ',ib,i
	out(i) = ib(i)
	enddo
	do i=1,(ibadvolume)*4
	call fputc(13,cout(i),istate)
	enddo
	close(13)
	do i=1,ibadvolume
	imin = 10000
	do ii=1,ibadvolume
	imin = min(ib(ii),imin)
	if(imin.eq.ib(ii))iset = ii
	enddo  !ii
c	write(6,*)'reorder ',ib(iset),i
	ib(iset) = 10000
	enddo  ! reorder

c
c  now do the good volumes and plots
c

	igoodvolume = 1
	do it=1,nvecs
	iflag = 0  ! means no bad slices
	do ii=1,ibad-1
	if(it.eq.plotbada(ii,2,isort))iflag = 1
	enddo
	if(iflag.eq.0)then  ! found a good volume
	igoodv(igoodvolume,1) = plotindex(it,isort)
	igoodv(igoodvolume,2) = it
	write(21,*)it-1, '0'
	igoodvolume = igoodvolume+1
	endif  !found a good volume
	if(iflag.eq.1)write(21,*)it-1,'1'
	enddo

	if(isort.eq.1)open(13,file ='plotgood1',form='unformatted')
	do it=1,igoodvolume
	do k=1,izsize-1
	out(k) = plot(k,igoodv(it,2),isort)
	enddo
	do k=1,(izsize-1)*4
	call fputc(13,cout(k),istate)
	enddo  !k
	enddo  !it

	close(13)


	if(isort.eq.1)open(13,file = 'goodvolumes1',form = 'unformatted')
	do i=1,igoodvolume
	out(i) = igoodv(i,1)
	enddo
	do i=1,(igoodvolume)*4
	call fputc(13,cout(i),istate)
	enddo
	close(13)
c

	rgood = itotal-ibad
	rtotal = itotal
	write(6,*)'dti interlace correlation qc score is  ',(rgood/rtotal)*100
	write(6,*)'a perfect score would be 100% '

	if(isort.eq.1)open(11,file = 'dimensionsbad1.txt')

	write(11,*)ixsize,iysize,izsize,ibadvolume-1
	close(11)
	if(isort.eq.1)open(11,file = 'dimensionsgood1.txt')

	write(11,*)ixsize,iysize,izsize,igoodvolume-1
	close(11)


	write(6,*)'finished '
	stop
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

