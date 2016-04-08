#!/usr/bin/env python
"""
Read Philips Examcard files.

Jasper J.F. van den Bosch <jasperb@uw.edu>
"""
from xml.dom.minidom import parse
import struct, pprint
import niprov.comparing
from niprov.xmllib import *
from niprov.basefile import BaseFile

fields = {'field-of-view':'EX_GEO_fov',
          'epi-factor':'IF_epi_factor',
          'magnetization-transfer-contrast':'EX_MTC_enable',
          'echo-time':'EX_ACQ_first_echo_time',
          'repetition-time':'EX_ACQ_se_rep_time',
          'flip-angle':'EX_ACQ_flip_angle',
          'duration':'IF_str_total_scan_time',
          'subject-position':'EX_GEO_patient_position',
          'water-fat-shift':'EX_ACQ_water_fat_shift',
          'subject-orientation':'EX_GEO_patient_orientation'}

def load(fpath):
    obj = PylabsExamCardFile(fpath)
    obj.inspect()
    return obj.provenance['examcard']


class PylabsExamCardFile(BaseFile):

    def __init__(self, location, **kwargs):
        super(PylabsExamCardFile, self).__init__(location, **kwargs)

    def inspect(self):
        provenance = super(PylabsExamCardFile, self).inspect()
        dom = parse(provenance['path'])
        soapBody = dom.getElementsByTagName("SOAP-ENV:Body")[0]
        examCardItemNodes = getNonTextChildNodes(soapBody)
        examCardNode = soapBody.getElementsByTagName("a1:ExamCard")[0]
        nameNode = examCardNode.getElementsByTagName("name")[0]
        exam = {}
        exam['name'] = getTextContent(nameNode)
        scanNodes = getElementsByTagNameWithoutPrefix(soapBody, "ScanProcedure")
        exam['scans'] = []
        for scanNode in scanNodes:
            scan = {}
            scan['name'] = getTextContentForFirstElementByTag(scanNode, "name")
            ref = getRefForFirstElementByTag(scanNode, "parameterData")
            refNode = getElementById(soapBody, ref)
            b64content = getTextContent(refNode)
            scan['parameters'] = decodeParameters(b64content)
            exam['scans'].append(scan)
        provenance['examcard'] = exam

    def getScan(self, scanname):
        scanname = scanname.split(' ')[1]
        scannames = [s['name'] for s in self.provenance['examcard']['scans']]
        if scanname not in scannames:
            msg = "Can't find scan '{}' in {}"
            raise ValueError(msg.format(scanname, pprint.pformat(scannames)))
        scanindex = scannames.index(scanname)
        scanDict = self.provenance['examcard']['scans'][scanindex]
        scanProvenance = {'examcard-scan':scanDict}
        for field, ecname in fields.items():
            scanProvenance[field] = scanDict['parameters'][ecname]
        return PylabsExamCardScan(str(self.location), 
            provenance=scanProvenance)

    def compareCorrespondingScan(self, other):
        assert 'protocol' in other.provenance
        scan = self.getScan(other.provenance['protocol'])
        return niprov.comparing.compare(other, scan)


class PylabsExamCardScan(BaseFile):

    def __init__(self, location, **kwargs):
        super(PylabsExamCardScan, self).__init__(location, **kwargs)

def decodeParameters(b64content):
    params = {}
    dtypes = {0:float,1:int,2:str,4:int}
    dtypeLengths = {float:4,int:4,str:81} # 4 is an enum, use int for now
    bytes = b64content.decode('base64')
    nparams = readValue(bytes, 28)
    assert nparams < 1000
    for p in range(nparams):
        pstart = 32 + 50 * p
        paramName = readValue(bytes, pstart, str, 32)
        dtypeNumber = readValue(bytes, pstart+32+2)
        nvalues = readValue(bytes, pstart+32+6)
        assert nvalues < 10000
        enumDistance = readValue(bytes, pstart+32+10)
        valDistance = readValue(bytes, pstart+32+14)
        dtype = dtypes[dtypeNumber]
        firstValAddress = pstart + 32 + valDistance + 14
        valueLength = dtypeLengths[dtype]
        values = []
        for v in range(nvalues):
            valueAddress = firstValAddress + v * valueLength
            value = readValue(bytes, valueAddress, dtype, valueLength)
            values.append(value)
        if len(values) > 1:
            params[paramName] = values
        elif len(values) == 1:
            params[paramName] = values[0]
    return params

def readValue(bytes, start, dtype=int, length=4):
    symbols = {int:'L',float:'f'}
    chunk = bytes[start:start+length]
    if dtype in symbols:
        return struct.unpack('<{0}'.format(symbols[dtype]), chunk)[0]
    elif dtype == str:
        return chunk.split('\x00')[0]
    else:
        return chunk

"""
SingleScan > 
    scanProcedure > name
    scanProperties
"""



