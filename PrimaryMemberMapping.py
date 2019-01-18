
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import os
import re
import sys
import jellyfish
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from filelock import Timeout, FileLock
from nltk.corpus import wordnet
import datetime


# In[ ]:

sttime = datetime.datetime.now().replace(microsecond=0)
filename= sys.argv[1]
AC_Number = int(sys.argv[2])

file_path = "C:\\PrimaryMemberMapping\\NameList\\NameList.pickle"
lock_path = "C:\\PrimaryMemberMapping\\NameList\\NameList.pickle.lock"
lock = FileLock(lock_path, timeout=10)
try:
    with lock.acquire(timeout=10):
        pickle_names = open("C:\\PrimaryMemberMapping\\NameList\\NameList.pickle","rb")
        names_to_match = pickle.load(pickle_names)
        pickle_names.close()
except Timeout:
    print("Could not get a lock")


# In[ ]:


def getAddressList(add, city, Assem):
    return add.replace(city, '').replace(Assem, '')

def getAddressonly(x, y, city, Assem):
    xlist = re.split('\W+', x)
    xm = [y.find(i) + len(i) for i in xlist]
    return getAddressList(y[max(xm):], city, Assem)

def matchAddress(x, y):
    xlist = re.split('\W+', x)
    matchList = [jellyfish.jaro_winkler(i, str(y)) for i in xlist]
    if(len(matchList)>0):
        return max(matchList)
    else:
        return 0

def get_name(x, nameList):
    x = str(x).lstrip('0123456789.-,; |!@#$%^&*()')
    xlist = re.split('\W+', x)
    if (re.sub(r'[0-9]', '', xlist[0])!=xlist[0]):
        del xlist[0]
    nmfound = 0
    while(nmfound==0):
        if(len(xlist)>0):
            if (wordnet.synsets(xlist[0])):
                del xlist[0]
            elif xlist[0] in ["my", "name"]:
                del xlist[0]
            else:
                nmfound=1
        else:
            nmfound=1
    nameList.extend(xlist[:2])
    return " ".join(xlist[:2]), " ".join(xlist[2:])

def get_add_name(x, nameList):
    xlist = re.split('\W+', str(x))
    name = ""
    if (len(xlist)>0):
        if (xlist[0] in nameList):
            if not wordnet.synsets(xlist[0]):
                name = xlist.pop(0)
    return name, " ".join(xlist)


# In[ ]:


prim = pd.read_excel(filename)
prim['member_id'] = prim.index
booth = pd.read_excel("Maharashtra-Urban+Rural Booth-Village mapped.xlsx")
prim['Name_address'] = prim['Name_address'].str.lower()
prim['extracted_name'], prim['Address_only'] = zip(*prim['Name_address'].map(lambda x: get_name(x, names_to_match)))
names_to_match = list(set(names_to_match))
prim['Additional_name'], prim['Address_only'] = zip(*prim['Address_only'].map(lambda x: get_add_name(x, names_to_match)))
prim['extracted_name'] = prim['extracted_name'].str.cat(prim['Additional_name'], sep=" ")
prim.drop(['Additional_name'], axis=1, inplace=True)
booth["Village mapped"] = booth["Village mapped"].str.lower()
booth_filtered = booth[booth['AC Number']==AC_Number]
booth_filtered =  booth_filtered[['Booth No.', 'Village mapped', 'Key']]


# In[ ]:


try:
    with lock.acquire(timeout=10):
        pickle_names = open("C:\\PrimaryMemberMapping\\NameList\\NameList.pickle","wb")
        pickle.dump(names_to_match, pickle_names)
        pickle_names.close()
except Timeout:
    print("Could not get a lock")


# In[ ]:


prim['mk'] = 1
booth_filtered['mk'] = 1
prim_cross = prim.merge(booth_filtered, on = ['mk'], how = 'inner')
prim_cross['edit'] = prim_cross.apply(lambda x:matchAddress(x['Address_only'], x['Village mapped']), axis=1)
prim_cross.sort_values(by=['member_id', 'edit'], ascending=[True, False], inplace=True)
prim_cross.drop_duplicates(subset=['member_id'], keep = 'first', inplace=True)
prim_lvl2_match = prim_cross[prim_cross['edit'] >= 0.75].drop(['mk', 'edit'], axis=1)
prim_matched = prim_lvl2_match


# In[ ]:


prim_matched['Address_only'] = prim_matched['Address_only'].apply(lambda x:re.sub(r'[0-9]', '', x))


# In[ ]:


prim_matched_address_docs = prim_matched.groupby(['Booth No.'])['Address_only'].apply(lambda x:"%s" % ' '.join(x)).reset_index()


# In[ ]:


v1 = TfidfVectorizer(stop_words = 'english')
tfVector = v1.fit_transform(prim_matched_address_docs['Address_only'].tolist())


# In[ ]:


prim_unmatched = prim[~prim['member_id'].isin(list(set(prim_lvl2_match['member_id'].tolist())))]
prim_unmatched['Address_only'] = prim_unmatched['Address_only'].apply(lambda x:re.sub(r'[0-9]', '', x))
score_vector=v1.transform(prim_unmatched['Address_only'].tolist())


# In[ ]:


distances = np.matmul(score_vector.todense(), tfVector.todense().transpose())
max_cosine = np.argmax(np.asarray(distances), axis=1)
prim_unmatched['Matched_index'] = pd.Series(max_cosine)
prim_matched_address_docs['Matched_index'] = prim_matched_address_docs.index
prim_unmatched = prim_unmatched.merge(prim_matched_address_docs.drop(['Address_only'], axis=1), on=['Matched_index']                                ,how = 'inner').drop(['Matched_index'], axis=1)
prim_lvl3_match = prim_unmatched
prim_matched = pd.concat([prim_lvl2_match, prim_lvl3_match ])


# In[ ]:

prim_matched.drop_duplicates(subset=['member_id'], inplace=True)
prim_matched.to_excel("MatchedPrimaryMembers_" + str(AC_Number) +".xlsx")
entime = datetime.datetime.now().replace(microsecond=0)
print(entime - sttime)