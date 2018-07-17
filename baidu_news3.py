#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 16:27:08 2018
百度新闻爬虫
改进：每一次请求网页时，爬取当页新闻标题和检查是否有下一页

@author: situ
"""

import time
from urllib.parse import urlencode
import pandas as pd
import os
import requests
import numpy as np
from lxml import etree
from multiprocessing import Pool


#bt = "2011-01-01"
#et = "2011-12-31"
#word = "购房意愿"

#如果搜索标题，则不会显示摘要，且按时间排序
#如果搜索全文，按相关度排序，则越后面的新闻越不相关


def get_url(word,year,page,mode):
    bt = str(year)+"-01-01 00:00:00"
    et = str(year)+"-12-31 00:00:00"
    bts = int(time.mktime(time.strptime(bt, "%Y-%m-%d %H:%M:%S")))#时间戳
    ets = int(time.mktime(time.strptime(et, "%Y-%m-%d %H:%M:%S")))
    
    pn = 20*(page-1)# 页码对应：0 20 40 60
    if mode=="news":
        qword = urlencode({'word': word.encode('utf-8')})
        url = "http://news.baidu.com/ns?%s&pn=%d&cl=2&ct=1&tn=newsdy&rn=20&ie=utf-8&bt=%d&et=%d"%(qword,pn,bts,ets)
    if mode=="title":
        qword = "word=intitle%3A%28"+word+"%29"
        url = "http://news.baidu.com/ns?%s&pn=%d&cl=2&ct=0&tn=newstitledy&rn=20&ie=utf-8&bt=%d&et=%d"%(qword,pn,bts,ets)
    return url

#url = get_url("投资热度",bt,et,10)


def crawl(word,year=2011,mode="title"):
    i = 1
    is_nextpage=True
    newsData = pd.DataFrame()
    while is_nextpage:
        print("--------------正在爬取【%s】第%d页新闻----------------"%(word,i))
        url = get_url(word,year,i,mode)
        print(url)
        result = requests.get(url,timeout=60)
        if result.status_code==200:
            print("\n请求成功")
        result.encoding = 'utf-8'
        selector = etree.HTML(result.text)  
        if mode=="news":

            for item in selector.xpath('//*[@class="result"]'):
    #            item = selector.xpath('//*[@class="result"]')[0]
                newsdict = {"title":[0],"date":[0],"time":[0],"source":[0],
                            "abstract":[0],"href":[0]}
                onenews = pd.DataFrame(newsdict)
                
                onenews["title"] = item.xpath('h3/a')[0].xpath("string(.)").strip()
                print(onenews["title"])
                onenews["href"] = item.xpath('h3/a/@href')[0]
                info = item.xpath('div')[0].xpath("string(.)")
                onenews["source"] , onenews["date"] , onenews["time"]= info.split()[:3]
                onenews["abstract"] = " ".join(info.split()[3:len(info.split())-1])
                newsData = newsData.append(onenews)
        if mode=="title":
            for item in selector.xpath('//*[@class="result title"]'):
#                item = selector.xpath('//*[@class="result title"]')[0]
                newsdict = {"title":[0],"date":[0],"time":[0],"source":[0],"href":[0]}
                onenews = pd.DataFrame(newsdict)
                
                onenews["title"] = item.xpath('h3/a')[0].xpath("string(.)").strip()
                onenews["href"] = item.xpath('h3/a/@href')[0]
                info = item.xpath('div')[0].xpath("string(.)")
#                print(info)
                onenews["source"] , onenews["date"] , onenews["time"]= info.split()[:3]
                
                newsData = newsData.append(onenews)
        page_info = selector.xpath('//*[@id="page"]/a[@class="n"]/text()')
        print(page_info)
        if len(page_info)>=1 and "下一页>" in page_info:
            is_nextpage=True
            i=i+1
        else:
            is_nextpage=False

    newsData.to_csv(word+"_"+str(year)+"_"+mode+".csv",index = False,encoding = "gb18030")


if __name__=='__main__':
#    os.chdir("E:/graduate/毕业论文")
    os.chdir("/Volumes/SNOWING")
    para = ["购房意愿","楼市热度","市场情绪"]
    p=Pool(len(para))
    p.map(crawl,para)      
    p.close()
    p.join()
    print("爬取成功，请打开【"+os.getcwd()+"】查看详情")
