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
9. then add basic python dependencies: `pip install pynrrd pathlib pydicom`
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
	`cd ~/Software && wget http://fsl.fmrib.ox.ac.uk/fsldownloads/patches/eddy-patch-fsl-5.0.9/centos6/{eddy_cuda7.5,eddy_openmp} && sudo cp {eddy_cuda7.5,eddy_openmp} /usr/share/fsl/5.0/bin && sudo chmod 777 /usr/share/fsl/5.0/bin/{eddy_cuda7.5,eddy_openmp}`
19. Download and unpack Freesurfer latest Linux-centos6 development release into ~/Software at `ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/dev` and copy your .license file into the folder and update ~/.bashrc with
`# Freesurfer configuration
export FREESURFER_HOME=/home/toddr/Software/freesurfer_dev20161104 #change date stamp to your dev release date 
source $FREESURFER_HOME/SetUpFreeSurfer.sh`
20. install camino and R using ~/Software/Dropbox/bash_scripts/how_to_install_camino_and_R.txt
21. using https://help.ubuntu.com/community/SettingUpNFSHowTo to set up NFS mounts:
    `sudo apt-get install nfs-common` and then `gksudo gedit /etc/fstab` and add the following tab delim line under #mount for NFS:
    <scotty_ip_addr>:/export /mnt    nfs auto    0   0
    `sudo ufw allow from <scotty_ip_addr>` on new machine and `sudo ufw allow from <your_new_ip_addr>` on scotty
    on scotty set up /etc/exports add to /exports AND /exports/users lines ` <your_new_ip_addr>(rw,nohide,insecure,no_subtree_check,async)` - pls include leading space.
22. copy scotty .bashrc appropriate elements to ${HOME}/.bashrc (hint use pycharm compare file fn)  
23. install and start condor: `sudo apt install htcondor && sudo service condor start`
24. _--- wait on this one-bugs! ----install sip, pyqt4, mayavi, pysurfer:_ 
        cd ${HOME}/Software
        https://riverbankcomputing.com/software/sip/download
        example docs:
        file:///Users/mrjeffs/Software/sip-4.19.2.dev1703031758/doc/html/build_system.html
        cd sip-4.19*
        python configure.py
        make
        make install
        cd ..
        http://pyqt.sourceforge.net/Docs/PyQt4/installation.html#downloading-pyqt4
        cd PyQt4*
        python configure-ng.py
        make
        make install
        cd ..
        git clone https://github.com/enthought/mayavi
        cd mayavi
        python setup.py develop
        cd ..
        git clone https://github.com/nipy/PySurfer
        cd PySurfer
        python setup.py develop
25. install into ${HOME}/Software the nightly build of mne-c from https://www.martinos.org/mne/stable/getting_started.html (need user name, pwd, and lic)
        library problems: libxp6, libquicktime, libgfortran (or gfortran installed above),
        sudo vim /etc/apt/sources.list
        # append this line to sources list by scrolling down to empty line hit i  (FOR INSERT) THEN PASTE:
        deb http://security.ubuntu.com/ubuntu precise-security main
        # hit
        esc :wq
        # to save file with new repo, then
        sudo apt update
        sudo apt-get install libxp6
        sudo apt-get install libquicktime2
        # make hard links to missing older lib files
        cd /usr/lib/x86_64-linux-gnu/
        ls -l libquicktime*
        sudo ln -s libquicktime.so.2 libquicktime.so
        sudo ln -s libgfortran.so.3 libgfortran.so.1
        # then copy following to .bashrc (again assumes Software under home folder is where mne lives)
            #setup mne
            MNE_ROOT=${HOME}/Software/MNE-2.7.4-3514-Linux-x86_64
            PATH=${HOME}/Software/MNE-2.7.4-3514-Linux-x86_64/bin:$PATH
            # optional matlab hook. need to change/update release name
            MATLAB_ROOT=/usr/local/MATLAB/R2016b/bin/matlab
            export PATH MNE_ROOT MATLAB_ROOT
            . $MNE_ROOT/bin/mne_setup_sh

26. Download and install the brain connectivity toolkit from https://sites.google.com/site/bctnet in ~/Software

27. Download and install rclone for linux google drive and dropbox comand line execution from https://rclone.org/downloads/ or see below:
        **Fetch and unpack** 
        curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
        unzip rclone-current-linux-amd64.zip
        cd rclone-*-linux-amd64 
        **Copy binary file**
        sudo cp rclone /usr/bin/
        sudo chown root:root /usr/bin/rclone
        sudo chmod 755 /usr/bin/rclone
        **Install manpage**
        sudo mkdir -p /usr/local/share/man/man1
        sudo cp rclone.1 /usr/local/share/man/man1/
        sudo mandb 
        **Run rclone config to setup. See rclone config docs for more details.**
        rclone config
            set up as teamdrive using existing google drive hierarchy eg ${HOME}/Software/gdrive/NBWR/subject_scans/results

28. install into ${HOME}/Software pdfminer:
        cd ${HOME}/Software
        git clone https://github.com/euske/pdfminer.git
        cd pdfminer/
        python setup.py install

29. install matlab NOT as root but as user in ${HOME}/Software/matlab${ReleaseDate}
    as of 9/19/2017 need latest release for python interface build and maybe (tbd) 2013b for inspector on linux 2016b on mac
        make sure conda is latest release and anaconda or env is latest:
        conda install conda
        conda upgrade --all
        ReleaseDate=2017b
        cd ${HOME}/Software/matlab${ReleaseDate}/extern/engines/python
        python setup.py install --prefix=${HOME}/Software/anaconda2
        note bug in pycharm console and runtime engine. use only on comand line till fixed
        
30. install gannett 2.0 sw in ${HOME}/Software
        on linux make sure to edit philipsRead.m line 60:
        ```% work out data header name
        sparnameW = [fname_water(1:(end-4)) 'SPAR']; ```
        this makes sure the spar file ext is read on linux eg all upper case.
        