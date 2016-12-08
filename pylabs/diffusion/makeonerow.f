c program to make one row out of two rows for allvtk.txt
c
	character*120 cfn
	real r1(8)
	open(11,file= 'allvtk_run3.txt')
	open(12,file='allvtk_onerow.txt')
	do i=1,1000
	read(11,*,err=99,end=99)cfn
	write(6,*)cfn,i
	read(11,*)(r1(ii),ii=1,8)
	write(12,*)cfn,(r1(ii),ii=1,8)
	enddo
 99	close(11)
	close(12)
	stop
	end
	
