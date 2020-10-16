# This file is a new mac laptop setup recipe for mmimproc sw on Mojave.
on brand new system:
1. **Install XCode (note compatible version with myMacOS=10.14 myXcode=10.3), XQuartz, get from apple dev site
 https://developer.apple.com/download/more/ Command_Line_Tools_macOS_10.14_for_Xcode_10.1.dmg,
 gcc and gfortran 8.1, R-3.5.3.pkg and octave 4.3 for macos, jre-8u201-macosx-x64.dmg or latest, .**
1.5 install homebrew `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
3. set up ssh: `ssh-keygen -t rsa -b 4096 && chmod 400 ~/.ssh/id_rsa && pbcopy < ~/.ssh/id_rsa.pub` login to your github acct and paste into sshkey in profile.
2. `mkdir -p ${HOME}/Software`
3. no cuda as of yet on new mac laptops. plan on using cloud.
4. Install python 2.7 as base and a 3.6 env using anaconda distro at `https://www.anaconda.com/distribution/` and installing with prefix=${HOME}/Software.
7. `cd ${HOME}/Downloads && bash Anaconda2-2018.12-MacOSX-x86_64.sh -p ${HOME}/Software` **version number will change**
5. `cd ${HOME}/Software && git clone https://github.com/mrjeffstevenson3/mmiproc.git` 
6. `cd ${HOME}/Software/mmimproc && conda create --name py36tf --file environment_py27.yml`




