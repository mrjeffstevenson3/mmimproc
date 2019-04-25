	COMMON /NMRDAT/pnmr(200000),dnmr(200000),isize,YSC
	COMMON /XFACTOR/rFACT
	COMMON /OFFSET/LLEDGE,psav(100000),DSAV(100000)
	COMMON /SPARAM/RMIN,SCALE,IOFFSET
	COMMON /APOD1/rLB
	common /resolu/renh,rsmo
	COMMON /OPTION/OPT
	common /filen/cfn2
	common /dsize/jsize
	common /passppm/rinfo(10)
	common /bound/ipf(20),ips(20),ipenum
	COMMON /PASSPM/iszbeg
	COMMON /NMRfit/Dfit(66000)
c
c
	character*40 cfn2
