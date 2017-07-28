
	real imagef(68,68),waytotal(68),row(68)
c
	open(11,file = 'fdt_network_matrix')
	do j=1,68
	read(11,*)(row(i),i=1,68)
	do i=1,68
	imagef(i,j) = row(i)
	enddo
	write(6,*)row(1),row(2)
	enddo
	close(11)
	open(11,file = 'waytotal')
	do i=1,68
	read(11,*)waytotal(i)
	enddo
	close(11)
	open(11,file = 'fdt_network_matrix2')
	do j=1,68
	write(11,*)((imagef(i,j)/waytotal(j)),i=1,68)
	enddo
	close(11)
	stop
	end
