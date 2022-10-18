#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import textgrids #import textgrids
import pandas as pd
import numpy as np
import shutil


# In[2]:


tg_dir = "/Users/masato/Box/cloze_experiments/filter/data_pilot/tg_corrected"


# In[3]:


filenames = [os.path.splitext(fn)[0] for fn in os.listdir(tg_dir) if ".TextGrid" in fn]
item_id = [f.split("_")[1] for f in filenames]
item_num = [i[:-1] for i in item_id]
item_con = [i[-1] for i in item_id]
subject_id = [f.split("_")[2] for f in filenames]


# In[4]:


rt = []
response = []
notes = []
for tg_loc in [f for f in os.listdir(tg_dir) if ".TextGrid" in f]:
    tg = textgrids.TextGrid(os.path.join(tg_dir, tg_loc))
    rt.append(tg["words"][1].xmin)
    response.append(tg["words"][1].text)
    notes.append(tg["notes"][0].text)


# In[5]:


d = pd.DataFrame({"filenames": filenames, "item_id": item_id, "item_num":item_num, "item_con":item_con, "subject_id": subject_id, "response":response, "rt":rt, "notes":notes})


# In[6]:


d


# In[7]:


d.to_csv("/Users/masato/Box/cloze_experiments/filter/data_pilot/result_pilot.csv", index = False)


# In[ ]:




