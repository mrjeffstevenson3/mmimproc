c program to make one row out of two rows for allvtk.txt
c
	character*120 cfn
	character*40 cfnin
	real r1(8)
	write(6,*)'enter the input file name '
	read(5,*)cfnin
	open(11,file= cfnin)
	open(12,file='allvtk_onerow.txt')
 98	continue
	read(11,*,err=99,end=99)cfn
	write(6,*)cfn
	read(11,*)(r1(ii),ii=1,8)
	write(12,*)cfn,(r1(ii),ii=1,8)
	go to 98
 99	continue
	close(11)
	close(12)
	stop
	end
	
