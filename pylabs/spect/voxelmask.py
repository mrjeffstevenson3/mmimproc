from nipype.interfaces import fsl


coordsfile = 'pylabs/spect/coords.txt'
basefile = fsl.Info.standard_image('MNI152_T1_1mm_brain.nii.gz')

coords = []
with open(coordsfile) as cfile:
    lines = cfile.readlines()
    for line in lines:
        coords.append(line.split()[0:3])

sides = [
(0,1)
(1,2)
(2,3)
(4,5)
(5,6)
(6,7)
(0,4)
(1,5)
(2,6)
(3,7)
(0,3)
(4,7)
]


