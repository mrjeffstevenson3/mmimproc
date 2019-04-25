c
c this is software to test all of the network results for bbc for
c paired ttest
c
	character*40 cfn
	real behav(1000)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2

	open(11,file = 'networkvalues.txt')
	open(21,file = 'behav.txt')
	open(22,file = 'behav1.txt')
	open(12,file = 'brain10.txt')
	open(13,file = 'brain11.txt')
	read(21,*)cfn
	read(21,*)cfn
	read(11,*)cfn
	do i=1,9
	read(21,*)behav(i)
	write(22,*)behav(i)
	read(11,*)dmnmr(i)
	write(12,*)dmnmr(i)
	read(11,*)dmnmr2(i)
	write(13,*)dmnmr2(i)
c	write(6,*)dmnmr(i),dmnmr2(i)
	enddo
c
	close(11)
	close(12)
	close(13)
	close(21)
	close(22)
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

