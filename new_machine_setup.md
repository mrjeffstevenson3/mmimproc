# This file is a new machine setup recipe for brainteam sw on ubuntu 16.04 Mate system based on uhora.
on brand new system:
1. **DO NOT INSTALL PIP, CONDA, OR PYTHON FROM UBUNTU REPOS. USE ONLY CONDA AND DELETE ANY REFS IN ~/.local/bin or ~/.local/lib.
    USE ONLY STEP 5 FOR PYTHON INSTALLATION.**
2. `mkdir ${HOME}/Software`
3. follow cuda_install instructions to get cuda working up to FSL part then continue back here.
3. setup build/development environment (paste as 1 liner):
```
sudo apt-get update && \
sudo apt-get install build-essential synaptic autoconf python-gpgme autogen libtool gfortran cmake-curses-gui software-properties-common uuid-dev libtiff5-dev:i386 libtiff5-dev -y && \
sudo apt-get install libinsighttoolkit4.9 libinsighttoolkit4-dev libinsighttoolkit4-dbg insighttoolkit4-python insighttoolkit4-examples libgdcm-tools -y && \
sudo add-apt-repository ppa:ubuntu-toolchain-r/test -y && \
sudo apt-get update && \
sudo apt-get install gcc-snapshot -y && \
sudo apt-get update && \
sudo apt-get install gcc-6 g++-6 -y && \
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-6 && \
sudo apt-get install gcc-4.8 g++-4.8 -y && \
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 40 --slave /usr/bin/g++ g++ /usr/bin/g++-4.8;
```
#### When completed, you must change to the gcc you want (here gcc 6) to work with by default. Type in your terminal:
`sudo update-alternatives --config gcc`

##### To verify if it worked. Just type in your terminal
`gcc -v`
5. download to ~/Software the py2.7 64bit anaconda installer from https://www.continuum.io/downloads#linux
   in terminal `cd ~/Software && bash Anaconda2-5.1.0-Linux-x86_64.sh` **#nb version numbers will change.**
   review and accept license and enter install location as /home/toddr/Software/anaconda2  and say yes to prepend to .bashrc
8. either open a new terminal to continue or `source ~/.bashrc`
9. update and configure conda and then add basic python dependencies/requirements:
    ```
    conda update conda && conda config --set channel_priority false && conda config --append channels conda-forge && conda config --append channels dfroger
    conda install pip sh pathlib pathlib2 pygpgme pydicom qgrid pytest-xdist pytest-env nose-timer python-pgpme
    conda upgrade --all
    pip install pynrrd petname latex shell argparse msgpack cloud
    ```
11. install pycharm into ~/Software and register
edit VM memory options to increase memory support for large files:
-Xms4000m
-Xmx10000m

12. install pycharm plugins bashsupport and markdown, restart pycharm then in pycharm settings Project interpreter press cogwheel button add local and select the anaconda python interpreter at ${HOME}/Software/anaconda2/bin/python
13. clone your master branch of pylabs from your github repo into ~/Software: `cd ~/Software && git clone https://github.com/mrjeffs/pylabs.git` (Replace mrjeffs with your github account id.)
14. Add the main pylabs repo as upstream:
    `cd ~/Software/pylabs && git remote add upstream https://github.com/ilabsbrainteam/pylabs.git`
15. in `cd ~/Software` dir for each of the following github packages clone, cd into and `python setup.py develop:
    ```
    cd ${HOME}/Software && git clone https://github.com/nipy/nibabel.git && cd nibabel && python setup.py develop
	cd ${HOME}/Software && git clone https://github.com/ilogue/niprov.git && cd niprov && python setup.py develop
	cd ${HOME}/Software && git clone https://github.com/nipy/dipy.git && cd dipy && python setup.py develop
	cd ${HOME}/Software && git clone https://github.com/nipy/nipype.git && cd nipype && python setup.py develop
	cd ${HOME}/Software && git clone https://github.com/euske/pdfminer.git && cd pdfminer && python setup.py install
	cd ${HOME}/Software && git clone https://github.com/ANTsX/ANTsPy.git && cd ANTsPy && python setup.py develop
	cd ${HOME}/Software && git clone https://github.com/yeatmanlab/AFQ.git
	cd ${HOME}/Software && git clone https://github.com/vistalab/vistasoft.git
	cd ${HOME}/Software && git clone https://github.com/stnava/ANTs.git && mkdir antsbin && cd antsbin && ccmake ../ANTs
	```
	#### when the cmake interface comes onscreen press c twice (to configure) till you see the option g appear on bottom middle, then press g twice to save and exit. then type
	`make -j 4`
	
    **and** open another terminal tab since this will take a while and there is more to do.
17. If you like, Install and setup Dropbox `https://www.dropbox.com` and teamviewer `https://www.teamviewer.com/en/`
18. install FSL. first install requirements for for fsleyes:
    ```
    sudo apt-get update
    sudo apt-get install freeglut3 libsdl1.2debian
    sudo apt-get install libgtk2.0-dev libgtk-3-dev libwebkitgtk-dev libwebkitgtk-3.0-dev
    sudo apt-get install libjpeg-turbo8-dev libtiff5-dev libsdl1.2-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3-dev
    ```
    check if platform function will work. either `cat /etc/debian_version` or in python
    ```python
    import platform;
    platform.linux_distribution(full_distribution_name=0)
    ```
    result should read ('debian', '16.04', '') or higher if ubuntu release is > 16.04.
    if result not release number the overwrite /etc/debian_version with actual number eg:
    `cd ${HOME}/Software && echo "16.04" > debian_version && sudo cp debian_version /etc/debian_version`
    then download fslinstaller.py from https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/Linux
	when done downloading type/paste and be sure to accept updating bashrc
	`python fslinstaller.py && source ${HOME}/.bashrc`
	or run this one liner:
	```
	brc=${HOME}/.bashrc && echo "FSLDIR=/usr/local/fsl" >> $brc && echo ". \${FSLDIR}/etc/fslconf/fsl.sh" >> $brc && \
	echo "PATH=\${FSLDIR}/bin:\${PATH}" >> $brc && echo "export FSLDIR PATH" >> $brc && source $brc
	```
	download eddy and bedpostx patches from https://fsl.fmrib.ox.ac.uk/fsldownloads/patches/ and https://users.fmrib.ox.ac.uk/~moisesf/Bedpostx_GPU/Installation.html and copy into $FSLDIR/bin and /lib dirs
	```
	mkdir -p ${HOME}/Software/fsl_patches/bedpostx_gpu_cuda8.0 && cd ${HOME}/Software/fsl_patches && wget https://fsl.fmrib.ox.ac.uk/fsldownloads/patches/eddy-patch-fsl-5.0.11/centos6/eddy_cuda8.0 && \
	cd bedpostx_gpu_cuda8.0 && wget http://users.fmrib.ox.ac.uk/~moisesf/Bedpostx_GPU/CUDA_8.0/bedpostx_gpu.zip && unzip bedpostx_gpu.zip && \
	sudo mv ${FSLDIR}/lib/libbedpostx_cuda.so ${FSLDIR}/lib/libbedpostx_cuda.so_orig && sudo cp lib/libbedpostx_cuda.so ${FSLDIR}/lib/libbedpostx_cuda.so && sudo chmod 777 ${FSLDIR}/lib/libbedpostx_cuda.so && \
	for f in `ls bin`; do sudo mv ${FSLDIR}/bin/${f} ${FSLDIR}/bin/${f}_orig; sudo cp bin/${f} ${FSLDIR}/bin; sudo chmod 777 ${FSLDIR}/bin/${f}; done && \
	```
19. Download and unpack Freesurfer and infant latest Linux-centos7 development release into ~/Software at `ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/dev` and copy your .license file into the folder and update ~/.bashrc with
    extract and rename freesurfer folders:
    infant folder name from extracting archive: freesurfer freesurfer_dev20180503_infant  # date will not change much
    adult folder name from extracting archive: freesurfer freesurfer_dev20180503_adult   # date will change
    ```
    # Freesurfer configuration
    alias recon-alli='reconallinfant'
    alias recon-alla='reconalladult'
    function reconallinfant() { export FREESURFER_HOME=${HOME}/Software/freesurfer_dev20180503_infant;
        source $FREESURFER_HOME/SetUpFreeSurfer.sh; export SUBJECTS_DIR=${PWD}; 
        echo "Current freesurfer subject directory is now $SUBJECTS_DIR. running infant recon-all"; echo -e "mris_inflate -n 15\n" > freesurf_expert_opts.txt; recon-all "$@" ;
        }
    function reconalladult() { export FREESURFER_HOME=${HOME}/Software/freesurfer_dev20180503_adult;
        source $FREESURFER_HOME/SetUpFreeSurfer.sh; export SUBJECTS_DIR=${PWD}; 
        echo "Current freesurfer subject directory is now $SUBJECTS_DIR. running adult recon-all"; echo -e "mris_inflate -n 15\n" > freesurf_expert_opts.txt; recon-all "$@" ;
        }
    ```
20. install camino and R using ~/Software/Dropbox/bash_scripts/how_to_install_camino_and_R.txt
21. using https://help.ubuntu.com/community/SettingUpNFSHowTo to set up NFS mounts:
    `sudo apt-get install nfs-common` and then `gksudo gedit /etc/fstab` and add the following tab delim line under #mount for NFS:
    <scotty_ip_addr>:/export /mnt    nfs auto    0   0
    `sudo ufw allow from <scotty_ip_addr>` on new machine and `sudo ufw allow from <your_new_ip_addr>` on scotty
    on scotty set up /etc/exports add to /exports AND /exports/users lines ` <your_new_ip_addr>(rw,nohide,insecure,no_subtree_check,async)` - pls include leading space.
22. copy scotty .bashrc appropriate elements to ${HOME}/.bashrc (hint use pycharm compare file fn)
    here are some pylabs env vars to put at the end to make sure bash scripts find their way:
    ```
    #set up pylabs env variables
    PYLABSD=`python -c "from pylabs.utils import pylabs_datadir; print str(pylabs_datadir)"`
    PYLABS=`python -c "from pylabs.utils import pylabs_dir; print str(pylabs_dir)"`
    DATADIR=`python -c "import pylabs; pylabs.datadir.target = 'jaba'; from pylabs.utils.paths import getnetworkdataroot; fs = getnetworkdataroot(verbose=False); print fs"`
    PATH="$PYLABS:$PYLABSD:$PYLABS/pylabs:$PYLABS/bin:$PATH"
    MORIMNI=`python -c "from pylabs.utils import moriMNIatlas; print str(moriMNIatlas)"`
    JHUMNI=`python -c "from pylabs.utils import JHUMNIatlas; print str(JHUMNIatlas)"`
    FS=`python -c "import pylabs; pylabs.datadir.target = 'jaba'; from pylabs.utils.paths import getnetworkdataroot; fs = getnetworkdataroot(verbose=False); print fs"`
    export PYLABS PYLABSD DATADIR PATH FS MORIMNI JHUMNI
    ```
23. install and start condor: `sudo apt install htcondor && sudo service condor start`

    ~~**do not use! --- wait on this one-bugs!** ----install sip, pyqt4, mayavi, pysurfer:
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
    XX24. install vtk and mayavi and pysurfer as prereqs: do not use
        cd ${HOME}/Software
        conda install vtk
        pip install mayavi pysurfer~~
        
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

29. install matlab NOT as root but as user in ${HOME}/Software/matlab${ReleaseDate}
    as of 9/19/2017 need latest release for python interface build and maybe (tbd) 2013b for inspector on linux 2016b on mac
        make sure conda is latest release and anaconda or env is latest:
        conda install conda
        conda upgrade --all
        ReleaseDate=2017b
        cd ${HOME}/Software/matlab${ReleaseDate}/extern/engines/python
        python setup.py install --prefix=${HOME}/Software/anaconda2
        note __init__ import bug in ubuntu pycharm console and runtime engine. use only on comand line till fixed
        
30. install gannett 2.0 sw in ${HOME}/Software
        on linux make sure to edit philipsRead.m line 60:
        ```% work out data header name
        sparnameW = [fname_water(1:(end-4)) 'SPAR']; ```
        this makes sure the spar file ext is read on linux eg all upper case.
        
31. install inspector sw in ${HOME}/Software (depends on matlab R2013b )

32. install spm12 and spm8 sw in ${HOME}/Software (depends on matlab)

33. install octave:
    linux: sudo apt-get install octave
    mac: make sure xquratz and xcode command line tools are installed from apple. then
        # install Homebrew http://brew.sh/ if you don't already have it 
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" 
        # install some Octave dependencies, the update/upgrade command below could take a while
        brew update && brew upgrade
        brew install gcc # or 'brew reinstall gcc' if you have an older gcc without gfortran in it
        # skip for now...
                # You may also need to install mactex (see http://tex.stackexchange.com/questions/97183/what-are-the-practical-differences-between-installing-latex-from-mactex-or-macpo)
                # The download here takes a while...
                brew cask install mactex 
                export PATH=$PATH:/usr/texbin
                
                # install X11 -> should use apple xqurartz site
                brew cask install xquartz
        
        # install gnuplot
        brew install gnuplot --with-x11
        
        # install octave
        brew install octave --with-x11