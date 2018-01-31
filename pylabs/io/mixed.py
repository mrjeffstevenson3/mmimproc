from pathlib import *
import pandas as pd
import json, datetime, dateutil.parser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
"""
Tools to save a list of dictionaries with pandas Dataframes in them to a 
json file, and load them back.
And convert a pdf to text.
"""

def _copy(self, target):
    import shutil
    assert self.is_file()
    shutil.copy(str(self), str(target))  # str() only there for Python < (3, 6)

Path.copy = _copy


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json(orient='split')
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def listOfDictsToJson(data, fpath):
    with open(fpath, 'w') as fp:
        json.dump(data, fp, cls=JSONEncoder)

def listOfDictsFromJson(fpath):
    toplevel = json.load(open(fpath))
    assert isinstance(toplevel, list)
    outlist = []
    for item in toplevel:
        item['data'] = pd.read_json(item['data'], orient='split')
        item['date'] = dateutil.parser.parse(item['date']).date()
        outlist.append(item)
    return outlist


def pdftotxt(fpath):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(str(fpath), 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text

# make get_gaba function that uses pdftotext to return gaba value with test range 0.3 to 2.0
def getgabavalue(fitpdf):
    gaba_val = None
    if not fitpdf.is_file():
        raise ValueError('file not found.')
    pdf_text = pdftotxt(str(fitpdf))
    for line in pdf_text.splitlines():
        if 'inst. units.' in line:
            gaba_val = line.split()[4]
    if gaba_val == None:
        raise ValueError('could not find a gaba value in '+str(fitpdf))
    return float(gaba_val)

def conv_df2h5(df, h5_fname, append=True):
    """
    This function is used by brain convert routine to store scan parameter info captured during conversion.
    :param df:      multi index dataframe level0=subject id, level1=session, level2= convert info by anat and file
    :param h5_fname: name of .h5 file. usually all_<project name>_info.h5 in project directory
    :param append: safe is True but False will ovewrite the session with new info. use this for new or reworked data.
    :return:
    """
    if not df.index.nlevels > 2:
        raise ValueError('Dataframe has fewer than 3 levels. must have at least subject, session, and modality levels')
    subject2store = [x for x in df.index.get_level_values(0).unique() if 'sub-' in x]
    sessions2store = [x for x in df.index.get_level_values(1).unique() if 'ses-' in x]
    if not len(subject2store) == len(df.index.get_level_values(0).unique()):
        raise ValueError('Not all subjects conform to BIDS conventions and begin with sub-. please check dataframe level 0.')
    if not len(sessions2store) == len(df.index.get_level_values(1).unique()):
        raise ValueError('Not all sessions conform to BIDS conventions and begin with ses-. please check dataframe level 1.')

    with pd.HDFStore(str(Path(h5_fname))) as storeh5:
        for subj in subject2store:
            if not list(df.loc[subj].index.get_level_values(0).unique()):
                raise ValueError('stopping now because df missing level 1 i.e. session for '+subj )
            for ses in df.loc[subj].index.get_level_values(0).unique():
                if append:
                    storeh5.append(subj+'/'+ses+'/convert_info', df.loc[subj,ses].applymap(str), format='t')
                else:
                    storeh5.put(subj + '/' + ses + '/convert_info', df.loc[subj,ses].applymap(str), format='t')
    return

