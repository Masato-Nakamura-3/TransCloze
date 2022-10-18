#!/usr/bin/env python
# coding: utf-8

# # Check inflection

# In[2]:


import spacy
import pyinflect

import textgrids

import os


# In[3]:


tg_dir = "/Users/masato/Box/cloze_experiments/filter/data_pilot/tg_corrected"


# In[4]:


tglist = [f for f in os.listdir(tg_dir) if ".TextGrid" in f]
pathlist = [os.path.join(tg_dir, t) for t in tglist]


# In[5]:


nlp = spacy.load('en_core_web_sm')


# In[6]:


exceptions = ["worked", "swum", "embarrassed", "amazed", "worked for", "impressed", 
              "dive-bombed", "pooped", "gotten", "lied", "spit", "spilt", "hidden", "scammed"]


# In[7]:


plist = []

for p in pathlist:
    tg = textgrids.TextGrid(p)
    response = str(tg["words"][1].text)
    tokens = nlp(response)
    pp = tokens[0]._.inflect('VBN')
    
    if ((str(tokens[0]) != pp) & (response not in ["NOT_RECOGNIZED", "NEED_HELP"]) & (response not in exceptions) & 
        (str(tokens[0]) not in exceptions) & ("not_verb" not in tg["notes"][0].text) & ("speech_error" not in tg["notes"][0].text) #& 
       #("uncertain" not in tg["notes"][0].text)
       ): 
                
        fn = os.path.splitext(os.path.basename(p))[0]
        
        print(fn, "\t", response, "\t", pp)
        
        plist.append(p)


# In[60]:


plist


# In[62]:


import shutil
for p in plist:
    shutil.move(p, "/Users/masato/Box/cloze_experiments/filter/batch1/working")


# In[ ]:





# In[ ]:


attention = ["spit", "spat", "spitted", "beaten", "pled","pleaded","flew", "flown", "bit", "bitten", "spilled", "spilt"]


# In[27]:


for p in pathlist:
    tg = textgrids.TextGrid(p)
    response = str(tg["words"][1].text)

    
    if response in attention: 
                
        fn = os.path.splitext(os.path.basename(p))[0]
        
        print(fn, "\t", response)


# In[ ]:





# ### Check tags/notes

# Get a list of tags and make sure there is no typo

# In[66]:


import re
tagset = set()

for p in pathlist:
    tg = textgrids.TextGrid(p)
    rtags = tg["notes"][0].text
    rtaglist = re.split(' |,', rtags)
    
    tagset = tagset | set(rtaglist)
    
print(tagset)


# In[67]:


taglist = list(tagset)
taglist.sort()


# In[68]:


print(taglist)


# In[ ]:




