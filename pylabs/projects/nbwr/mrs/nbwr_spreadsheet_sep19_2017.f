c
c this is software to test all of the network results for bbc for
c paired ttest
c
	character*40 cfn,cfnlist(100),cheader(100),ch
	character*40 cout,csubjects(100)
	character*35 clabels(100)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
	real dnmr(100,100),behav1(10000),dout(100,100)
	real tvalue(100),pvalue(100)
	character*1 c1
	REAL X,XNU,PROB1,PROB2,aver(2),mean1(100),mean2(100)
	real dof(100),sdv(2),stdev1(100),stdev2(100)
  	INTEGER NU, ERROR

	
	open(11,file ='numcol.txt')
	read(11,*)numcol
	close(11)
	open(11,file ='numrow.txt')
	read(11,*)numrow
	close(11)

	open(11,file = 'all_nbwr_mrs_uncorr_fits.csv')
	read(11,*)cheader(1),(cfnlist(ii),ii=1,numcol)
	write(6,*)cfnlist(1),cfnlist(numcol)
	do irow =2,numrow
	read(11,*)cheader(irow),(dnmr(ii,irow),ii=1,numcol)
	write(6,*)cheader(irow),dnmr(1,irow),dnmr(numcol,irow),irow
	enddo  !irow

	close(11)
c
c first find the row with the csf left

	do imetab=2,numrow
	ch=cheader(imetab)
	if(ch.eq.'left-percCSF')irowcorrect = imetab
	enddo
c
	clabels(1) = 'subjectid'
	ileft = 1
	do imetab=2,numrow
	ch=cheader(imetab)
	if(ch(1:1).eq.'l'.and.ch(6:6).ne.'p')then
	ileft = ileft+1
	cout(1:12)='csfcorrected'
	cout(13:13)='_'
	cout(14:35)=ch(1:20)
	clabels(ileft) = cout
	write(6,*)'clabels(ileft) ',clabels(ileft)


	isize1 = 0
	isize2 = 0
	do isub=1,numcol


	correctionfactor = 1/(1- dnmr(isub,irowcorrect))

	cfn=cfnlist(isub)
	write(6,*)cfn(9:9),ifil
c	read(11,*)c1,(dnmr(ifil,ii),ii=1,14)
c	read(11,*)(dnmr(ifil,ii),ii=1,1)
c	write(6,*)'dnmr 10',dnmr(ifil,1)
	if(cfn(9:9).ne.'4')then
	isize1 = isize1+1
	dmnmr(isize1) = dnmr(isub,imetab)*correctionfactor
c	dmnmr(isize1) = dnmr(isub,imetab)
	endif
	if(cfn(9:9).eq.'4')then
	isize2 = isize2+1
	dmnmr2(isize2) = dnmr(isub,imetab)*correctionfactor
	endif
	enddo !isub
	do i=1,isize1
	dout(i,ileft)=dmnmr(i)
	write(6,*)dout(i,ileft),i,ileft,cout
	enddo
	do i=1,isize2
	dout(i+isize1,ileft)=dmnmr2(i)
	write(6,*)dout(i+isize1,ileft),i,ileft
	enddo

	write(6,*)'isize1 isize2 ',isize1,isize2
	call ttest_unequalv(t,degreesof,aver,sdv)
	tvalue(ileft)=t
	mean1(ileft) =aver(1)
	mean2(ileft) =aver(2)
	stdev1(ileft) = sdv(1)
	stdev2(ileft) = sdv(2)
	dof(ileft) = degreesof
	PROB2=STUDNT(t,degreesof,ERROR)
  	write(6,*)' tvalue=', t
  	write(6,*)' PROB2=', PROB2*2.0
	pvalue(ileft)=prob2*2.0

	write(6,*)t,imetab
	endif !for left
	enddo  !imetab
c
c add a column for the glu/gaba ratio on the left
c
	ileft = ileft+1
	write(6,*)'ratio test ',clabels(2),clabels(7)
	cout(1:12)='csfcorrected'
	cout(13:13)='_'
	cout(14:35)='glu_gaba_ratio_left'
	clabels(ileft) = cout

	do i=1,isize1
	dout(i,ileft)=dout(i,7)/dout(i,2)
	dmnmr(i) = dout(i,ileft)
	enddo
	do i=1,isize2
	dout(i+isize1,ileft)=dout(i+isize1,7)/dout(i+isize1,2)
	dmnmr2(i) = dout(i+isize1,ileft)
	enddo
	call ttest_unequalv(t,degreesof,aver,sdv)
	tvalue(ileft)=t
	mean1(ileft) =aver(1)
	mean2(ileft) =aver(2)
	stdev1(ileft) = sdv(1)
	stdev2(ileft) = sdv(2)
	dof(ileft) = degreesof
	PROB2=STUDNT(t,degreesof,ERROR)
  	write(6,*)' tvalue=', t
  	write(6,*)' PROB2=', PROB2*2.0
	pvalue(ileft)=prob2*2.0
	
c
c first find the row with the csf right

	do imetab=2,numrow
	ch=cheader(imetab)
	if(ch.eq.'right-percCSF')irowcorrect = imetab
	enddo
c
	clabels(1) = 'subjectid'
	iright = ileft
	do imetab=2,numrow
	ch=cheader(imetab)
	if(ch(1:1).eq.'r'.and.ch(7:7).ne.'p')then
	iright = iright+1
	cout(1:12)='csfcorrected'
	cout(13:13)='_'
	cout(14:35)=ch(1:20)
	clabels(iright) = cout
	write(6,*)'clabels(iright) ',clabels(iright),iright


	isize1 = 0
	isize2 = 0
	do isub=1,numcol


	correctionfactor = 1/(1- dnmr(isub,irowcorrect))

	cfn=cfnlist(isub)
	write(6,*)cfn(9:9),ifil
c	read(11,*)c1,(dnmr(ifil,ii),ii=1,14)
c	read(11,*)(dnmr(ifil,ii),ii=1,1)
c	write(6,*)'dnmr 10',dnmr(ifil,1)
	if(cfn(9:9).ne.'4')then
	isize1 = isize1+1
	dmnmr(isize1) = dnmr(isub,imetab)*correctionfactor
c	dmnmr(isize1) = dnmr(isub,imetab)
	endif
	if(cfn(9:9).eq.'4')then
	isize2 = isize2+1
	dmnmr2(isize2) = dnmr(isub,imetab)*correctionfactor
	endif
	enddo !isub
	do i=1,isize1
	dout(i,iright)=dmnmr(i)
	write(6,*)dout(i,iright),i,iright,cout
	enddo
	do i=1,isize2
	dout(i+isize1,iright)=dmnmr2(i)
	write(6,*)dout(i+isize1,iright),i,iright
	enddo

	write(6,*)'isize1 isize2 ',isize1,isize2
c to test the equation we use a verified example of data
c
c	dmnmr(1) = 134
c	dmnmr(2) = 146
c	dmnmr(3) = 104
c	dmnmr(4) = 119
c	dmnmr(5) = 124
c	dmnmr(6) = 161
c	dmnmr(7) = 107
c	dmnmr(8) = 83
c	dmnmr(9) = 113
c	dmnmr(10)= 129
c	dmnmr(11) = 97
c	dmnmr(12) = 123
c	dmnmr2(1) = 70
c	dmnmr2(2) = 118
c	dmnmr2(3) = 101
c	dmnmr2(4) = 85
c	dmnmr2(5) = 107
c	dmnmr2(6) = 132
c	dmnmr2(7) = 94
cHigh protein 	Low protein
c134 	70
c146 	118
c104 	101
c119 	85
c124 	107
c161 	132
c107 	94
c83 	 
c113 	 
c129 	 
c97 	 
c123 	 

c	isize1 = 12
c	isize2 = 7
	call ttest_unequalv(t,degreesof,aver,sdv)
	mean1(iright) =aver(1)
	mean2(iright) =aver(2)
	stdev1(iright) = sdv(1)
	stdev2(iright) = sdv(2)

	dof(iright) = degreesof
	PROB2=STUDNT(t,degreesof,ERROR)
  	write(6,*)' tvalue=', t
  	write(6,*)' PROB2=', PROB2*2.0
  	write(6,*)' ERROR=', ERROR
	tvalue(iright)=t
	pvalue(iright)=prob2*2.0
	write(6,*)t,imetab
	endif !for left
	enddo  !imetab
c add a column for the glu/gaba ratio on the left
c
	iright = iright+1
	write(6,*)'ratio test ',clabels(9),clabels(14)
	cout(1:12)='csfcorrected'
	cout(13:13)='_'
	cout(14:35)='glu_gaba_ratio_right'
	clabels(iright) = cout

	do i=1,isize1
	dout(i,iright)=dout(i,14)/dout(i,9)
	dmnmr(i) = dout(i,iright)
	enddo
	do i=1,isize2
	dout(i+isize1,iright)=dout(i+isize1,14)/dout(i+isize1,9)
	dmnmr2(i) = dout(i+isize1,iright)
	enddo
	call ttest_unequalv(t,degreesof,aver,sdv)
	mean1(iright) =aver(1)
	mean2(iright) =aver(2)
	stdev1(iright) = sdv(1)
	stdev2(iright) = sdv(2)

	dof(iright) = degreesof
	PROB2=STUDNT(t,degreesof,ERROR)
  	write(6,*)' tvalue=', t
  	write(6,*)' PROB2=', PROB2*2.0
  	write(6,*)' ERROR=', ERROR
	tvalue(iright)=t
	pvalue(iright)=prob2*2.0
	write(6,*)t,imetab

c
c output new files
c
	write(6,*)'ileft ',ileft,iright
	open(11,file = 'csfcorrected.csv')
	write(11,12)clabels(1),(',',clabels(ii),ii=2,iright)
 12	format(10a,100(1a,10a))
	do i=1,numcol
	write(11,13)cfnlist(i),(',',dout(i,ii),ii=2,iright)
 13	format(a12,100(a1,f10.5))
	write(6,*)cfnlist(i),i
	enddo
	close(11)
	
	open(11,file = 'stats_tvalue.csv')
	write(11,12)'ttest_tvalue',(',',clabels(ii),ii=2,iright)
	write(11,13)'ttest_values_unequalvariances',(',',tvalue(ii),ii=2,iright)
	write(11,13)'proba_values_unequalvariances',(',',pvalue(ii),ii=2,iright)
	write(11,13)'mean_group1',(',',mean1(ii),ii=2,iright)
	write(11,13)'stdev_group1',(',',stdev1(ii),ii=2,iright)
	write(11,13)'mean_group2',(',',mean2(ii),ii=2,iright)
	write(11,13)'stdev_group2',(',',stdev2(ii),ii=2,iright)
	write(11,13)'degreesof',(',',dof(ii),ii=2,iright)
	write(11,*)'Notes_There_were ',isize1,'subjects_from_group_1'
	write(11,*)'Notes_There_were ',isize2,'subjects_from_group_2'
	close(11)

	stop
	end
	


	subroutine ttest_unequalv(t,degreesof,averv,sdv)
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

