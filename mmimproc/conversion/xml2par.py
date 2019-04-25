# todo: drop interface and make callable function with input .xml and output .PAR fnames
# convert xml into par format
#
# ----- VERSION HISTORY -----
#
# Version 0.1 - 14, October 2015
#       - 1st Beta Release
# Version 0.2 - 22, October 2015
#       - reverse translation of patient positioning (beyond HFS-->Head First Supine)
#       - reverse translation of phase encode directions (beyond AP-->Anterior-Posterior)
#       - reverse translation of image type
#       - reverse translation of sequence type
#       - reverse translation of "info" tags (Display Orientation, Slice Orientation, fMRI Status Indication, Image Type Ed Es)
#       - reverse translation of contrast type
#       - reverse translation of anisotropy direction
#       - reverse translation of label type
#       - crop string condition inlcuded in form_str_len
#
# ----- LICENSE -----
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License (GPL) as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version. For more detail see the
#    GNU General Public License at <http://www.gnu.org/licenses/>.
#    additionally to the GPL the following license terms apply:
#
#    1) Personal NO MILTARY clause:
#    THE USE OF THIS SOFTWARE OR ANY PARTS OF IT IS EXPLICITLY PROHIBITED FOR
#    MILITARY INSTITUTIONS, BOTH GOVERNMENTAL AND PRIVATE "SECURITY" SERVICES,
#    AND ANY INSTITUTIONS DIRECTLY OR INDIRECTLY LINKED TO INTELLIGENCE SERVICES,
#    BOTH FOR MILITARY AND CIVIL ESPIONAGE. THIS INCLUDES, BUT IS NOT LIMITED TO,
#    CIVIL SERVICES RUN BY THE MILITARY, SUCH AS MILITARY HOSPITALS.
#
#
# ----- REQUIREMENTS -----
#
#    This program was developed under Python Version 2.7.6 for Windows 32bit
#    a windows standalone executable can be "compiled" with PyInstaller or py2exe
#
#
# ----- to do -----
#
#    see the comments "# some issue here: ....", basically the following:
#       - check reverse translation of Slice Orientation (should be OK)
#       - check reverse translation of anisotropy direction (probably doen't matter)
#   error conditions and messaging in case somke XML tag is not found
#   more general/better handling of the 3 "find_xml_" soubroutines
#   improove handling of array type XML tags ("Phase Encoding Velocity" and "Pixel Spacing")
#

'''
# this 1st commented out section and a second option.
import xml.etree.ElementTree as ET
import sys, os
from Tkinter import Tk
from tkFileDialog import askopenfilename

def find_xml_seriesinfo(name):
    result=''
    for info in root[0]:
        if info.get('Name')==(name):
            result=info.text
    return result
def find_xml_imageinfo1(name,index):
    result=''
    for info in root[1][index][0]:
        if info.get('Name')==(name):
            result=info.text
    return result
def find_xml_imageinfo2(name,index):
    result=''
    for info in root[1][index]:
        if info.get('Name')==(name):
            result=info.text
    return result

def format_number(str_number,digits):
    form = "{:."+str(digits)+"f}"
    num = form.format(float(str_number))
    return str(num)
def form_str_len (str,size):
    result=''
    if len(str)>=size-1: result=' '+str[0:size-1]
    else:
        for i in range(0, size-len(str)): result+=' '
        result+=str
    return result

#  ------------------- Main programm starts here ---------------------------

TKwindows = Tk(); TKwindows.withdraw() #hiding tkinter window
TKwindows.attributes( '-topmost', True ) #stay on top
TKwindows.overrideredirect(True) # even over fullscreen apps


# open file dialog
input_file = askopenfilename(title="Open IVIM Diffusion file", filetypes=[("XML files",".xml")])
if input_file == "": print('No input file specified'); sys.exit(1)
tree = ET.parse(input_file)
root = tree.getroot()

#open outfile
output_file = os.path.splitext(input_file)[0]+'.par'
outfile = open(output_file, 'w')

#write header
outfile.write ('# === DATA DESCRIPTION FILE ======================================================\n')
outfile.write ('#\n')
outfile.write ('# CAUTION - Investigational device.\n')
outfile.write ('# Limited by Federal Law to investigational use.\n')
outfile.write ('#\n')
outfile.write ('# Dataset name: '+input_file[:input_file.find('.')]+'\n')
outfile.write ('#\n')
outfile.write ('# CLINICAL TRYOUT             Research image export tool     V4.2\n')
outfile.write ('#\n')
outfile.write ('# === GENERAL INFORMATION ========================================================\n')
outfile.write ('#\n')

#write general info
outfile.write ('.    Patient name                       :   '+find_xml_seriesinfo ('Patient Name')+'\n')
outfile.write ('.    Examination name                   :   '+find_xml_seriesinfo ('Examination Name')+'\n')
outfile.write ('.    Protocol name                      :   '+find_xml_seriesinfo ('Protocol Name')+'\n')
outfile.write ('.    Examination date/time              :   '+find_xml_seriesinfo ('Examination Date')+' / '+find_xml_seriesinfo ('Examination Time')+'\n')
outfile.write ('.    Series Type                        :   Image   MRSeries\n')
outfile.write ('.    Acquisition nr                     :   '+find_xml_seriesinfo ('Aquisition Number')+'\n')
outfile.write ('.    Reconstruction nr                  :   '+find_xml_seriesinfo ('Reconstruction Number')+'\n')
outfile.write ('.    Scan Duration [sec]                :   '+format_number(find_xml_seriesinfo ('Scan Duration'),0)+'\n')
outfile.write ('.    Max. number of cardiac phases      :   '+find_xml_seriesinfo ('Max No Phases')+'\n')
outfile.write ('.    Max. number of echoes              :   '+find_xml_seriesinfo ('Max No Echoes')+'\n')
outfile.write ('.    Max. number of slices/locations    :   '+find_xml_seriesinfo ('Max No Slices')+'\n')
outfile.write ('.    Max. number of dynamics            :   '+find_xml_seriesinfo ('Max No Dynamics')+'\n')
outfile.write ('.    Max. number of mixes               :   '+find_xml_seriesinfo ('Max No Mixes')+'\n')
pos=find_xml_seriesinfo ('Patient Position')
position=''
if pos.find('HF')>=0: position += 'Head First'
if pos.find('FF')>=0: position += 'Feet First'
if pos.find('S')>=0: position += ' Supine'
if pos.find('P')>=0: position += ' Prone'
if pos.find('D')>=0: position += ' Decubitus'
if pos.find('R')>=0: position += ' Right'
if pos.find('L')>=0: position += ' Left'
if position=='': position=pos
outfile.write ('.    Patient position                   :   '+position+'\n')
prep=find_xml_seriesinfo ('Preparation Direction')
if prep.find('AP')>=0: prep= 'Anterior-Posterior'
elif prep.find('RL')>=0: prep= 'Right-Left'
elif prep.find('FH')>=0: prep= 'Foot-Head'
outfile.write ('.    Preparation direction              :   '+prep+'\n')
outfile.write ('.    Technique                          :   '+find_xml_seriesinfo ('Technique')+'\n')
outfile.write ('.    Scan resolution  (x, y)            :   '+find_xml_seriesinfo ('Scan Resolution X')+'  '+find_xml_seriesinfo ('Scan Resolution Y')+'\n')
outfile.write ('.    Scan mode                          :   '+find_xml_seriesinfo ('Scan Mode')+'\n')
outfile.write ('.    Repetition time [ms]               :   '+format_number(find_xml_seriesinfo ('Repetition Times'),3)+'\n')
outfile.write ('.    FOV (ap,fh,rl) [mm]                :   '+format_number(find_xml_seriesinfo ('FOV AP'),3)+'  '+format_number(find_xml_seriesinfo ('FOV FH'),3)+'  '+format_number(find_xml_seriesinfo ('FOV RL'),3)+'\n')
outfile.write ('.    Water Fat shift [pixels]           :   '+format_number(find_xml_seriesinfo ('Water Fat Shift'),3)+'\n')
outfile.write ('.    Angulation midslice(ap,fh,rl)[degr]:   '+format_number(find_xml_seriesinfo ('Angulation AP'),3)+'  '+format_number(find_xml_seriesinfo ('Angulation FH'),3)+'  '+format_number(find_xml_seriesinfo ('Angulation RL'),3)+'\n')
outfile.write ('.    Off Centre midslice(ap,fh,rl) [mm] :   '+format_number(find_xml_seriesinfo ('Off Center AP'),3)+'  '+format_number(find_xml_seriesinfo ('Off Center FH'),3)+'  '+format_number(find_xml_seriesinfo ('Off Center RL'),3)+'\n')
flowcomp=find_xml_seriesinfo ('Flow Compensation')
if flowcomp=='N': flowcomp='0';
else: flowcomp='1'
outfile.write ('.    Flow compensation <0=no 1=yes> ?   :   '+flowcomp+'\n')
presat=find_xml_seriesinfo ('Presaturation')
if presat=='N': presat='0';
else: presat='1'
outfile.write ('.    Presaturation     <0=no 1=yes> ?   :   '+presat+'\n')
dummy=str(find_xml_seriesinfo ('Phase Encoding Velocity'))
str1=dummy.split()[0]
str2=dummy.split()[1]
str3=dummy.split()[2]
outfile.write ('.    Phase encoding velocity [cm/sec]   :   '+format_number(str1,6)+'  '+format_number(str2,6)+'  '+format_number(str3,6)+'\n')
mtc=find_xml_seriesinfo ('MTC')
if mtc=='N': mtc='0';
else: mtc='1'
outfile.write ('.    MTC               <0=no 1=yes> ?   :   '+mtc+'\n')
spir=find_xml_seriesinfo ('SPIR')
if spir=='N': spir='0';
else: spir='1'
outfile.write ('.    SPIR              <0=no 1=yes> ?   :   '+spir+'\n')
outfile.write ('.    EPI factor        <0,1=no EPI>     :   '+find_xml_seriesinfo ('EPI factor')+'\n')
dyn=find_xml_seriesinfo ('Dynamic Scan')
if dyn=='N': dyn='0';
else: dyn='1'
outfile.write ('.    Dynamic scan      <0=no 1=yes> ?   :   '+dyn+'\n')
diff=find_xml_seriesinfo ('Diffusion')
if diff=='N': diff='0';
else: diff='1'
outfile.write ('.    Diffusion         <0=no 1=yes> ?   :   '+diff+'\n')
outfile.write ('.    Diffusion echo time [ms]           :   '+format_number(find_xml_seriesinfo ('Diffusion Echo Time'),4)+'\n')
outfile.write ('.    Max. number of diffusion values    :   '+find_xml_seriesinfo ('Max No B Values')+'\n')
outfile.write ('.    Max. number of gradient orients    :   '+find_xml_seriesinfo ('Max No Gradient Orients')+'\n')
outfile.write ('.    Number of label types   <0=no ASL> :   '+find_xml_seriesinfo ('No Label Types')+'\n')

#write instructions
outfile.write ('#\n')
outfile.write ('# === PIXEL VALUES =============================================================\n')
outfile.write ('#  PV = pixel value in REC file, FP = floating point value, DV = displayed value on console\n')
outfile.write ('#  RS = rescale slope,           RI = rescale intercept,    SS = scale slope\n')
outfile.write ('#  DV = PV * RS + RI             FP = DV / (RS * SS)\n')
outfile.write ('#\n')
outfile.write ('# === IMAGE INFORMATION DEFINITION =============================================\n')
outfile.write ('#  The rest of this file contains ONE line per image, this line contains the following information:\n')
outfile.write ('#\n')
outfile.write ('#  slice number                             (integer)\n')
outfile.write ('#  echo number                              (integer)\n')
outfile.write ('#  dynamic scan number                      (integer)\n')
outfile.write ('#  cardiac phase number                     (integer)\n')
outfile.write ('#  image_type_mr                            (integer)\n')
outfile.write ('#  scanning sequence                        (integer)\n')
outfile.write ('#  index in REC file (in images)            (integer)\n')
outfile.write ('#  image pixel size (in bits)               (integer)\n')
outfile.write ('#  scan percentage                          (integer)\n')
outfile.write ('#  recon resolution (x y)                   (2*integer)\n')
outfile.write ('#  rescale intercept                        (float)\n')
outfile.write ('#  rescale slope                            (float)\n')
outfile.write ('#  scale slope                              (float)\n')
outfile.write ('#  window center                            (integer)\n')
outfile.write ('#  window width                             (integer)\n')
outfile.write ('#  image angulation (ap,fh,rl in degrees )  (3*float)\n')
outfile.write ('#  image offcentre (ap,fh,rl in mm )        (3*float)\n')
outfile.write ('#  slice thickness (in mm )                 (float)\n')
outfile.write ('#  slice gap (in mm )                       (float)\n')
outfile.write ('#  image_display_orientation                (integer)\n')
outfile.write ('#  slice orientation ( TRA/SAG/COR )        (integer)\n')
outfile.write ('#  fmri_status_indication                   (integer)\n')
outfile.write ('#  image_type_ed_es  (end diast/end syst)   (integer)\n')
outfile.write ('#  pixel spacing (x,y) (in mm)              (2*float)\n')
outfile.write ('#  echo_time                                (float)\n')
outfile.write ('#  dyn_scan_begin_time                      (float)\n')
outfile.write ('#  trigger_time                             (float)\n')
outfile.write ('#  diffusion_b_factor                       (float)\n')
outfile.write ('#  number of averages                       (integer)\n')
outfile.write ('#  image_flip_angle (in degrees)            (float)\n')
outfile.write ('#  cardiac frequency   (bpm)                (integer)\n')
outfile.write ('#  minimum RR-interval (in ms)              (integer)\n')
outfile.write ('#  maximum RR-interval (in ms)              (integer)\n')
outfile.write ('#  TURBO factor  <0=no turbo>               (integer)\n')
outfile.write ('#  Inversion delay (in ms)                  (float)\n')
outfile.write ('#  diffusion b value number    (imagekey!)  (integer)\n')
outfile.write ('#  gradient orientation number (imagekey!)  (integer)\n')
outfile.write ('#  contrast type                            (string)\n')
outfile.write ('#  diffusion anisotropy type                (string)\n')
outfile.write ('#  diffusion (ap, fh, rl)                   (3*float)\n')
outfile.write ('#  label type (ASL)            (imagekey!)  (integer)\n')
outfile.write ('#\n')
outfile.write ('# === IMAGE INFORMATION ==========================================================\n')
outfile.write ('#  sl ec  dyn ph ty    idx pix scan% rec size                (re)scale              window        angulation              offcentre        thick   gap   info      spacing     echo     dtime   ttime    diff  avg  flip    freq   RR-int  turbo delay b grad cont anis         diffusion       L.ty\n')
outfile.write ('\n')

#write frame data
End=False
index=0
while not End:
    outfile.write (form_str_len(find_xml_imageinfo1('Slice',index),3))
    outfile.write (form_str_len(find_xml_imageinfo1('Echo',index),4))
    outfile.write (form_str_len(find_xml_imageinfo1('Dynamic',index),5))
    outfile.write (form_str_len(find_xml_imageinfo1('Phase',index),3))
    type=find_xml_imageinfo1('Type',index)
    imagetypes = ['M','R','I','P','CR','T0','T1','T2', 'RHO','SPECTRO','DERIVED','ADC','RCBV','RCBF','MTT','TTP','FA','EADC','B0','DELAY','MAXRELENH','RELENH','MAXENH','WASHIN','WASHOUT','BREVENH','AREACURV','ANATOMIC','T_TEST','STD_DEVIATION','PERFUSION','T2_STAR','R2','R2_STAR','W','IP','OP','F','SPARE1','SPARE2']
    try: type=str(imagetypes.index(type))
    except: type='0'
    outfile.write (' '+type)
    seq=find_xml_imageinfo1('Sequence',index)
    sequences = ['IR','SE','FFE','DERIVED','PCA','UNSPECIFIED','SPECTRO','SI']
    try: seq=str(sequences.index(seq))
    except: sequence='5'
    outfile.write (form_str_len(seq,2))
    outfile.write (form_str_len(find_xml_imageinfo1('Index',index),6))
    outfile.write (form_str_len(find_xml_imageinfo2('Pixel Size',index),4))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Scan Percentage',index),0),6))
    outfile.write (form_str_len(find_xml_imageinfo2('Resolution X',index),5))
    outfile.write (form_str_len(find_xml_imageinfo2('Resolution Y',index),5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Rescale Intercept',index),5),12))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Rescale Slope',index),5),10))
    outfile.write (form_str_len(find_xml_imageinfo2('Scale Slope',index).replace("E","e"),13))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Window Center',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Window Width',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Angulation AP',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Angulation FH',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Angulation RL',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Offcenter AP',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Offcenter FH',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Offcenter RL',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Slice Thickness',index),3),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Slice Gap',index),3),7))
    disp_orient = find_xml_imageinfo2('Display Orientation',index)
    disp_orientations= ['NONE','RIGHT90','RIGHT180','LEFT90','VM','RIGHT90VM','RIGHT180VM','LEFT90VM']
    try: disp_orient=str(disp_orientations.index(disp_orient))
    except: disp_orient='0'
    outfile.write (form_str_len(disp_orient,2))
    sl_orient = find_xml_imageinfo2('Slice Orientation',index)
    sl_orient = sl_orient.lower()
    if sl_orient.find('tra')>=0: sl_orient='1'   # some issue here: what are the other possibilities
    elif sl_orient.find('sag')>=0: sl_orient='2' # some issue here: is that correct?
    elif sl_orient.find('cor')>=0: sl_orient='3' # some issue here: is that correct?
    else: sl_orient='0'
    outfile.write (form_str_len(sl_orient,2))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('fMRI Status Indication',index),0),2))
    type_ed_es = find_xml_imageinfo2('Image Type Ed Es',index)
    if type_ed_es.find('U')>=0: type_ed_es='2'
    elif type_ed_es.find('ED')>=0: type_ed_es='0'
    elif type_ed_es.find('ES')>=0: type_ed_es='1'
    else: type_ed_es='2'
    outfile.write (form_str_len(type_ed_es,2))
    dummy=str(find_xml_imageinfo2('Pixel Spacing',index))
    str1=dummy.split()[0]
    str2=dummy.split()[1]
    outfile.write (form_str_len(format_number(str1,3),7))
    outfile.write (form_str_len(format_number(str2,3),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Echo Time',index),2),7))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Dyn Scan Begin Time',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Trigger Time',index),2),9))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion B Factor',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('No Averages',index),0),4))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Image Flip Angle',index),2),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Cardiac Frequency',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Min RR Interval',index),0),5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Max RR Interval',index),0),5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('TURBO Factor',index),0),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Inversion Delay',index),1),6))
    outfile.write (form_str_len(format_number(find_xml_imageinfo1('BValue',index),0),3))
    outfile.write (form_str_len(format_number(find_xml_imageinfo1('Grad Orient',index),0),4))
    contr=find_xml_imageinfo2('Contrast Type',index)
    contrasttypes = ['DIFFUSION','FLOW_ENCODED','FLUID_ATTENUATED','PERFUSION','PROTON_DENSITY','STIR','TAGGING','T1','T2','T2_STAR','TOF','UNKNOWN','MIXED']
    try: contr=str(contrasttypes.index(contr))
    except: contr='11'
    outfile.write (form_str_len(contr,5))
    anis=find_xml_imageinfo2('Diffusion Anisotropy Type',index)
    if anis=='-': anis='0' # some issue here: what are the other possibilities
    outfile.write (form_str_len(anis,5))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion AP',index),3),8))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion FH',index),3),9))
    outfile.write (form_str_len(format_number(find_xml_imageinfo2('Diffusion RL',index),3),9))
    labletype=find_xml_imageinfo1('Label Type',index)
    if labletype=='-': labletype='1'
    elif labletype.find('L')>=0: labletype='1'
    elif labletype.find('l')>=0: labletype='1'
    else: labletype='0'
    outfile.write (form_str_len(labletype,3))
    outfile.write ('\n')
    index+=1
    try: test = find_xml_imageinfo1('Slice',index)
    except: End=True


outfile.write ('\n')
outfile.write ('# === END OF DATA DESCRIPTION FILE ===============================================\n')
outfile.close()
'''

'''
or this option from https://raw.githubusercontent.com/grlee77/nibabel/xmlrec/nibabel/xmlrec.py
'''

from copy import copy, deepcopy
import warnings
import xml.etree.ElementTree as ET

import numpy as np
from nibabel.parrec import one_line
from nibabel.parrec import PARRECImage, PARRECHeader


class XMLRECError(Exception):
    """Exception for XML/REC format related problems.

    To be raised whenever XML/REC is not happy, or we are not happy with
    XML/REC.
    """

# Dictionary of conversions from enumerated types to integer value for use in
# converting from XML enum names to PAR-style integers.
# The keys in enums_dict are the names of the enum keys used in XML files.
# The present conversions for strings to enumerated values was determined
# empirically via comparison of simultaneously exported .PAR and .xml files
# from a range of different scan types. Any enum labels that are not recognized
# will result in a warning encouraging the user to report the unkown case to
# the nibabel developers.
enums_dict = {
    'Label Type': {'CONTROL': 1, 'LABEL': 2, '-': 1},
    'Type': {'M': 0, 'R': 1, 'I': 2, 'P': 3, 'T1': 6, 'T2': 7, 'ADC': 11,
             'EADC': 17, 'B0': 18, 'PERFUSION': 30, 'F': 31, 'IP': 32,
             'FF': 34, 'R2': -1, 'R2_STAR': -1, 'T2_STAR': -1, 'W': -1,
             'STIFF': -1, 'WAVE': -1, 'SW_M': -1, 'SW_P': -1},
    'Sequence': {'IR': 0, 'SE': 1, 'FFE': 2, 'PCA': 4, 'UNSPECIFIED': 5,
                 'DERIVED': 7, 'B1': 9, 'MRE': 10},
    'Image Type Ed Es': {'U': 2},
    'Display Orientation': {'-': 0, 'NONE': 0},
    'Slice Orientation': {'Transversal': 1, 'Sagittal': 2, 'Coronal': 3},
    'Contrast Type': {'DIFFUSION': 0, 'FLOW_ENCODED': 1, 'PERFUSION': 3,
                      'PROTON_DENSITY': 4, 'TAGGING': 6, 'T1': 7, 'T2': 8,
                      'UNKNOWN': 11},
    'Diffusion Anisotropy Type': {'-': 0}}

# Dict for converting XML/REC types to appropriate python types
# could convert the Enumeration strings to int, but enums_dict is incomplete
# and the strings are more easily interpretable
xml_type_dict = {'Float': np.float32,
                 'Double': np.float64,
                 'Int16': np.int16,
                 'Int32': np.int32,
                 'UInt16': np.uint16,
                 'Enumeration': str,
                 'Boolean': bool,
                 'String': str,
                 'Date': str,
                 'Time': str}

# choose appropriate string length for use within the structured array dtype
str_length_dict = {'Enumeration': '|S32',
                   'String': '|S128',
                   'Date': '|S16',
                   'Time': '|S16'}

# for use with parrec.py, the Enumeration strings must be converted to ints
par_type_dict = copy(xml_type_dict)
par_type_dict['Enumeration'] = int

supported_xml_versions = ['PRIDE_V5']

# convert XML names to expected property names as used in nibabel.parrec
# Note: additional special cases are handled in general_info_xml_to_par()
general_info_XML_to_nibabel = {
    'Patient Name': 'patient_name',
    'Examination Name': 'exam_name',
    'Protocol Name': 'protocol_name',
    'Aquisition Number': 'acq_nr',
    'Reconstruction Number': 'recon_nr',
    'Scan Duration': 'scan_duration',
    'Max No Phases': 'max_cardiac_phases',
    'Max No Echoes': 'max_echoes',
    'Max No Slices': 'max_slices',
    'Max No Dynamics': 'max_dynamics',
    'Max No Mixes': 'max_mixes',
    'Patient Position': 'patient_position',
    'Preparation Direction': 'prep_direction',
    'Technique': 'tech',
    'Scan Mode': 'scan_mode',
    'Repetition Times': 'repetition_time',
    'Water Fat Shift': 'water_fat_shift',
    'Flow Compensation': 'flow_compensation',
    'Presaturation': 'presaturation',
    'Phase Encoding Velocity': 'phase_enc_velocity',
    'MTC': 'mtc',
    'SPIR': 'spir',
    'EPI factor': 'epi_factor',
    'Dynamic Scan': 'dyn_scan',
    'Diffusion': 'diffusion',
    'Diffusion Echo Time': 'diffusion_echo_time',
    'Max No B Values': 'max_diffusion_values',
    'Max No Gradient Orients': 'max_gradient_orient',
    'No Label Types': 'nr_label_types',
    'Series Data Type': 'series_type'}


def general_info_xml_to_par(xml_info):
    """Convert general_info from XML-style names to PAR-style names."""
    xml_info_init = xml_info
    xml_info = deepcopy(xml_info)
    general_info = {}
    for k in xml_info_init.keys():
        # convert all keys with a simple 1-1 name conversion
        if k in general_info_XML_to_nibabel:
            general_info[general_info_XML_to_nibabel[k]] = xml_info.pop(k)
    try:
        general_info['exam_date'] = '{} / {}'.format(
            xml_info.pop('Examination Date'),
            xml_info.pop('Examination Time'))
    except KeyError:
        pass

    try:
        general_info['angulation'] = np.asarray(
            [xml_info.pop('Angulation AP'),
             xml_info.pop('Angulation FH'),
             xml_info.pop('Angulation RL')])
    except KeyError:
        pass

    try:
        general_info['off_center'] = np.asarray(
            [xml_info.pop('Off Center AP'),
             xml_info.pop('Off Center FH'),
             xml_info.pop('Off Center RL')])
    except KeyError:
        pass

    try:
        general_info['fov'] = np.asarray(
            [xml_info.pop('FOV AP'),
             xml_info.pop('FOV FH'),
             xml_info.pop('FOV RL')])
    except KeyError:
        pass

    try:
        general_info['scan_resolution'] = np.asarray(
            [xml_info.pop('Scan Resolution X'),
             xml_info.pop('Scan Resolution Y')],
            dtype=int)
    except KeyError:
        pass

    # copy any excess keys not normally in the .PARREC general info
    # These will not be used by the PARREC code, but are kept for completeness
    general_info.update(xml_info)

    return general_info


# TODO: remove this function? It is currently unused, but may be useful for
#       testing roundtrip convesion.
def general_info_par_to_xml(par_info):
    """Convert general_info from PAR-style names to XML-style names."""
    general_info_nibabel_to_XML = {
        v: k for k, v in general_info_XML_to_nibabel.items()}
    par_info_init = par_info
    par_info = deepcopy(par_info)
    general_info = {}
    for k in par_info_init.keys():
        # convert all keys with a simple 1-1 name conversion
        if k in general_info_nibabel_to_XML:
            general_info[general_info_nibabel_to_XML[k]] = par_info.pop(k)
    try:
        tmp = par_info['exam_date'].split('/')
        general_info['Examination Date'] = tmp[0].strip()
        general_info['Examination Time'] = tmp[1].strip()
    except KeyError:
        pass

    try:
        general_info['Angulation AP'] = par_info['angulation'][0]
        general_info['Angulation FH'] = par_info['angulation'][1]
        general_info['Angulation RL'] = par_info['angulation'][2]
        par_info.pop('angulation')
    except KeyError:
        pass

    try:
        general_info['Off Center AP'] = par_info['off_center'][0]
        general_info['Off Center FH'] = par_info['off_center'][1]
        general_info['Off Center RL'] = par_info['off_center'][2]
        par_info.pop('off_center')
    except KeyError:
        pass

    try:
        general_info['FOV AP'] = par_info['fov'][0]
        general_info['FOV FH'] = par_info['fov'][1]
        general_info['FOV RL'] = par_info['fov'][2]
        par_info.pop('fov')
    except KeyError:
        pass

    try:
        general_info['Scan Resolution X'] = par_info['scan_resolution'][0]
        general_info['Scan Resolution Y'] = par_info['scan_resolution'][1]
        par_info.pop('scan_resolution')
    except KeyError:
        pass

    # copy any unrecognized keys as is.
    # known keys found in XML PRIDE_V5, but not in PAR v4.2 are:
    #    'Samples Per Pixel' and 'Image Planar Configuration'
    general_info.update(par_info)

    return general_info

# dictionary mapping fieldnames in the XML header to the corresponding names
# in a PAR V4.2 file
image_def_XML_to_PAR = {
    'Image Type Ed Es': 'image_type_ed_es',
    'No Averages': 'number of averages',
    'Max RR Interval': 'maximum RR-interval',
    'Type': 'image_type_mr',
    'Display Orientation': 'image_display_orientation',
    'Image Flip Angle': 'image_flip_angle',
    'Rescale Slope': 'rescale slope',
    'Label Type': 'label type',
    'fMRI Status Indication': 'fmri_status_indication',
    'TURBO Factor': 'TURBO factor',
    'Min RR Interval': 'minimum RR-interval',
    'Scale Slope': 'scale slope',
    'Inversion Delay': 'Inversion delay',
    'Window Width': 'window width',
    'Sequence': 'scanning sequence',
    'Diffusion Anisotropy Type': 'diffusion anisotropy type',
    'Index': 'index in REC file',
    'Rescale Intercept': 'rescale intercept',
    'Diffusion B Factor': 'diffusion_b_factor',
    'Trigger Time': 'trigger_time',
    'Echo': 'echo number',
    'Echo Time': 'echo_time',
    'Pixel Spacing': 'pixel spacing',
    'Slice Gap': 'slice gap',
    'Dyn Scan Begin Time': 'dyn_scan_begin_time',
    'Window Center': 'window center',
    'Contrast Type': 'contrast type',
    'Slice': 'slice number',
    'BValue': 'diffusion b value number',
    'Scan Percentage': 'scan percentage',
    'Phase': 'cardiac phase number',
    'Slice Thickness': 'slice thickness',
    'Slice Orientation': 'slice orientation',
    'Dynamic': 'dynamic scan number',
    'Pixel Size': 'image pixel size',
    'Grad Orient': 'gradient orientation number',
    'Cardiac Frequency': 'cardiac frequency'}

# copy of enums_dict but with key names converted to their PAR equivalents
enums_dict_PAR = {image_def_XML_to_PAR[k]: v for k, v in enums_dict.items()}


# TODO?: The following values have different names in the XML vs. PAR header
rename_XML_to_PAR = {
    'HFS': 'Head First Supine',
    'LR': 'Left-Right',
    'RL': 'Right-Left',
    'AP': 'Anterior-Posterior',
    'PA': 'Posterior-Anterior',
    'N': 0,
    'Y': 1,
}


def _process_gen_dict_XML(xml_root):
    """Read the general_info from an XML file.

    This is the equivalent of _process_gen_dict() for .PAR files
    """
    info = xml_root.find('Series_Info')
    if info is None:
        raise RuntimeError("No 'Series_Info' found in the XML file")
    general_info = {}
    for e in info:
        a = e.attrib
        if 'Name' in a:
            entry_type = xml_type_dict[a['Type']]
            if entry_type in ['S16', 'S32', 'S128']:
                entry_type = str
            if 'ArraySize' in a:
                val = [entry_type(i) for i in e.text.strip().split()]
            else:
                val = entry_type(e.text)
            general_info[a['Name']] = val
    return general_info


def _get_image_def_attributes(xml_root, dtype_format='xml'):
    """Get names and dtypes for all attributes defined for each image.

    called by _process_image_lines_xml

    Paramters
    ---------
    xml_root :
        TODO
    dtype_format : {'xml', 'par'}
        If 'par'', XML paramter names and dtypes are converted to their PAR
        equivalents.

    Returns
    -------
    key_attributes : list of tuples
        The attributes that are used when sorting data from the REC file.
    other_attributes : list of tuples
        Additional attributes that are not considered when sorting.
    """
    image_defs_array = xml_root.find('Image_Array')
    if image_defs_array is None:
        raise XMLRECError("No 'Image_Array' found in the XML file")

    # can get all of the fields from the first entry
    first_def = image_defs_array[0]

    # Key element contains attributes corresponding to image keys
    # e.g. (Slice, Echo, Dynamic, ...) that can be used for sorting the images.
    img_keys = first_def.find('Key')
    if img_keys is None:
        raise XMLRECError(
            "Expected to find a Key attribute for each element in Image_Array")
    if not np.all(['Name' in k.attrib for k in img_keys]):
        raise XMLRECError("Expected each Key attribute to have a Name")

    def _get_type(name, type_dict, str_length_dict=str_length_dict):
        t = type_dict[name]
        if t is str:  # convert from str to a specific length such as |S32
            t = str_length_dict[name]
        return t

    dtype_format = dtype_format.lower()
    if dtype_format == 'xml':
        # xml_type_dict keeps enums as their string representation
        key_attributes = [
            (k.get('Name'), _get_type(k.get('Type'), xml_type_dict))
            for k in img_keys]
    elif dtype_format == 'par':
        # par_type_dict converts enums to int as used in PAR/REC
        key_attributes = [
            (image_def_XML_to_PAR[k.get('Name')],
             _get_type(k.get('Type'), par_type_dict))
            for k in img_keys]
    else:
        raise XMLRECError("dtype_format must be 'par' or 'xml'")

    # Process other attributes that are not considered image keys
    other_attributes = []
    for element in first_def:
        a = element.attrib
        if 'Name' in a:
            # if a['Type'] == 'Enumeration':
            #     enum_type = a['EnumType']
            #     print("enum_type = {}".format(enum_type))
            name = a['Name']
            if dtype_format == 'xml':
                entry_type = _get_type(a['Type'], xml_type_dict)
            else:
                entry_type = _get_type(a['Type'], par_type_dict)
                if name in image_def_XML_to_PAR:
                    name = image_def_XML_to_PAR[name]
            if 'ArraySize' in a:
                # handle vector entries (e.g. 'Pixel Size' is length 2)
                entry = (name, entry_type, int(a['ArraySize']))
            else:
                entry = (name, entry_type)
            other_attributes.append(entry)

    return key_attributes, other_attributes


# these keys are elements of a multi-valued key in the PAR/REC image_defs
composite_PAR_keys = ['Diffusion AP', 'Diffusion FH', 'Diffusion RL',
                      'Angulation AP', 'Angulation FH', 'Angulation RL',
                      'Offcenter AP', 'Offcenter FH', 'Offcenter RL',
                      'Resolution X', 'Resolution Y']


def _composite_attributes_xml_to_par(other_attributes):
    """utility used in conversion from XML-style to PAR-style image_defs.

    called by _process_image_lines_xml
    """
    if ('Diffusion AP', np.float32) in other_attributes:
        other_attributes.remove(('Diffusion AP', np.float32))
        other_attributes.remove(('Diffusion FH', np.float32))
        other_attributes.remove(('Diffusion RL', np.float32))
        other_attributes.append(('diffusion', float, (3, )))

    if ('Angulation AP', np.float64) in other_attributes:
        other_attributes.remove(('Angulation AP', np.float64))
        other_attributes.remove(('Angulation FH', np.float64))
        other_attributes.remove(('Angulation RL', np.float64))
        other_attributes.append(('image angulation', float, (3, )))

    if ('Offcenter AP', np.float64) in other_attributes:
        other_attributes.remove(('Offcenter AP', np.float64))
        other_attributes.remove(('Offcenter FH', np.float64))
        other_attributes.remove(('Offcenter RL', np.float64))
        other_attributes.append(('image offcentre', float, (3, )))

    if ('Resolution X', np.uint16) in other_attributes:
        other_attributes.remove(('Resolution X', np.uint16))
        other_attributes.remove(('Resolution Y', np.uint16))
        other_attributes.append(('recon resolution', int, (2, )))

    return other_attributes


# TODO: remove? this one is currently unused, but perhaps useful for testing
def _composite_attributes_par_to_xml(other_attributes):
    if ('diffusion', float, (3, )) in other_attributes:
        other_attributes.append(('Diffusion AP', np.float32))
        other_attributes.append(('Diffusion FH', np.float32))
        other_attributes.append(('Diffusion RL', np.float32))
        other_attributes.remove(('diffusion', float, (3, )))

    if ('image angulation', float, (3, )) in other_attributes:
        other_attributes.append(('Angulation AP', np.float64))
        other_attributes.append(('Angulation FH', np.float64))
        other_attributes.append(('Angulation RL', np.float64))
        other_attributes.remove(('image angulation', float, (3, )))

    if ('image offcentre', float, (3, )) in other_attributes:
        other_attributes.append(('Offcenter AP', np.float64))
        other_attributes.append(('Offcenter FH', np.float64))
        other_attributes.append(('Offcenter RL', np.float64))
        other_attributes.remove(('image offcentre', float, (3, )))

    if ('recon resolution', int, (2, )) in other_attributes:
        other_attributes.append(('Resolution X', np.uint16))
        other_attributes.append(('Resolution Y', np.uint16))
        other_attributes.remove(('recon resolution', int, (2, )))
    return other_attributes


def _get_composite_key_index(key):
    """utility used in conversion from XML-style to PAR-style image_defs.

    called by _process_image_lines_xml
    """
    if 'Diffusion' in key:
        name = 'diffusion'
    elif 'Angulation' in key:
        name = 'image angulation'
    elif 'Offcenter' in key:
        name = 'image offcentre'
    elif 'Resolution' in key:
        name = 'recon resolution'
    else:
        raise ValueError("unrecognized composite element name: {}".format(key))

    if key in ['Diffusion AP', 'Angulation AP', 'Offcenter AP',
               'Resolution X']:
        index = 0
    elif key in ['Diffusion FH', 'Angulation FH', 'Offcenter FH',
                 'Resolution Y']:
        index = 1
    elif key in ['Diffusion RL', 'Angulation RL', 'Offcenter RL']:
        index = 2
    else:
        raise ValueError("unrecognized composite element name: {}".format(key))
    return (name, index)


def _process_image_lines_xml(xml_root, dtype_format='xml'):
    """Build image_defs by parsing the XML file.

    Parameters
    ----------
    xml_root :
        TODO
    dtype_format : {'xml', 'par'}
        If 'par'', XML paramter names and dtypes are converted to their PAR file
        equivalents.
    """
    image_defs_array = xml_root.find('Image_Array')
    if image_defs_array is None:
        raise RuntimeError("No 'Image_Array' found in the XML file")

    key_attributes, other_attributes = _get_image_def_attributes(xml_root, dtype_format=dtype_format)

    image_def_dtd = key_attributes + other_attributes
    # dtype dict based on the XML attribute names
    dtype_dict = {a[0]: a[1] for a in image_def_dtd}

    if dtype_format == 'par':
        # image_defs based on conversion of types in composite_PAR_keys
        image_def_dtd = _composite_attributes_xml_to_par(image_def_dtd)

    def _get_val(entry_dtype, text):
        if entry_dtype == '|S16':
            val = text[:16]
        elif entry_dtype == '|S32':
            val = text[:32]
        elif entry_dtype == '|S128':
            val = text[:128]
        else:
            val = entry_dtype(text)
        return val

    image_defs = np.zeros(len(image_defs_array), dtype=image_def_dtd)
    already_warned = []
    for i, image_def in enumerate(image_defs_array):

        if image_def.find('Key') != image_def[0]:
            raise RuntimeError("Expected first element of image_def to be Key")

        key_def = image_def[0]
        for key in key_def:
            name = key.get('Name')
            if dtype_format == 'par' and name in image_def_XML_to_PAR:
                name = image_def_XML_to_PAR[name]
            if dtype_format == 'par' and name in enums_dict_PAR:
                # string -> int
                if key.text in enums_dict_PAR[name]:
                    val = enums_dict_PAR[name][key.text]
                else:
                    if (name, key.text) not in already_warned:
                        warnings.warn(
                            ("Unknown enumerated value for {} with name {}. "
                             "Setting the value to -1.  Please contact the "
                             "nibabel developers about adding support for "
                             "this to the XML/REC reader.").format(
                                name, key.text))
                        val = -1
                        # avoid repeated warnings for this enum
                        already_warned.append((name, key.text))
            else:
                val = key.text
            image_defs[name][i] = _get_val(dtype_dict[name], val)

        # for all image properties we know about
        for element in image_def[1:]:
            a = element.attrib
            text = element.text
            if 'Name' in a:
                name = a['Name']
                if dtype_format == 'par' and name in image_def_XML_to_PAR:
                    name = image_def_XML_to_PAR[name]
                    # composite_PAR_keys
                entry_dtype = dtype_dict[name]
                if 'ArraySize' in a:
                    val = [entry_dtype(i) for i in text.strip().split()]
                else:
                    if dtype_format == 'par' and name in enums_dict_PAR:
                        # string -> int
                        if text in enums_dict_PAR[name]:
                            val = enums_dict_PAR[name][text]
                        else:
                            if (name, text) not in already_warned:
                                warnings.warn(
                                    ("Unknown enumerated value for {} with "
                                     "name {}. Setting the value to -1.  "
                                     "Please contact the nibabel developers "
                                     "about adding support for this to the "
                                     "XML/REC reader.").format(name, text))
                                val = -1
                                # avoid repeated warnings for this enum
                                already_warned.append((name, text))
                    else:
                        val = _get_val(entry_dtype, text)
                if dtype_format == 'par' and name in composite_PAR_keys:
                    # conversion of types in composite_PAR_keys
                    name, vec_index = _get_composite_key_index(name)
                    image_defs[name][i][vec_index] = val
                else:
                    image_defs[name][i] = val
    return image_defs


def parse_XML_header(fobj, dtype_format='xml'):
    """Parse a XML header and aggregate all information into useful containers.

    Parameters
    ----------
    fobj : file-object or str
        The XML header file object or file name.
    dtype_format : {'xml', 'par'}
        If 'par' the image_defs will be converted to a format matching that
        found in PARRECHeader.

    Returns
    -------
    general_info : dict
        Contains all "General Information" from the header file
    image_info : ndarray
        Structured array with fields giving all "Image information" in the
        header
    """
    # single pass through the header
    tree = ET.parse(fobj)
    root = tree.getroot()

    # _split_header() equivalent

    version = root.tag  # e.g. PRIDE_V5
    if version not in supported_xml_versions:
        warnings.warn(one_line(
            """XML version '{0}' is currently not supported.  Only PRIDE_V5 XML
            files have been tested. --making an attempt to read nevertheless.
            Please email the NiBabel mailing list, if you are interested in
            adding support for this version.
            """.format(version)))
    try:
        general_info = _process_gen_dict_XML(root)
        image_defs = _process_image_lines_xml(
            root, dtype_format=dtype_format)
    except ET.ParseError:
            raise XMLRECError(
                "A ParseError occured in the ElementTree library while "
                "reading the XML file. This may be due to a truncated XML "
                "file.")

    return general_info, image_defs


class XMLRECHeader(PARRECHeader):

    @classmethod
    def from_fileobj(klass, fileobj, permit_truncated=False,
                     strict_sort=False):
        info, image_defs = parse_XML_header(fileobj, dtype_format='par')
        # convert to PAR/REC format general_info
        info = general_info_xml_to_par(info)
        return klass(info, image_defs, permit_truncated, strict_sort)

    @classmethod
    def from_header(klass, header=None):
        if header is None:
            raise XMLRECError('Cannot create XMLRECHeader from air.')
        if type(header) == klass:
            return header.copy()
        raise XMLRECError('Cannot create XMLREC header from '
                          'non-XMLREC header.')

    def copy(self):
        return XMLRECHeader(deepcopy(self.general_info),
                            self.image_defs.copy(),
                            self.permit_truncated,
                            self.strict_sort)

class XMLRECImage(PARRECImage):
    """XML/REC image"""
    header_class = XMLRECHeader
    valid_exts = ('.rec', '.xml')
    files_types = (('image', '.rec'), ('header', '.xml'))

load = XMLRECImage.load