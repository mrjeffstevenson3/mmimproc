**This file is a new machine setup recipe for brainteam sw on ubuntu 16.04 Mate system based on uhora.**
on brand new system:
1. install chrome browser
2. `mkdir ~/Software`
3. install pycharm into ~/Software and register
4. install pycharm plugins bashsupport and markdown
5. clone pylabs from your github repo into ~/Software
6. `sudo apt install python-pip`
7. `pip install conda`
8. download to ~/Software the py2.7 64bit anaconda installer from https://www.continuum.io/downloads#linux
9. in terminal `cd ~/Software && bash Anaconda2-4.2.0-Linux-x86_64.sh` #nb version numbers will change.
10. review and accept license and enter install location as /home/toddr/Software/anaconda2  and say yes to prepend to .bashrc
11. either open a new terminal or `source ~/.bashrc` then in pycharm settings Project interpreter cogwheel button add local
12. in ~/Software dir for each of the following github packages clone, cd into and `python setup.py develop`
