c
c this is software to test all of the network results for bbc for
c paired ttest
c
	character*40 cfn,cfnlist(100),cheader(100),ch
	character*40 cout,csubjects(100)
	character*20 clabels(100),c20
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
	real dnmr(100,100),behav1(10000),dout(100,100)
	real tvalue(100)
	character*1 c1
	character*2 chside(100),chsidechosen(100)
	character*3 c3(100),c3unmed(100),c3control(100)
	numcol = 17
	numrows = 38
	open(11,file = 'for_todd_SPMcorrected_metabolites.csv')
	read(11,*)clabels(1),(cfnlist(ii),ii=1,numcol-1)
	write(6,*)cfnlist(1),cfnlist(numcol)
	do irow =1,numrows-1
	read(11,*)cheader(irow),(dnmr(ii,irow),ii=1,numcol-1)
	write(6,*)cheader(irow),chside(irow),dnmr(1,irow),dnmr(numcol-2,irow),irow
	enddo  !irow

	close(11)
c
c  nbwr med group
c
	c3(1) = '007'
	c3(2) = '317'
	c3(3) = '081'
	c3(4) = '215'
	do imet = 1,16
	do igr = 1,4
	do irow = 1,numrows-1
	c20 = cheader(irow)
	if(c20(9:11).eq.c3(igr))then
c	write(6,*)'c20 ',c20(9:11)
	dmnmr(igr) = dnmr(imet,irow)
	endif

	enddo
	enddo
	isize1 = 4
	c3unmed(1) = '017'
	c3unmed(2) = '038'
	c3unmed(3) = '088'
	c3unmed(4) = '107'
	c3unmed(5) = '110'
	c3unmed(6) = '132'
	c3unmed(7) = '135'
	c3unmed(8) = '136'
	c3unmed(9) = '144'
	c3unmed(10) = '226'
	c3unmed(11) = '301'
	c3unmed(12) = '307'
	c3unmed(13) = '309'
	do igr = 1,13
	do irow = 1,numrows-1
	c20 = cheader(irow)
	if(c20(9:11).eq.c3unmed(igr))then
c	write(6,*)'c20 ',c20(9:11)
	dmnmr2(igr) = dnmr(imet,irow)
	endif

	enddo
	enddo
	isize2 = 13

	c3control(1) = '401'
	c3control(2) = '404'
	c3control(3) = '405'
	c3control(4) = '407'
	c3control(5) = '409'
	c3control(6) = '421'
	c3control(7) = '426'
	c3control(8) = '427'
	c3control(9) = '428'
	c3control(10) = '431'
	c3control(11) = '432'
	c3control(12) = '437'
	c3control(13) = '440'
	c3control(14) = '442'
	c3control(15) = '443'
	c3control(16) = '444'
	c3control(17) = '447'
	c3control(18) = '448'
	c3control(19) = '449'
	c3control(20) = '451'

	do igr = 1,20
	do irow = 1,numrows-1
	c20 = cheader(irow)
	if(c20(9:11).eq.c3control(igr))then
c	write(6,*)'c20 ',c20(9:11)
	dmnmr3(igr) = dnmr(imet,irow)
	endif

	enddo
	enddo
	isize3 = 20


	write(6,*)'isize1 isize2 ',isize1,isize2
	call ttest_unequalv(t)
	write(6,*)t,imet,cfnlist(imet)
	enddo
	
	


c
c output new files
c

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
	write(6,*)'aver1 sdv, stem ',averv(1),sdv(1),stem,incv(1)
	isize1=isize2
	do i=1,isize1
	dmnmr(i)=dmnmr2(i)
	enddo
	call average2(averv(2),sdv(2),stem)
	write(6,*)'aver2 sdv, stem ',averv(2),sdv(2),stem,incv(2)
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

	subroutine ttest_unequalv(t)
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
	incv(1) = isize1-1
	incv(2) = isize2-1
	call average2(averv(1),sdv(1),stem)
	sum1 = 0
	do i=1,isize1
	sum1 = sum1 + ((dmnmr(i)-averv(1))*(dmnmr(i)-averv(1)))
	enddo

	s1s2 = sum1/incv(1)
	
	write(6,*)'aver1 sdv, stem ',averv(1),sdv(1),stem,incv(1)
	isize1=isize2
	do i=1,isize1
	dmnmr(i)=dmnmr2(i)
	enddo
	call average2(averv(2),sdv(2),stem)
	sum1 = 0
	do i=1,isize2
	sum1 = sum1 + ((dmnmr(i)-averv(2))*(dmnmr(i)-averv(2)))
	enddo
	s2s2 = sum1/incv(2)

	write(6,*)'aver2 sdv, stem ',averv(2),sdv(2),stem,incv(2),s1s2,s2s2
	t = averv(1) - averv(2)
c	denom = sqrt( (s1s2/incv(1) )+ s2s2/incv(2) )
	denom = sqrt( (s1s2/(incv(1)+1) )+ (s2s2/(incv(2)+1)) )
	t =( t/denom)
c	write(6,*)'ttest t value = ',t
	isize1 = isize1sav
	isize2 = isize2sav
c
c calculate the degrees of freedom for unequal
c variances
	rnumerator = (s1s2/(incv(1)+1))+(s2s2/(incv(2)+1))
	rnumerator2 = rnumerator*rnumerator
	denominator1 = (s1s2/(incv(1)+1))*(s1s2/(incv(1)+1))
	denominator2 = (s2s2/(incv(2)+1))*(s2s2/(incv(2)+1))
	denominator3 = (denominator1/incv(1))+ (denominator2/incv(2))
	degreesof = rnumerator2/denominator3
	write(6,*)'degrees of freedom for unequal variances ',degreesof

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
c correlation
c
	subroutine correlation(dnmr,behav1,rcorr,itsize)
	real dnmr(10000),behav1(10000)
	suma = 0
	sumb = 0
	sumsquarea = 0
	sumsquareb = 0
	sumab = 0
	rsize = 0
	do it=1,itsize
	suma = suma + dnmr(it)
	sumb = sumb + behav1(it)
	sumsquarea = sumsquarea + (dnmr(it)**2)
	sumsquareb = sumsquareb + (behav1(it)**2)

	sumab = sumab + (dnmr(it)*behav1(it))
	rsize =rsize +1
	enddo !it

	rmeana = suma/rsize
	rmeanb = sumb/rsize
c	write(6,*)'rmeana rmeanb ',rmeana,rmeanb

	sumasquare = 0
	sumbsquare = 0
	sumab = 0
	do i=1,itsize
	sumasquare = sumasquare+((dnmr(i)-rmeana)**2)
	sumbsquare = sumbsquare+((behav1(i)-rmeanb)**2)
	sumab = sumab + ((dnmr(i)-rmeana)*(behav1(i)-rmeanb))
	enddo
	denoma = (sumasquare**0.5)
	denomb = (sumbsquare**0.5)
	rdenominator = denoma*denomb
	if(rdenominator.ne.0)then
	rcorr = sumab/(denoma*denomb)	
	else
	rcorr = 0
	endif
	return
	end
