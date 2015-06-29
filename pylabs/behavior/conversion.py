import os


def csv2fslmat(csvfile):
    os.makedirs('matfiles')
    with open('matfiles/cardsorttotal.mat', 'w') as dummyfile:
        dummyfile.write('bla')
    #csvfile
    #out: .mat
