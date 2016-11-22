c program to make one row out of two rows for allvtk.txt
c
	character*120 cfn
	real r1(8)
	open(11,file= 'allvtk.txt')
	open(12,file='allvtk_onerow.txt')
	do i=1,349
	read(11,*)cfn
	write(6,*)cfn
	read(11,*)(r1(ii),ii=1,8)
	write(12,*)cfn,(r1(ii),ii=1,8)
	enddo
	close(11)
	close(12)
	stop
	end
	
