#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : sfda.py
@Author: Fengjicheng
@Date  : 2020/1/21
@Desc  : 药监局 国产药品 字段爬取 http://qy1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=25&tableName=TABLE25&title=%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81&bcId=152904713761213296322795806604
'''
import scrapy
from yiyao.items import YiyaoSfdaItem


class SfdaSpider(scrapy.Spider):
    name = 'sfda'

    def start_requests(self):
        # base_url = 'http://qy1.sfda.gov.cn/datasearchcnda/face3/search.jsp?tableId=25&State=1&bcId=152904713761213296322795806604&tableName=TABLE25&viewtitleName=COLUMN167&viewsubTitleName=COLUMN821,COLUMN170,COLUMN166&curstart='
        base_url = 'https://www.guahao.com/hospital/30/%E6%B9%96%E5%8D%97/266/%E5%A8%84%E5%BA%95/p'
        for page in range(1, 2):  # 共11052页
            url = base_url + str(page)
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page})

    def parse(self, response):
        # result = response.xpath('//td[@height="30"]//a').extract()
        result = response.text
        print(result)
