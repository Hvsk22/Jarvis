
# coding: utf-8

# In[1]:


import multiprocessing as mp
from eventlet import timeout
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
import pytesseract
from PIL import Image
import subprocess
from subprocess import Popen,PIPE,STDOUT,call, check_output
import os
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options


# In[2]:


def get_captcha(driver, element, path):
    location = element.location
    size = element.size
    # saves screenshot of entire page
    driver.save_screenshot(path)
    print(size, location)

    # uses PIL library to open image in memory
    
    image = Image.open(path)

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    image = image.crop((left, top, right, bottom))  # defines crop points
    image.save(path, 'jpeg', dpi=(1200, 1200))  # saves new cropped image
    proc=check_output('RunTess.bat').split()
    try:
        proc = int(proc[len(proc)-1])
    except:
        proc = 11111
    #os.remove(path)
    return proc

def read_page(df, browser):
    try:
        x = browser.find_element_by_xpath("//tbody")
        y = x.find_elements_by_xpath("./tr")
        for i in range(len(y)):
            z = y[i].find_elements_by_xpath("./td")
            thisline=[]
            for j in range(1, len(z)):
                thisline.append(z[j].text)
            df.loc[len(df)] = thisline
    except:
        pass
    
def hasNext(browser):
    try:
        browser.find_element_by_xpath("//li[@class='next']/a")
        return True
    except:
        return False
    
def isLoaded(browser):
    x11 = browser.find_element_by_xpath("//div[@id='captchaControlsDiv']/span")
    print(x11)
    return (x11.text=="")


# In[3]:


def getData(df, name, age):
    options = Options() 
    options.add_argument("--start-maximized") 
    browser = webdriver.Chrome("chromedriver", chrome_options=options)
    browser.get("http://electoralsearch.in/")
    browser.find_element_by_xpath("//input[@id='continue']").click()
    browser.find_element_by_xpath("//input[@id='name1']").send_keys(str(name))
    browser.find_element_by_xpath(age).click()
    loaded = False
    print("Test1")
    while (loaded==False):
        element = browser.find_element_by_xpath("//img[@id='captchaDetailImg']")
        captcha = get_captcha(browser, element, "TempCaptcha.jpeg")
        browser.find_element_by_xpath("//input[@id='txtCaptcha']").send_keys(str(captcha))
        browser.find_element_by_xpath("//button[@id='btnDetailsSubmit']").click()
        browser.implicitly_wait(10)
        time.sleep(5)
        loaded=isLoaded(browser)
    
    print("Test2")
    hasNextInd=True
    indPage = 0;
    while(hasNextInd):
        indPage = indPage+1;
        bool1 = read_page(df, browser)
        hasNextInd=hasNext(browser)
        if(hasNextInd & (indPage<100)):
            try:
                browser.find_element_by_xpath("//li[@class='next']/a").click()
                browser.implicitly_wait(10)
                time.sleep(5)
            except:
                hasNextInd = False
            
    print("Test3")
    browser.close()


# In[4]:


df = pd.DataFrame(columns = ['EpicNo', 'Name', 'Age', 'Father_Husband_Name', 'State', 'District', 'PollingStation', 'Assembly',                            'Parliament'])
for i1 in range(97, 123):
    for i2 in range(97, 123):
        for i3 in range(97, 123):
            for i4 in range(18, 121):
                name = chr(i1) + chr(i2) + chr(i3)
                age = str(i4)
                ageid = "//select[@id='ageList']/option[text()='" + age + "']"
                getData(df, name, ageid)


# In[5]:


df.to_csv("ScrappedVoterList_v1.csv")

