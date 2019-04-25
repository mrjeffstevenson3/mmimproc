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
	close(11)
	isize1 = 9
	isize2 = 9
	call ttest(t)
	write(6,*)'ttest result ',t
	if(t.gt.2.0)write(6,*)'we have a winner!'
	if(t.lt.-2.0)write(6,*)'we have a negative winner!'
	stop
	end
	

c
	subroutine ttest(t)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
C	CALCULATER AVERAGE AND STANDARD DEVIATION FOR INPUT
c	and student t
c
	real incv(2)
	dimension sdv(2),averv(2)
C
	isize1sav = isize1
	isize2sav = isize2
	df = isize1+isize2-2
c	write(6,*)'degrees of freedom ',df
	incv(1) = isize1
	incv(2) = isize2
	call average2(averv(1),sdv(1),stem)
c	write(6,*)'aver1 sdv, stem ',averv(1),sdv(1),stem,incv(1)
	isize1=isize2
	do i=1,isize1
	dmnmr(i)=dmnmr2(i)
	enddo
	call average2(averv(2),sdv(2),stem)
c	write(6,*)'aver2 sdv, stem ',averv(2),sdv(2),stem,incv(2)
	sdv(1)=sdv(1)**2
	sdv(2)=sdv(2)**2
	ssqu=( incv(1) -1 )*sdv(1) + (incv(2) - 1) * sdv(2)
	ssqu= ssqu/(incv(1) + incv(2) -2)
	t = averv(1) - averv(2)
	denom = sqrt( (ssqu/incv(1)) + (ssqu/incv(2)) )
	t =( t/denom)
c	write(6,*)'ttest t value = ',t
	isize1 = isize1sav
	isize2 = isize2sav
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

