c
c this is software to test all of the network results for bbc for
c paired ttest
c
	character*40 cfn,cfnlist(100),cheader(100),ch
	character*40 cout,csubjects(100)
	character*20 clabels(100)
	common /dat1/ dmnmr(1000),dmnmr2(1000),dmnmr3(1000)
	common /size/isize1,isize2
	real dnmr(100,100),behav1(10000),dout(100,100)
	character*1 c1
	
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
	cout(14:25)=ch(1:10)
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
	call ttest_unequalv(t)
	write(6,*)t,imetab
	endif !for left
	enddo  !imetab
c
c output new files
c
	write(6,*)'ileft ',ileft
	open(11,file = 'csfcorrected.csv')
	write(11,12)clabels(1),(',',clabels(ii),ii=2,ileft)
 12	format(10a,100(1a,10a))
	do i=1,numcol
	write(11,13)cfnlist(i),(',',dout(i,ii),ii=2,ileft)
 13	format(a12,100(a1,f10.5))
	write(6,*)cfnlist(i),i
	enddo
	close(11)
	

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
	incv(1) = isize1
	incv(2) = isize2
	call average2(averv(1),sdv(1),stem)
	sum1 = 0
	do i=1,isize1
	sum1 = sum1 + ((dmnmr(i)-averv(1))*(dmnmr(i)-averv(1)))
	enddo
	s1s2 = sum1/incv(1)
	
c	write(6,*)'aver1 sdv, stem ',averv(1),sdv(1),stem,incv(1)
	isize1=isize2
	do i=1,isize1
	dmnmr(i)=dmnmr2(i)
	enddo
	call average2(averv(2),sdv(2),stem)
	sum1 = 0
	do i=1,isize2
	sum1 = sum1 + ((dmnmr(i)-averv(1))*(dmnmr(i)-averv(1)))
	enddo
	s2s2 = sum1/incv(2)

c	write(6,*)'aver2 sdv, stem ',averv(2),sdv(2),stem,incv(2),s1s2,s2s2
	t = averv(1) - averv(2)
c	denom = sqrt( (s1s2/incv(1) )+ s2s2/incv(2) )
	denom = sqrt( ((sdv(1)*sdv(1))/incv(1) )+ ((sdv(2)*sdv(2))/incv(2)) )
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
