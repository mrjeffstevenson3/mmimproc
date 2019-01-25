c
c this is software to test all of the network results for bbc for
c paired ttest
c
	character*40 cfn
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2

	open(11,file = 'networkvalues.txt')
	read(11,*)cfn
	do i=1,9
	read(11,*)dmnmr(i)
	read(11,*)dmnmr2(i)
c	write(6,*)dmnmr(i),dmnmr2(i)
	enddo
c	dmnmr(1) = 16
c	dmnmr(2) = 3
c	dmnmr(3) = 17
c	dmnmr(4) = 3
c	dmnmr(5) = 19
c	dmnmr(6) = 15
c	dmnmr(7) = 24
c	dmnmr(8) = 23
c	dmnmr(9) = 3
c	dmnmr(10) = 12	
c	dmnmr(11) = 32
c	dmnmr2(1) = 32
c	dmnmr2(2) =22
c	dmnmr2(3) = 23
c	dmnmr2(4) = 13
c	dmnmr2(5) = 20
c	dmnmr2(6) = 29
c	dmnmr2(7) = 11
c	dmnmr2(8) = 25
c	dmnmr2(9) = 13
c	dmnmr2(10) = 20	
c	dmnmr2(11) = 30
c
	close(11)
	isize1 = 11
	isize2 = 11
	call paired(t)
	write(6,*)'paired t result ',t
	if(t.gt.2.0)write(6,*)'we have a winner!'
	if(t.lt.-2.0)write(6,*)'we have a negative winner!'
	stop
	end
	

c
	subroutine paired(t)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
	real diff(1000), diffsq(1000)
C	CALCULATER AVERAGE AND STANDARD DEVIATION FOR INPUT
c	and student t
c
	real incv(2)
	dimension sdv(2),averv(2)
C
	sumdiff = 0
	sumsq = 0
	do i=1,isize1
	diff(i) = dmnmr(i)-dmnmr2(i)
	diffsq(i) = diff(i)*diff(i)
	sumdiff = sumdiff+diff(i)
	sumsq = sumsq+diffsq(i)
c	write(6,*)dmnmr(i),dmnmr2(i),diff(i),i
	enddo
	rsize = isize1
	rnumer = sumdiff/rsize
	rdenom = sqrt((sumsq - ((sumdiff*sumdiff)/rsize))/(rsize*(rsize-1)))
c	write(6,*)'rnumer rdenom ',rnumer, rdenom, sumdiff,sumsq
	t = rnumer/rdenom
	return
	end
	subroutine average2(aver,stdev,stem)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
c
c
c
c	calculate the average
c
	sum=0
	risize1 = isize1
	do 40 i=1,isize1
c	write(6,*)'dmnmr in aver ',dmnmr(i),i
 40	sum=dmnmr(i)+sum
c
	aver=sum/risize1
c	write(6,*)'average and size = ',aver,isize1
c
c	calculate the standart deviation
c
	sum=0
	do 50 i=1,isize1
 50	sum=sum + ((dmnmr(i)-aver)**2)
c
	risize1 = isize1
	stdev=sum/(risize1-1)
	stdev = sqrt(stdev)
	stem = stdev/sqrt(risize1)
c	write(6,*)'standard deviation = ',stdev
c	write(6,*)'standard error in the mean = ',stem
c
	return
	end

