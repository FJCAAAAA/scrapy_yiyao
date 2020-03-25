#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : yongyaozhushou.py
@Author: Fengjicheng
@Date  : 2020/3/19
@Desc  :  用药助手药品数据爬取，通过微信小程序
'''
import scrapy
import re
import json
from yiyao.items import YiyaoYongyazhushouItem


class YongyaozhushouSpider(scrapy.Spider):
    name = 'yongyaozhushou_weixin'
    home_page = 'https://drugs.dxy.cn/api/open/category/list?sessionId={}'
    sessionId = 'eyJhcHBJZCI6MTI2MTgyODY1NywiZHh5VXNlck5hbWUiOiJkeHlfNmFpZHN2ZHEiLCJub25jZSI6InlvSEpRbjNtWHRZWU45MjAiLCJwcm9maWxlSWQiOjY5MjE2NTAwLCJzaWduIjoiMTNlOWUyNTQ4OGE5OTRkYzZmZDIxNmMwOWY0NjE0MTAxNjcxYzY5ZiIsInNpbXVpZCI6NjgwNzI2ODk1ODA4ODc1MzM5OCwidGVhbUlkIjo0ODUsInRpbWVzdGFtcCI6MTU4NTA0MzcxOX0'


    def start_requests(self):
        yield scrapy.Request(url=self.home_page.format(self.sessionId),  callback=self.parse)

    def parse(self, response):
        sec_page = 'https://drugs.dxy.cn/api/open/category/drug?sessionId={}&categoryId={}&page={}'
        all_med_dict = json.loads(response.text)
        # print(all_med_dict)
        first_cate_list = all_med_dict.get('results').get('items')
        if first_cate_list:
            for first_cate in first_cate_list:
                sec_cate_list = first_cate.get('childCategoryList')
                if sec_cate_list:
                    for sec_cate in sec_cate_list:
                        sec_cate_id = sec_cate.get('id')
                        if sec_cate_id:
                            for page in range(1, 9):
                                url = sec_page.format(self.sessionId, sec_cate_id, page)
                                yield scrapy.Request(url=url, callback=self.erji_parse)
                            # print(sec_cate_id)

    def erji_parse(self, response):
        detail_url = 'https://drugs.dxy.cn/api/v2/detail'
        sec_med_dict = json.loads(response.text)
        sec_med_list = sec_med_dict.get('results').get('items')
        if sec_med_list:
            for med in sec_med_list:
                drug_id = med.get('id')
                date = {
                    'wxxcx': 'true',
                    'sessionId': str(self.sessionId),
                    'category': '2',
                    'id': str(drug_id)
                }
                # print('药品id {}'.format(drug_id))
                yield scrapy.FormRequest(url=detail_url, formdata=date, callback=self.yaopin_parse, dont_filter=True)

    def yaopin_parse(self, response):
        item = YiyaoYongyazhushouItem()
        sep1 = re.compile('<.*?>')
        sep2 = re.compile('\n')
        res_dict = json.loads(response.text)
        if res_dict.get('data'):
            med_dict = {}
            for field in res_dict.get('data'):
                key = field.get('cnName')
                value = field.get('value')
                if key:
                    med_dict[key] = sep1.sub('', value)
            # print(med_dict)
            item['tongyongmingcheng'] = med_dict.get('通用名')
            item['shangpinmingcheng'] = med_dict.get('商品名')
            item['chengfen'] = med_dict.get('成份')
            item['shiyingzheng'] = med_dict.get('适应症')
            item['ertongyongyao'] = med_dict.get('儿童用药')
            item['laonianyongyao'] = med_dict.get('老年用药')
            item['buliangfanying'] = med_dict.get('不良反应')
            item['jinji'] = med_dict.get('禁忌')
            item['yaowuxianghuzuoyong'] = med_dict.get('药物相互作用')
            item['yaolizuoyong'] = med_dict.get('药理作用')
            item['yaodaidonglixue'] = med_dict.get('药代动力学')
            item['yaowuguoliang'] = med_dict.get('药物过量')
            item['huanzhejiaoyu'] = med_dict.get('患者教育')
            item['yaowufenlei'] = med_dict.get('药物分类')
            item['xingzhuang'] = med_dict.get('性状')
            item['zhucang'] = med_dict.get('贮藏')
            item['baozhuang'] = med_dict.get('包装')
            item['youxiaoqi'] = med_dict.get('有效期')
            item['zhixingbiaozhun'] = med_dict.get('执行标准')
            item['shengchanqiye'] = med_dict.get('生产企业')
            item['yongfayongliang'] = med_dict.get('用法用量')
            item['chaoshuomingshuyongyao'] = med_dict.get('超说明书用药')
            item['chaoshuomingshushiyingzheng'] = med_dict.get('超说明书适应症')
            item['yunfuyongyao'] = med_dict.get('孕妇及哺乳期妇女用药')
            item['yaowujierong'] = med_dict.get('药物警戒')
            item['zhishiyanshen'] = med_dict.get('知识延伸')
            item['yaowuguoliangjijiejiu'] = med_dict.get('药物过量及解救')
            item['yunfujiburuqiweixianfenji'] = med_dict.get('孕妇及哺乳期危险分级')
            yield item


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl yongyaozhushou_weixin'.split())







