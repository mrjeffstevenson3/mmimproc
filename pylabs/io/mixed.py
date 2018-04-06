import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import pandas as pd
import numpy as np
import json, datetime, dateutil.parser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from pylabs.conversion.parrec2nii_convert import BrainOpts
from pylabs.utils import getnetworkdataroot, WorkingContext
fs = Path(getnetworkdataroot())

"""
Tools to save a list of dictionaries with pandas Dataframes in them to a 
json file, and load them back.
And convert a pdf to text.
"""

opts = BrainOpts()

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
            for k,v in {'GABA+/H2O  : ': '', ' inst. units.': '', 'GABA+/H 2 O  : ': '', }.iteritems():
                line = line.replace(k,v)
            gaba_val = float(line)
        if 'GABA+/Cr i.r.' in line:
            for k,v in {'GABA+/Cr i.r.: ': '',}.iteritems():
                line = line.replace(k,v)
            gabaovercr = float(line)
        if 'FitErr (H/Cr)   : ' in line:
            for k, v in {'FitErr (H/Cr)   : ': '', '%': '', }.iteritems():
                line = line.replace(k, v)
            fit_err = float(line.split(',')[0])
            fit_perc = float(line.split(',')[1])
    if gaba_val == None:
        raise ValueError('could not find a gaba value in '+str(fitpdf))
    return gaba_val, gabaovercr, fit_err, fit_perc

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

def df2h5(df, h5_fname, key, append=False):
    h5_fname = Path(h5_fname)
    if not h5_fname.is_file():
        print('new hdf file '+str(h5_fname)+' is being created since no existing file found.')
    with pd.HDFStore(str(h5_fname)) as storeh5:
            if append:
                storeh5.append(key, df.applymap(str), format='t')
            else:
                storeh5.put(key, df.applymap(str), format='t')
    return

def h52df(h5_fname, key):
    h5_fname = Path(h5_fname)
    if not h5_fname.is_file():
        raise ValueError(str(h5_fname)+' h5 file not found.')
    with pd.HDFStore(str(h5_fname)) as storeh5:
        df = storeh5.select(key)
        df = df.apply(pd.to_numeric, errors='ignore')
    return df

def get_h5_keys(h5_fname, key=None):
    h5_fname = Path(h5_fname)
    if not h5_fname.is_file():
        raise ValueError(str(h5_fname)+' h5 file not found.')
    with pd.HDFStore(str(h5_fname)) as storeh5:
        h5keys = storeh5.keys()
    if not key is None:
        match_key = [k for k in h5keys if key in k]
        h5keys = match_key
    return h5keys

def getTRfromh5(h5_fname, subject, session, modality, scan):
    h5_fname = Path(h5_fname)
    if not h5_fname.is_file():
        raise ValueError(str(h5_fname)+' h5 file not found.')
    with pd.HDFStore(str(h5_fname)) as storeh5:
        df = storeh5.select('/'+'/'.join([subject, session, 'convert_info']))
        tr = df.loc[[modality, scan], 'tr']
    return np.fromstring(tr.values[0].translate(None, '[]'), sep=' ')


def gen_df_extract(key, var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            #print k, v, isinstance(v, dict)
            if k == key:
                yield v
            if isinstance(v, dict) or isinstance(v, pd.DataFrame) or isinstance(v, pd.Series):
                #print('found sub item')
                for result in gen_df_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_df_extract(key, d):
                        yield result

def backup_source_dirs(project, subjects):
    from pylabs.conversion.brain_convert import img_conv
    if project not in img_conv:
        raise ValueError(project+" not in img_conv Panel. Please check")
    setattr(opts, 'proj', project)
    scans = img_conv[project]
    scans.dropna(axis=1, how='all', inplace=True)
    if not Path(fs / opts.proj / 'tesla_backups').is_dir():
        Path(fs / opts.proj / 'tesla_backups').mkdir(parents=True)
    with WorkingContext(str(fs / opts.proj)):
        for subject in subjects:
            setattr(opts, 'subj', subject)
            if all(list(gen_df_extract('multisession', scans))) != 0:
                setattr(opts, 'multisession', np.unique(list(gen_df_extract('multisession', scans))))
                for s in opts.multisession:
                    ses = 'ses-' + str(s)
                    if Path('tesla_backups', subject+'_'+ses+'_source_parrec').is_symlink():
                        Path('tesla_backups',subject+'_'+ses+'_source_parrec').unlink()
                    if Path(subject, ses, 'source_parrec').is_dir():
                        Path('tesla_backups', subject + '_' + ses + '_source_parrec').symlink_to(Path('../', subject, ses, 'source_parrec'), target_is_directory=True)
                    else:
                        print('did not find source_parrec directory for backup for '+subject+' in '+ses)

                    if Path('tesla_backups', subject+'_'+ses+'_source_dicom').is_symlink():
                        Path('tesla_backups',subject+'_'+ses+'_source_dicom').unlink()
                    if Path(subject, ses, 'source_dicom').is_dir():
                        Path('tesla_backups', subject + '_' + ses + '_source_dicom').symlink_to(Path('../', subject, ses, 'source_dicom'), target_is_directory=True)
                    else:
                        print('did not find source_dicom directory for backup for '+subject+' in '+ses)

                    if Path('tesla_backups', subject+'_'+ses+'_source_sparsdat').is_symlink():
                        Path('tesla_backups',subject+'_'+ses+'_source_sparsdat').unlink()
                    if Path(subject, ses, 'source_sparsdat').is_dir():
                        Path('tesla_backups', subject + '_' + ses + '_source_sparsdat').symlink_to(Path('../', subject, ses, 'source_sparsdat'), target_is_directory=True)
                    else:
                        print('did not find source_sparsdat directory for backup for '+subject+' in '+ses)

                    if Path('tesla_backups', subject+'_'+ses+'_phantom_parrec').is_symlink():
                        Path('tesla_backups',subject+'_'+ses+'_phantom_parrec').unlink()
                    if Path(subject, ses, 'phantom_parrec').is_dir():
                        Path('tesla_backups', subject + '_' + ses + '_phantom_parrec').symlink_to(Path('../', subject, ses, 'phantom_parrec'), target_is_directory=True)
                    else:
                        print('did not find phantom_parrec directory for backup for '+subject+' in '+ses)




