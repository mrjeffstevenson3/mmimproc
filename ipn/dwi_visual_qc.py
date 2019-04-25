
# coding: utf-8

# In[1]:


# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
import pandas as pd
import numpy as np
from mmimproc.io.mixed import df2h5, h52df, get_h5_keys
from mmimproc.utils import *
from mmimproc.projects.genz.file_names import project, Optsd
import qgrid
qgrid.enable
import ipywidgets as widgets
fs = Path(getnetworkdataroot())
opts = Optsd()
input_selkey = widgets.Dropdown(options=get_h5_keys(opts.info_fname, key='auto_qc'), disabled=False,
    description='Subject DWI to qc:',)
input_selkey.layout.width = '600px'
input_selkey


# In[2]:


all_dwi_auto_qc = h52df(opts.info_fname, input_selkey.value)
#all_dwi_auto_qc


# In[3]:


pick = {'subj': input_selkey.value.split('/')[1], 'session': input_selkey.value.split('/')[2], }
all_dwi_auto_qc = h52df(opts.info_fname, input_selkey.value)
pick['dwi_fname'] = all_dwi_auto_qc.loc[0, 'dwi_fname']
fslv_names = ' '.join([x + ' -b 1,200' for x in all_dwi_auto_qc.loc[0, ['dwi_fname', 'topup_fname', 'topdn_fname']].values])
with WorkingContext(str(Path(all_dwi_auto_qc.loc[0, 'dwi_fname']).parent)):
    with open('fslview_cmd.sh', 'w') as f:
        f.write('fslview ' + fslv_names + ' &\n')
all_dwi_auto_qc['itopup_isnum'] = all_dwi_auto_qc['itopup'] == np.number
# limit to only active rows with mask
all_dwi_auto_qc['itopup_isnum'] = all_dwi_auto_qc['itopup'].str.isnumeric()
all_dwi_auto_qc['itopdn_isnum'] = all_dwi_auto_qc['itopdn'].str.isnumeric()
all_dwi_auto_qc.loc[all_dwi_auto_qc.itopup_isnum, 'itopup_visqc'] = True
all_dwi_auto_qc.loc[all_dwi_auto_qc.itopdn_isnum, 'itopdn_visqc'] = True
all_dwi_auto_qc.itopup_visqc.fillna(False, inplace=True)
all_dwi_auto_qc.itopdn_visqc.fillna(False, inplace=True)
all_dwi_auto_qc.loc[:, 'dwi_visqc'] = True
with WorkingContext(str(Path(pick['dwi_fname']).parent/'qc')):  
    topup_gvolspng = open('{subj}_{session}_topup8b0-qc_good_plot.png'.format(**pick), 'rb').read()
    topup_bvolspng = open('{subj}_{session}_topup8b0-qc_bad_plot.png'.format(**pick), 'rb').read()
    topdn_gvolspng = open('{subj}_{session}_topdn7b0-qc_good_plot.png'.format(**pick), 'rb').read()
    topdn_bvolspng = open('{subj}_{session}_topdn7b0-qc_bad_plot.png'.format(**pick), 'rb').read()
    dwi800_gvolspng = open('{subj}_{session}_b800-qc_good_plot.png'.format(**pick), 'rb').read()
    dwi800_bvolspng= open('{subj}_{session}_b800-qc_bad_plot.png'.format(**pick), 'rb').read()
    dwi2000_gvolspng = open('{subj}_{session}_b2000-qc_good_plot.png'.format(**pick), 'rb').read()
    dwi2000_bvolspng= open('{subj}_{session}_b2000-qc_bad_plot.png'.format(**pick), 'rb').read()

dwicols = [u'bvals', u'auto_dwi_vol_idx', u'auto_dwi_qc', 'dwi_visqc', u'x_bvec', u'y_bvec', u'z_bvec']
topudcols = [u'itopup', u'alltopup_idx', u'topup_qc', 'itopup_visqc', u'itopdn', u'topdn_qc', 'itopdn_visqc',]
dwi_auto_qc = all_dwi_auto_qc[dwicols]
topud_auto_qc = all_dwi_auto_qc[topudcols]
dwi_w = qgrid.show_grid(dwi_auto_qc, show_toolbar=False)
topupdn_w = qgrid.show_grid(topud_auto_qc, show_toolbar=False)


# In[5]:


items = [widgets.Image(description='dwi b2000 bad vols', value=dwi2000_bvolspng,    format='png',    width=500,    height=600),
        widgets.Image(description='dwi b2000 good vols', value=dwi2000_gvolspng,    format='png',    width=500,    height=600),]
#items_layout = [widgets.Layout(flex-basis='50%', ), widgets.Layout(flex-basis='50%', widgets.Layout(flex-basis='100%',)]
box_layout = widgets.Layout(display='flex', align_items='stretch', border='solid', width='100%')
top_box = widgets.HBox(children=items)
bottom_box = widgets.HBox(children=[dwi_w])
dwi_box = widgets.Box([top_box, bottom_box], layout=box_layout)
dwi_box


# In[10]:


items = [widgets.Image(description='topup bad vols', value=topup_bvolspng,    format='png',    width=400,    height=600),
        widgets.Image(description='topup good vols', value=topup_gvolspng,    format='png',    width=400,    height=600),
        widgets.Image(description='topdn bad vols', value=topdn_bvolspng,    format='png',    width=400,    height=600),
        widgets.Image(description='topdn good vols', value=topdn_gvolspng,    format='png',    width=400,    height=600),
]
box_layout = widgets.Layout(display='flex',
                    flex_flow='row',
                    align_items='stretch',
                    border='solid',
                    width='100%')
topupdn_box = widgets.Box(children=items+[topupdn_w], layout=box_layout)
topupdn_box


# In[13]:


topupdn_w.get_changed_df()


# In[14]:


dwi_w.get_changed_df()


# In[11]:


all_dwi_visqc = pd.concat([dwi_w.get_changed_df(), topupdn_w.get_changed_df()], axis=1)
df2h5(all_dwi_visqc, opts.info_fname, input_selkey.value.replace('auto_qc', 'vis_qc'))

