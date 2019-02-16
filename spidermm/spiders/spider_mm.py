# -*- coding: utf-8 -*-
import scrapy
from spidermm.items import SpidermmItem
from scrapy.http import Request
import requests
import re
import os
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

class SpiderMmSpider(scrapy.Spider):
    name = 'spider_mm'
    allowed_domains = ['www.mmonly.cc']
    start_urls = ['http://www.mmonly.cc/']
    base = 'd:\\2\\'

    def start_requests(self):
        # 一共有7页
        for i in range(1, 8):
            if i==1:
                url = 'https://www.mmonly.cc/tag/xh1/index.html'
            else:
                url = 'https://www.mmonly.cc/tag/xh1/' + str(i) + '.html'
            yield Request(url, callback=self.parse_one)

    def parse_one(self, response):
        # 创建一个大的list存储所有的item
        items = []
        pattern = re.compile(r'<div class="title".*?<a.*?href="(.*?)">(.*?)</a></span></div>', re.S)
        pattern1=re.compile(r'<b>(.*?)</b>', re.S)
        mains = re.findall(pattern, response.text)
        for main in mains:
            # 创建实例,并转化为字典
            item = SpidermmItem()
            item['siteURL'] = main[0]
            item['title'] = main[1]
            #print item['title']
            #如果匹配<b></b>，需要处理
            if item['title'][0] != '<':
                item['fileName'] = self.base + item['title']
            else:
                item['fileName'] = self.base + re.findall(pattern1, response.text)[0]

            items.append(item)

        for item in items:
            #print item
            # 创建文件夹
            fileName = item['fileName']
            print fileName
            if not os.path.exists(fileName):
                try:
                    os.makedirs(fileName)

                except:
                    pass
                    print '创建文件错误111'
                    #print self.base +re.compile(pattern1, item['title'])[0]
                    #os.makedirs(self.base +re.compile(pattern1, item['title'])[0])
            # 用meta传入下一层
            yield Request(url=item['siteURL'], meta={'item1': item}, callback=self.parse_two)

    def parse_two(self, response):
        # 传入上面的item1
        #print response.url
        item2 = response.meta['item1']
        source = requests.get(response.url)
        html = source.text.encode('iso-8859-1').decode('gbk')
        #print html
        Numpage1 = response.xpath("//div[@class ='pages']/ul/li[1]/a").extract()[0]
        #print Numpage1.decode('utf-8')
        pattern = re.compile(r'共(.*?)页:', re.S)
        Num = re.sub(r'\D',"",Numpage1.decode('utf-8'))
        #print Num
        if Num==None:
            Num=1
        items = []
        for i in range(1, int(Num) + 1):
            item = SpidermmItem()
            item['fileName'] = item2['fileName']
            # 构造每一个图片的存储路径
            item['path'] = item['fileName'] + '/' + str(i) + '.jpg'
            # 构造每一个图片入口链接，以获取源码中的原图链接
            item['pageURL'] = response.url[:-5] + '_' + str(i) + '.html'
            items.append(item)
        for item in items:
            yield Request(url=item['pageURL'], meta={'item2': item}, callback=self.parse_three)

    def parse_three(self, response):
        item = SpidermmItem()
        # 传入上面的item2
        item3 = response.meta['item2']
        pattern = re.compile(
            r'<li class="pic-down h-pic-down"><a target="_blank" class="down-btn" href=\'(.*?)\'>.*?</a>', re.S)
        URL = re.search(pattern, response.text).group(1)
        item['detailURL'] = URL
        item['path'] = item3['path']
        item['fileName'] = item3['fileName']
        yield item
