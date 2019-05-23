# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:00:11 2019

@author: fanning1207
"""

import os
import pandas as pd
import pymysql
import requests
import time
import random 
from urllib.parse import quote
import string
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

#os.chdir('地址')

#-----------------------------connect mysql-------------------
sql = 'SELECT com_id,com_name FROM ba_company WHERE com_name IS NOT NULL'

db = pymysql.connect(host=host,
                       user=用户名,
                       passwd=用户密码,
                       db=数据库名,
                       port=3306,
                       charset="utf8")    
cursor = db.cursor()
cursor.execute(sql)
datalist= cursor.fetchall()
datalist  = pd.DataFrame(list(datalist),columns=('com_id','com_name'))

com_id = datalist['com_id']
com_name = datalist['com_name']



sql = 'SELECT patent_id,title,assignee,inventor,priority_date,filing_date,publication_date,grant_date,google_link,industry FROM patent_new'

cursor.execute(sql)
patent = cursor.fetchall()
patent = pd.DataFrame(list(datalist),columns=("patent_id",'title','assignee',"inventor","priority_date","filing_date","publication_date","grant_date","google_link","industry"))

db.close()

#-----------------------------download csv and insert-------------------
pymysql.install_as_MySQLdb()
engine = create_engine("mysql://用户名:用户密码@host/db")

for i in range(len(com_id)):
    url = 'https://patents.google.com/xhr/query?url=assignee%3D'+com_name[i]+'%26language%3DCHINESE%26type%3DPATENT%26num%3D100%26sort%3Dnew&exp=&download=true'
    url = quote(url, safe = string.printable)  
    r = requests.get(url)
    file = str(com_id[i]) +".csv"
    with open (file, "wb") as code:
        code.write(r.content)
    
    if os.path.getsize(file)>376 :
        try:
            insert_data = pd.read_csv(file, header=1)
            insert_data.columns = ["patent_id",'title','assignee',"inventor","priority_date","filing_date","publication_date","grant_date","google_link",'representative figure link']
            insert_data = insert_data.iloc[:,0:9]
            insert_data.insert(9, "industry",["NA"]*len(insert_data.patent_id), True) 
            
            insert_data = insert_data.append(patent)
            insert_data = insert_data.drop_duplicates(subset=["patent_id"],keep=False)
            
            if len(insert_data.patent_id)>0:
                try:
                    insert_data.to_sql(con=engine, name='patent_new', if_exists='append',index=False)
                except:
                    pass
        except:
            pass
    os.remove(file)
    time.sleep(random.uniform(3,5))

#-----------------------------connect mysql-------------------
sql = 'SELECT patent_id,google_link FROM patent_new WHERE classification_code IS NULL OR abstract IS NULL'

db = pymysql.connect(host=host,
                       user=用户名,
                       passwd=用户密码,
                       db=数据库名,
                       port=3306,
                       charset="utf8")      

cursor = db.cursor()
cursor.execute(sql)
datalist = cursor.fetchall()

datalist = pd.DataFrame(list(datalist),columns=('patent_id','google_link'))

patent_id = datalist['patent_id']
google_link = datalist['google_link']

#------------------------ update abstract/classification--------------------------------------
for i in range(len(google_link)):
    try:
        r = requests.get(google_link[i])
        r.encoding='utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        result_code = str(soup.findAll('span',{'itemprop':'Code'}))
        result_code = result_code.replace('<span itemprop="Code">','')
        result_code = result_code.replace('[','')
        result_code = result_code.replace('</span>','')
        result_code = result_code.replace(']','')

        result_d = str(soup.findAll('span',{'itemprop':'Description'}))
        result_d = result_d.replace('<span itemprop="Description">','')
        result_d = result_d.replace('[','')
        result_d = result_d.replace('</span>','')
        result_d = result_d.replace(']','')
        
        result_search = str(soup.findAll('div',{'class':'abstract'}))
        result_search = result_search.replace('[<div class="abstract">','')
        result_search = result_search.replace('[<div class="abstract" num="0001">','')
        result_search = result_search.replace('&lt;pb pnum="1" /&gt; "','')
        result_search = result_search.replace('&lt;pb pnum="1" /&gt;','')
        result_search = result_search.replace('</div>]','')
        
        add_it0 = 'update patent_new set classification_code = "' + result_code + ' " where patent_id = "' + str(patent_id[i]) +'"'
        cursor.execute(add_it0)
        db.commit()
        
        add_it1 = 'update patent_new set classifications_name = "' + result_d + ' " where patent_id = "' + str(patent_id[i]) +'"'
        cursor.execute(add_it1)
        db.commit()
        
        add_it = 'update patent_new set abstract = "' + result_search + ' " where patent_id = "' + str(patent_id[i]) +'"'
        cursor.execute(add_it)
        db.commit()
    except:
        pass


db.close()
