#!/usr/bin/env python
"""
Read Philips Examcard files.

Jasper J.F. van den Bosch <jasperb@uw.edu>
"""
from xml.dom.minidom import parse
import struct
from niprov.xmllib import *
from niprov.basefile import BaseFile

def load(fpath):
    obj = PylabsExamCardFile(fpath)
    obj.inspect()
    return obj.provenance


class PylabsExamCardFile(BaseFile):

    def __init__(self, location, **kwargs):
        super(PylabsExamCardFile, self).__init__(location, **kwargs)
        self.libs = self.dependencies.getLibraries()

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
        provenance.update(exam)

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



