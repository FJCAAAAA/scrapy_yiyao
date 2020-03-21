#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : yongyaozhushou.py
@Author: Fengjicheng
@Date  : 2020/3/19
@Desc  :  用药助手药品数据爬取
'''
import scrapy
from yiyao.items import YiyaoYongyazhushouItem


class YongyaozhushouSpider(scrapy.Spider):
    name = 'yongyaozhushou'
    home_page = 'http://drugs.dxy.cn/'

    def start_requests(self):
        yield scrapy.Request(url=self.home_page, callback=self.parse)

    def parse(self, response):
        erjileimu_list = response.xpath('//div[@class="common_main ml279"]/div[@name="cate_div"]//li/h3/a/@href').extract()
        for erjileimu in erjileimu_list:
            url = 'http:' + erjileimu
            yield scrapy.Request(url=url, callback=self.erji_parse)

    def erji_parse(self, response):
        med_url_list = response.xpath('//div[@class="m49 result"]//li//h3/a/@href').extract()
        for med_url in med_url_list:
            med_url = 'http:' + med_url
            yield scrapy.Request(url=med_url, callback=self.yaopin_parse)
        next_page = response.xpath('//div[@class="pagination"]//a[@title="下一页"]/@href').extract_first()
        if next_page:
            next_page = ''.join([response.url, next_page])
            yield scrapy.Request(url=next_page, callback=self.erji_parse)

    def yaopin_parse(self, response):
        response.xpath('')




