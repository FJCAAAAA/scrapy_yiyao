#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : baidu.py
@Author: Fengjicheng
@Date  : 2019/3/10
@Desc  : 医疗百科药物 https://baike.baidu.com/wikitag/taglist?tagId=75954
'''
import scrapy
import json
import re
from yiyao.items import YiyaoBaiduItem


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    spe1 = '。，：；．.,:;'
    pattern1 = re.compile('：')
    pattern2 = re.compile('、')
    pattern3 = re.compile('。')
    pattern4 = re.compile('^[^0-9].*：$')  # 匹配概括性语句，例如 "阿莫西林适用于敏感菌(不产β内酰胺酶菌株)所致的下列感染："
    pattern5 = re.compile('^[0-9]+(\.|．).*')  # 匹配数字开头的语句，例如 "2.大肠埃希菌、奇异变形杆菌或粪肠球菌所致的泌尿生殖道感染。"
    pattern6 = re.compile('[0-9]+(\.|．)')

    def start_requests(self):
        url = 'https://baike.baidu.com/wikitag/api/getlemmas'
        for page_num in range(10):
            data = {
                'limit': '24',
                'timeout': '3000',
                'filterTags': [],
                'tagId': '75954',
                'fromLemma': 'false',
                'contentLength': '40',
                'page': str(page_num)
            }
            yield scrapy.FormRequest(url=url, formdata=data, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.text)
        res_list = res.get('lemmaList')
        for res_dict in res_list:
            med_name = res_dict.get('lemmaTitle')
            url = res_dict.get('lemmaUrl')
            yield scrapy.Request(url=url, callback=self.detail_parse, meta={'med_name': med_name})

    def large_text(self, obj):
        if type(obj) == list and len(obj) != 0:
            # 判断首行是否是概括性语句,如果是，就排除掉
            if self.pattern4.match(obj[0]):
                obj = obj[1:]
            # 判断格式是否数字开头
            if self.pattern5.match(obj[0]):
                obj_new = self.pattern6.split(''.join(obj))
            else:
                obj_new = obj
            return [x.strip(self.spe1) for x in obj_new if
                    x.strip(self.spe1) != '' and x.strip(self.spe1) != '，' and x.strip(self.spe1) != '、']
        else:
            return ''

    def detail_parse(self, response):
        # 判断主体末端是哪种标签
        if response.text.find('<div class="tashuo-bottom" id="tashuo_bottom">'):
            sep0 = '<div class="tashuo-bottom" id="tashuo_bottom">'
        elif response.text.find('<dt class="reference-title">'):
            sep0 = '<dt class="reference-title">'
        elif response.text.find('<div class="lemma-paper-box">'):
            sep0 = '<div class="lemma-paper-box">'
        elif response.text.find('<div class="open-tag-title">'):
            sep0 = '<div class="open-tag-title">'
        html = re.split(sep0, response.text)[0]
        med_name = response.meta.get('med_name')
        summary = response.xpath('//div[@class="lemma-summary"]/div[@class="para"]/text()').strip()


        item = YiyaoBaiduItem()
        item['med_name'] = med_name
        item['med_intro'] = summary
        yield item



