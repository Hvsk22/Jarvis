
# coding: utf-8

# In[2]:


import pandas as pd 


# In[37]:


import numpy as np


# In[3]:


import datetime as datetime


# In[4]:


projectid = "bjp-booth"


# In[5]:


invitation = pd.read_gbq('SELECT app_trained,verification_call_done, bk_type, owner, user_id, constituency_id, refCode, hidden, joining_status,inivited_name.string, inivited_name.text, booth_id, create_ts, verified, trained_on, voter_id, inivited_designation.text,bk_cc_verified,bk_cc_rejected, inivited_phone, mark_trained,invited_user_type, cast(__key__.id as string) as key_id_invitation  FROM [bjp-booth:dsExport.Invitation]', projectid)


# In[6]:


invitation = invitation[invitation.hidden == False]


# In[7]:


mydefined = pd.read_gbq('select alt_phone, app_trained, booth, aadhar.text, password, last_active, designation.text, change_ts, constituency_id, refCode, hidden,app_version, email, booth_id, language, user_type, pc_id, phone, create_ts, logged_in_using, fcm_id, name.text, voter_id.text, created,constituency, is_sudo, vistarak_whatsapp, cast(__key__.id as string) as key_id_user from [bjp-booth:dsExport.MyDefinedUser]',projectid)


# In[8]:


mydefined = mydefined[mydefined.hidden == False]


# In[9]:


newbooth = pd.read_gbq('select name, number, cc_verified, constituency_id, state, create_ts, otp, hidden, pramukh, cast(__key__.id as string) as key_id_booth from [bjp-booth:dsExport.NewBooth]', projectid)


# In[10]:


newbooth = newbooth[newbooth.hidden == False]


# In[11]:


newconstituency = pd.read_gbq("select parwasi, ac_wa_grp_2, booths, name, pc_incharge, ac_wa_grp, number, type_, create_ts, pc_wa_grp, hidden, vistarak, parcon,cast(__key__.id as string) as key_id_constituency from [bjp-booth:dsExport.NewConstituency]", projectid)


# In[12]:


newconstituency = newconstituency[newconstituency.hidden == False]


# In[13]:


newevent = pd.read_gbq("select managed_by, duration, created_by, constituency_id, hidden, booth_id, constituency_name,invited, date, training_event, training_type, create_ts, cast(__key__.id as string) as key_id_newEvent from [bjp-booth:dsExport.NewEvent]",projectid)


# In[14]:


newevent = newevent[newevent.hidden== False]


# In[15]:


mapping = pd.read_excel(r'Master Sheet.xlsx')


# In[167]:


bk = invitation[invitation['invited_user_type'] == 0][invitation['hidden'] == False ]


# In[168]:


bk_ac = bk.groupby(['booth_id']).size()


# In[169]:


bk_ac = bk_ac.reset_index()


# In[170]:


bk_ac = bk_ac.rename(columns={0:'bk_total'})


# In[171]:


booth = newbooth[['key_id_booth','constituency_id','name']].copy()


# In[172]:


booth = booth.reindex()


# In[173]:


ac = newconstituency[['key_id_constituency','name','number']].copy()


# In[174]:


ac = ac.rename(columns={'key_id_constituency': 'constituency_id'})


# In[175]:


ac.drop_duplicates('name',inplace = True)


# In[176]:


ac = ac.reset_index()


# In[177]:


ac = ac.drop(columns=['index'])


# In[178]:


booth = booth.merge(ac,on = 'constituency_id', how = 'left')


# In[179]:


booth = booth.rename(columns={'key_id_booth':'booth_id','name_x':'booth_number','name_y':'ac_name'})


# In[180]:


booth = booth.dropna(subset=['number'])


# In[181]:


booth = booth.merge(bk_ac,on = 'booth_id', how = 'left')


# In[182]:


bk_verified = bk[['booth_id', 'verified']].reset_index()


# In[183]:


bk_verified = bk_verified[bk_verified.verified == True]


# In[184]:


bk_verified = bk_verified.drop(columns='index')


# In[185]:


bk_verified = bk_verified.groupby(['booth_id']).size()


# In[186]:


bk_verified = bk_verified.reset_index()


# In[187]:


bk_verified = bk_verified.rename(columns={0:'bk_verified'})


# In[188]:


booth = booth.merge(bk_verified,on='booth_id',how='left')


# In[189]:


bk_app = bk[bk.joining_status == 1]


# In[190]:


bk_app = bk_app.groupby(['booth_id']).size()


# In[191]:


bk_app = bk_app.reset_index().rename(columns = {0:'bk_app'})


# In[192]:


booth = booth.merge(bk_app,on = 'booth_id',how = 'left')


# In[193]:


x = datetime.date.today() - datetime.timedelta(3)


# In[194]:


bk_total_last_3days = bk[['booth_id', 'create_ts']].copy()


# In[195]:


bk_total_last_3days = bk_total_last_3days[bk_total_last_3days.create_ts > x]


# In[196]:


bk_total_last_3days = bk_total_last_3days.groupby(['booth_id']).size().reset_index()


# In[197]:


bk_total_last_3days = bk_total_last_3days.rename(columns= {0:'bk_total_last_3days'})


# In[198]:


booth = booth.merge(bk_total_last_3days,on='booth_id',how='left')


# In[199]:


booth = booth.rename(columns = {'number':'AC Number'})


# In[220]:





# In[201]:


booth = booth.merge(mapping,on ='AC Number', how= 'left')


# In[202]:


y = datetime.date.today()


# In[203]:


bk_not = bk[(bk.bk_cc_rejected == False) & (bk.bk_cc_verified == False) & (bk.verification_call_done == True)]


# In[204]:


bk_not = bk_not.groupby(['booth_id']).size()


# In[205]:


bk_not = bk_not.reset_index().rename(columns = {0:'bk_call_attempts_>5'})


# In[206]:


booth = booth.merge(bk_not,on = 'booth_id',how = 'left')


# In[207]:


bk_ccver = bk[bk.bk_cc_verified == True]


# In[208]:


bk_ccver = bk_ccver.groupby(['booth_id']).size()


# In[209]:


bk_ccver = bk_ccver.reset_index().rename(columns = {0:'bk_cc_verified'})


# In[210]:


booth = booth.merge(bk_ccver,on='booth_id',how='left')


# In[211]:


bk_ccrej = bk[bk.bk_cc_rejected== True]


# In[212]:


bk_ccrej = bk_ccrej.groupby(['booth_id']).size()


# In[213]:


bk_ccrej=bk_ccrej.reset_index().rename(columns = {0:'bk_cc_rejected'})


# In[214]:


booth = booth.merge(bk_ccrej,on='booth_id',how = 'left')


# In[215]:


bk_file = booth.drop(columns=['booth_id','constituency_id'])


# In[216]:


bk_file = bk_file.fillna('0')


# In[217]:


bk_file['AC Number'] = bk_file['AC Number'].map(lambda x : float(x))


# In[218]:


bk_file.to_csv('bk_file' + str(y) + '.csv' )


# In[ ]:




