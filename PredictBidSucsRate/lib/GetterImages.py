# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 11:25:22 2021

@author: USER
"""
from lib.MessageDispatcher import MessageDispatcher
from urllib.request import urlopen
from urllib.parse import quote_plus
import json
import os
import shutil
import datetime as dt

class GetterImages:
    dispatcher = MessageDispatcher.getInstance();
    
    
    def __init__(self):
        pass
    
    @classmethod
    def log(cls, msg):
        strdt = dt.datetime.now().isoformat()
        fmtMsg = strdt+" [DEBUG] " + msg
        cls.dispatcher.send("SubGetterImgForm", cls, "console", fmtMsg)
        #print(fmtMsg)        
        
    @classmethod
    def run(cls, keyword, pagesize, page):
        startIndex = 1+((page-1)*pagesize)
        
        #baseUrl = 'https://search.naver.com/search.naver?where=image&sm=tab_jum&query='
        baseUrl = 'https://s.search.naver.com/p/image/46/search.naver?ac=0&aq=0&json_type=6&mode=&section=image&where=image';
        

        params = "&start="+str(startIndex)+"&display="+str(pagesize)+"&query=" 
        url = baseUrl + params + quote_plus(keyword) # 한글 검색 자동 변환
        
        cls.log(url);
        
        html = urlopen(url).read()
        #soup = bs(html,'html.parser')
        #jsons = json.loads(soup.text)
        jsons = json.loads(html)
        
        cur_dir = os.getcwd()
        basedir = cur_dir+'/data/'+keyword
        jsondir = cur_dir+'/data/'+keyword+'/json'
        imgdir = cur_dir+'/data/'+keyword+'/images'
        datasetdir = cur_dir+'/data/dataset/'+keyword
        
        if os.path.exists(basedir):
            shutil.rmtree(basedir, ignore_errors=True)
        
        os.mkdir(basedir)    
        
        if os.path.exists(datasetdir):
            shutil.rmtree(datasetdir, ignore_errors=True)
        
        os.mkdir(datasetdir)   
        
        if not os.path.exists(jsondir):
            os.mkdir(jsondir)
            
        if not os.path.exists(imgdir):
            os.mkdir(imgdir)
        
        filecnt = len(os.listdir(jsondir))
        jsonname = 'rs_' + str(filecnt+1) +'.json'
        
        if jsons:
            with open(jsondir+'/' + jsonname,'w+') as t: # w - write
                json.dump(jsons, t)
                t.close()
        
        
        n = 0
        for row in jsons["items"]:
            n += 1
            with open(jsondir+'/img_' + str(n)+'.json','w+') as fo: # w - write
                json.dump(row, fo)
                fo.close()    
                
            img332url = row['thumb332']
            if img332url:
                cls.log("["+str(n)+"] "+img332url)
                
                with urlopen(img332url) as f:
                    imgname = 'img_' + str(n)+'.jpg'
                    with open(imgdir+'/'+imgname,'wb+') as h: # w - write b - binary
                        img = f.read()
                        h.write(img)   
                        h.close()
                        shutil.copyfile(imgdir+'/'+imgname, datasetdir+'/'+imgname)
            
           
        cls.log('Image Crawling is done.')
        
