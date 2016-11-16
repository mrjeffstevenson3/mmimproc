**This file is a new machine setup recipe for brainteam sw on ubuntu 16.04 Mate system based on uhora.**
on brand new system:
1. install chrome browser
2. `mkdir ~/Software`
3. `sudo apt-get install python-pip gfortran`
4. `pip install conda`
5. download to ~/Software the py2.7 64bit anaconda installer from https://www.continuum.io/downloads#linux
6. in terminal `cd ~/Software && bash Anaconda2-4.2.0-Linux-x86_64.sh` #nb version numbers will change.
7. review and accept license and enter install location as /home/toddr/Software/anaconda2  and say yes to prepend to .bashrc
8. either open a new terminal or `source ~/.bashrc` 
9. then add basic python dependencies: `pip install pynrrd pathlib`
10. and from conda
	`conda install --channel https://conda.anaconda.org/dfroger pygpgme`
	`conda upgrade --all`
11. install pycharm into ~/Software and register
12. install pycharm plugins bashsupport and markdown, restart pycharm then in pycharm settings Project interpreter press cogwheel button add local and select the anaconda python interpreter at /home/mrjeffs/Software/anaconda2/bin/python
13. clone your master branch of pylabs from your github repo into ~/Software: `cd ~/Software && git clone https://github.com/mrjeffs/pylabs.git` (Replace mrjeffs with your github account id.)
14. Add the main pylabs repo as upstream: `cd ~/Software/pylabs && git remote add upstream https://github.com/ilabsbrainteam/pylabs.git`
15. in `cd ~/Software` dir for each of the following github packages clone, cd into and `python setup.py develop`:
	`cd ~/Software && git clone https://github.com/nipy/nibabel.git && cd nibabel && python setup.py develop`
	`cd ~/Software && git clone https://github.com/ilogue/niprov.git && cd niprov && python setup.py develop`
	`cd ~/Software && git clone https://github.com/nipy/dipy.git && cd dipy && python setup.py develop`
16. install ANTS:
	`sudo apt-get install cmake-curses-gui`
	`cd ~/Software && git clone https://github.com/stnava/ANTs.git && mkdir antsbin && cd antsbin && ccmake ../ANTs`
	when the cmake interface comes onscreen press c twice (to configure) till you see the option g appear on bottom middle, then press g to save and exit
	then type `make -j 4`
and open another terminal tab since this will take a while and there is more to do.
17. If you like, Install and setup Dropbox `https://www.dropbox.com` and teamviewer `https://www.teamviewer.com/en/`
18. install FSL. in terminal paste:
	`wget -O- http://neuro.debian.net/lists/xenial.us-ca.full | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list` and enter your admin pwd then
	`sudo apt-get update && sudo apt-get install fsl-5.0-core`
	when done download and copy into $FSLDIR/bin the cuda and/or openmp eddy current correction binaries
	`cd ~/Software && wget http://fsl.fmrib.ox.ac.uk/fsldownloads/patches/eddy-patch-fsl-5.0.9/centos6/{eddy_cuda7.5,eddy_openmp} && sudo cp {eddy_cuda7.5,eddy_openmp} /usr/share/fsl/5.0/bin`
19. Download and unpack Freesurfer latest Linux-centos6 development release into ~/Software at `ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/dev` and copy your .license file into the folder
20. using https://help.ubuntu.com/community/SettingUpNFSHowTo to set up NFS mounts:
    `sudo apt-get install nfs-common` and then `gksudo gedit /etc/fstab` and add the following tab delim line under #mount for NFS:
    <scotty_ip_addr>:/export /mnt    nfs auto    0   0
    `sudo ufw allow from <scotty_ip_addr>` on new machine and `sudo ufw allow from <your_new_ip_addr>` on scotty
    on scotty set up /etc/exports add to /exports AND /exports/users lines ` <your_new_ip_addr>(rw,nohide,insecure,no_subtree_check,async)` - pls include leading space.
    
