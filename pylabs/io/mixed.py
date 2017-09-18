import json, pandas, datetime, dateutil.parser
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
        item['data'] = pandas.read_json(item['data'], orient='split')
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
            gaba_val = line.split(' ')[3]
    if gaba_val == None:
        raise ValueError('could not fing a gaba valur in '+str(fitpdf))
    return float(gaba_val)
