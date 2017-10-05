c
c this is software to test all of the network results for bbc for
c paired ttest
c
	character*40 cfn,cfnlist(100),cfnlist2(100),cheader(100),ch,cheader2(100)
	character*40 cout,csubjects(100)
	character*20 clabels(100),cbehav(100),cbrain(100)
	character*90 cfnall_nbwr,cfnbehav
	common /dat1/ dmnmr(10000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
	integer scores(100,100)
	real dnmr(100,100),behav1(10000),dout(100,100)
	real tvalue(100)
	character*1 c1
	character*3 csubg,csubb,csubsav(100)
	REAL X,XNU,PROB1,PROB2,aver(2),mean1(100),mean2(100)
	real dof(100),sdv(2),stdev1(100),stdev2(100)
  	INTEGER NU, ERROR

	open(11,file ='numcol1.txt')
	read(11,*)numcol1
	close(11)
	open(11,file ='numrow1.txt')
	read(11,*)numrow1
	close(11)
	open(11,file ='numcol2.txt')
	read(11,*)numcol2
	close(11)
	open(11,file ='numrow2.txt')
	read(11,*)numrow2
	close(11)
	open(11,file = 'chosen_metabolite.txt')
	read(11,*)ichosen_metabolite
	close(11)
	open(11,file ='all_nbwr.txt')
	read(11,11)cfnall_nbwr
 11	format(a90)
	write(6,*)'cfnall_nbwr ',cfnall_nbwr
	close(11)
	open(11,file ='gaba_scores.txt')
	read(11,11)cfnbehav
	write(6,*)'cfnbehav ',cfnbehav
	close(11)


	open(11,file = cfnall_nbwr)
	read(11,*)cfn
	read(11,*)cheader(1),(cfnlist(ii),ii=1,numcol1)
	write(6,*)cfnlist(1),cfnlist(numcol1)
	do irow =2,numrow1-1
	read(11,*)cheader(irow),(dnmr(ii,irow),ii=1,numcol1)
	write(6,*)cheader(irow),dnmr(1,irow),dnmr(numcol1,irow),irow
	enddo  !irow1
	close(11)
	open(11,file = cfnbehav)
	read(11,*)cheader2(1),(cfnlist2(ii),ii=1,numcol2)
	write(6,*)cfnlist2(1),cfnlist2(numcol2)
	do irow =2,numrow2
	read(11,*)cheader2(irow),(scores(ii,irow),ii=1,numcol2)
	write(6,*)cheader2(irow),scores(1,irow),scores(numcol2,irow),irow
	enddo  !irow1
	
	close(11)

c

C
	do ii=ichosen_metabolite,ichosen_metabolite
	do ibeh = 1,1
	index1 = 1
	do irow = 2,numrow1-1
	cfn = cheader(irow)
c	write(6,*)cfn
	csubg = cfn(9:11)
c	write(6,*)csubg
	do irow2 = 2,numrow2-1
	cfn = cheader2(irow2)
	csubb =cfn(6:8)

	if(csubb.eq.csubg)then
c	write(6,*)'we have found the one!'
c		write(6,*)csubb
	dmnmr(index1) = dnmr(ii,irow)
	behav1(index1) = scores(ibeh,irow2)
	csubsav(index1) = csubb
	index1 = index1+1
	endif

	enddo
	enddo
	itsize = index1-1
	open(12,file='output_correlation.txt')
	open(13,file='output_correlation_stats.txt')
	do i=1,itsize
c	write(6,*)'test corr input ',dmnmr(i),behav1(i),i
	write(12,*)dmnmr(i),behav1(i),csubsav(i)
	enddo
	call correlation(dmnmr,behav1,rcorr,itsize)
	if(rcorr.gt.0.6.or.rcorr.lt.-0.6)write(6,*)'rcorr ',rcorr, ii,ibeh,itsize,cfnlist(ii),cfnlist2(ibeh)
	rsize = itsize
	rdenom = sqrt((1-(rcorr*rcorr))/(rsize-2))
	rt = rcorr/rdenom
	write(6,*)'this is the tvalue converted from correlation rvalue ',rt
	write(13,*)rt
	tt=rt
	degreesof = rsize
	PROB2=STUDNT(tt,degreesof,ERROR)
  	write(6,*)' tvalue=', tt
  	write(6,*)' PROB2=', PROB2*2.0
  	write(13,*)PROB2*2.0
  	write(6,*)' ERROR=', ERROR


	enddo !ibehav
	enddo !ii
c
	close(12)
	close(13)
	stop
	end
	

c
	subroutine ttest(t)
	common /dat1/ dmnmr(10000),dmnmr2(1000),dmnmr3(1000)
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
	common /dat1/ dmnmr(10000),dmnmr2(1000),dmnmr3(1000)
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
	common /dat1/ dmnmr(10000),dmnmr2(1000),dmnmr3(1000)
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
c
	REAL FUNCTION STUDNT (T, DOFF, IFAULT)
! ----------------------------------------------------------------
!  ALGORITHM AS 27  APPL. STATIST. VOL.19, NO.1
!
!  Calculate the upper tail area under Student's t-distribution
!
!  Translated from Algol by Alan Miller
! ----------------------------------------------------------------
	INTEGER IFAULT
	REAL T, DOFF
!  Local variables

	REAL V, X, TT, TWO, FOUR, ONE, ZERO, HALF
	REAL A1, A2, A3, A4, A5, B1, B2, C1, C2, C3, C4, C5, D1, D2, E1, E2, E3, E4, E5, F1, F2, G1, G2, G3, G4, G5, H1, H2, I1, I2, I3, I4, I5, J1, J2
	LOGICAL POS
	DATA TWO /2.0/, FOUR /4.0/, ONE /1.0/, ZERO /0.0/, HALF /0.5/
	DATA A1, A2, A3, A4, A5 /0.09979441, -0.581821, 1.390993,-1.222452, 2.151185/, B1, B2 /5.537409, 11.42343/
	DATA C1, C2, C3, C4, C5 /0.04431742, -0.2206018, -0.03317253,5.679969, -12.96519/, D1, D2 /5.166733, 13.49862/
	DATA E1, E2, E3, E4, E5 /0.009694901, -0.1408854, 1.88993,-12.75532, 25.77532/, F1, F2 /4.233736, 14.3963/
	DATA G1, G2, G3, G4, G5 /-9.187228E-5, 0.03789901, -1.280346,9.249528, -19.08115/, H1, H2 /2.777816, 16.46132/
	DATA I1, I2, I3, I4, I5 /5.79602E-4, -0.02763334, 0.4517029,-2.657697, 5.127212/, J1, J2 /0.5657187, 21.83269/

!  Check that number of degrees of freedom > 4.

	IF (DOFF .LT. TWO) THEN
	 IFAULT = 1
	 STUDNT = - ONE
	 RETURN
	END IF

	IF (DOFF .LE. FOUR) THEN
	 IFAULT = DOFF
	ELSE
	 IFAULT = 0
	END IF

!  Evaluate series.

	V = ONE / DOFF
	POS = (T .GE. ZERO)
	TT = ABS(T)
	X = HALF * (ONE + TT * (((A1 + V * (A2 + V * (A3 + V * (A4 + V * A5)))) / (ONE - V * (B1 - V * B2))) + TT * (((C1 + V * (C2 + V * (C3 + V * (C4 + V * C5)))) /  (ONE - V * (D1 - V * D2))) +TT * (((E1 + V * (E2 + V * (E3 + V * (E4 + V * E5)))) / (ONE - V * (F1 - V * F2))) +TT * (((G1 + V * (G2 + V * (G3 + V * (G4 + V * G5)))) /  (ONE - V * (H1 - V * H2))) + TT * ((I1 + V * (I2 + V * (I3 + V * (I4 + V * I5)))) /(ONE - V * (J1 - V * J2))) ))))) ** (-8)
	IF (POS) THEN
	 STUDNT = X
	ELSE
	 STUDNT = ONE - X
	END IF

	RETURN
	END

!end of file Student.f90

