#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : yaojianju.py
@Author: Fengjicheng
@Date  : 2020/3/31
@Desc  : 药监局药品数据爬取 通过app接口
'''
import scrapy
import json
from yiyao.items import YiyaoYaojianjuJiBenItem
from yiyao.items import YiyaoYaojianjuTeGuanItem


class YaojianjuSpider(scrapy.Spider):
    # name = 'yaojianju_jiben'  # 国家基本药物（2018年版）
    name = 'yaojianju_teguan'  # 特管药品
    list_url = 'http://mobile.nmpa.gov.cn/datasearch/QueryList?tableId={}&searchF=Quick%20SearchK&pageIndex={}&pageSize=15'
    med_url = 'http://mobile.nmpa.gov.cn/datasearch/QueryRecord?tableId={}&searchF=ID&searchK={}'
    cate = {'jiben': {'tableId': 138, 'page': 46}, 'teguan': {'tableId': 102, 'page': 26}}
    headers = {
        'Host': 'mobile.nmpa.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cookie': 'JSESSIONID=058367C53EBBA259C0B5DFB68D144B02.7; tuNQaYE2WCOr80T=41ShNN0UXW1KC74m9krX0hdY_7ocENNATw_VdgUi8g88xLfzokmz3aA4Lp2_34PYWwHrsRVXWni910GSVrU2sTW37Fp08t37EJZEjhyw7wlTs3eOU3lS_DQa19..vLfCLyt8NXapdazXa5c8QxmMAPtGISnJI8yYOIh1qVqY6HXkiaecB3EY9JJWKb_d9pU2WiBxc4bSxBj_byNfOPBGsd3lWHULshdkGmtsQb98TtPTmDGScDOaTuI.n1vOO8er7OxCLI1bXzR5qBXPrvbZlGntl; tuNQaYE2WCOr80S=fjQ77YloJUQ9tBC1LJPr2o_6XnH5YX3MVDwAGFhI6Fg9AZq_9yWgrZnvtZ8bf0IT',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    def start_requests(self):
        if self.name == 'yaojianju_jiben':
            page = self.cate.get('jiben').get('page')
            tableid = self.cate.get('jiben').get('tableId')
        elif self.name == 'yaojianju_teguan':
            page = self.cate.get('teguan').get('page')
            tableid = self.cate.get('teguan').get('tableId')
        for num in range(1, page+1):
            url = self.list_url.format(tableid, num)
            yield scrapy.Request(url=url, callback=self.parse, meta={'tableId': tableid}, headers=self.headers)

    def parse(self, response):
        tableid = response.meta.get('tableId')
        res_list = json.loads(response.text)
        if res_list:
            for res in res_list:
                url = self.med_url.format(tableid, res.get('ID'))
                yield scrapy.Request(url=url, callback=self.med_parse, meta={'tableId': tableid}, headers=self.headers)

    def med_parse(self, response):
        tableid = int(response.meta.get('tableId'))
        res_list = json.loads(response.text)
        med_dict = {}
        for res in res_list:
            med_dict[res.get('NAME')] = res.get('CONTENT')
        if tableid == 138:
            item = YiyaoYaojianjuJiBenItem()
            item['yijimulu'] = med_dict.get('一级目录')
            item['erjimulu'] = med_dict.get('二级目录')
            item['sanjimulu'] = med_dict.get('三级目录')
            item['beizhu'] = med_dict.get('备注')
            item['yingwenming'] = med_dict.get('英文名')
            item['jixingguige'] = med_dict.get('剂型、规格')
            item['pinzhongmingcheng'] = med_dict.get('品种名称')
            yield item
        elif tableid == 102:
            item = YiyaoYaojianjuTeGuanItem()
            item['zhongwenming'] = med_dict.get('中文名')
            item['yingwenming'] = med_dict.get('英文名')
            item['cas'] = med_dict.get('CAS号')
            item['beizhu'] = med_dict.get('备注')
            item['yaopinleibie'] = med_dict.get('药品类别')
            item['mulubanben'] = med_dict.get('目录版本')
            yield item

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl yaojianju_jiben'.split())