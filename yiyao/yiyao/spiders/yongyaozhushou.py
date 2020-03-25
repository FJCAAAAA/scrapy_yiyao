#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : yongyaozhushou.py
@Author: Fengjicheng
@Date  : 2020/3/19
@Desc  :  用药助手药品数据爬取
'''
import scrapy
import re
import json
from yiyao.settings import COOKIE
from yiyao.items import YiyaoYongyazhushouItem


class YongyaozhushouSpider(scrapy.Spider):
    name = 'yongyaozhushou'
    home_page = 'http://drugs.dxy.cn/'
    # cookie = COOKIE
    headers = {
        'Connection': 'keep-alive',  # 保持链接状态
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        # 'Referer': 'http://drugs.dxy.cn',
        # 'Host': 'drugs.dxy.cn',
        'Cookie': 'Hm_lvt_d1780dad16c917088dd01980f5a2cfa7=1584936925,1584936926,1584946850,1584946878; __utma=129582553.1331474424.1576140003.1585012175.1585031028.16; __utmz=129582553.1584936925.11.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __auc=ff34aa3d16ef943db072bc867b0; Hm_lvt_8a6dad3652ee53a288a11ca184581908=1576140037; route=76fe8badbf970cea48a83fee22e3ae12; DRUGSSESSIONID=81592B7741DAEF371E655197951ED8CE-n1; Hm_lpvt_d1780dad16c917088dd01980f5a2cfa7=1585032391; __utmc=129582553; _ga=GA1.2.1254399796.1584946847; _gid=GA1.2.1312381115.1584946847; CLASS_CASTGC=5d0474c42cdf1e0ba49a5e34b1c996c0ace79e4eaabce4e0f7798e7ba243cfa9ae30acbc4cd65e4f8bbca60a1b44951ea6f2c4fcb4189cc3c5d90fda39579f10bc56d2a439dfed4b9d7809bb53af8b6f8f9eb0842ff45ba218077f099ddbbfbf189305a6dd8c3e98b3335e6ebe3a30d84b9ed4961880d2f795b4308ab3432855d74655fabd43942a3ad0f9d7654d0c2637310760e4cfa15ea8a9fdf021e77fa8f3632399a0d00e24a3dd18e3a9dcbffcdda9ff5590987d2dd326af4108ea024dcccd6e7244bee181fbc2dec2e6cf05933890a7a6ed02e2495f31620beefe6539a266453bcfbafc506f14f058a911a56c96d0d76966620aa5bc36767932e42006; JUTE_BBS_DATA=75f6738bd1b56ba84f3e090c7dda4bb1f54adbc97de2afcc24c20fa689dc5e68a1ff7dba6703bf1e85c0e274941b48e00126b634591fd21d6428f803470f25782887660fd424d853878d52a0e109877e; __asc=66079bce1710b361cc77d8dbb44; __utmb=129582553.5.10.1585031028; __utmt=1'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.home_page, headers=self.headers, callback=self.parse)
        # url = 'http://drugs.dxy.cn/category/1001.htm'
        # yield scrapy.Request(url=url, headers=self.headers, callback=self.erji_parse)

    def parse(self, response):
        erjileimu_list = response.xpath('//div[@class="common_main ml279"]/div[@name="cate_div"]//li/h3/a/@href').extract()
        for erjileimu in erjileimu_list:
            url = 'http:' + erjileimu
            yield scrapy.Request(url=url, headers=self.headers, callback=self.erji_parse)

    def erji_parse(self, response):
        # print(response.text)
        sep1 = re.compile('//drugs.dxy.cn/drug/(.*?).htm')
        sep2 = re.compile('\?')
        detail_url = 'https://drugs.dxy.cn/api/v2/detail'
        med_url_list = response.xpath('//div[@class="m49 result"]//li//h3/a/@href').extract()
        for med_url in med_url_list:
            # med_url = 'http:' + med_url
            drug_id = sep1.findall(med_url)[0]
            date = {
                'wxxcx': 'true',
                'sessionId': 'eyJhcHBJZCI6MTI2MTgyODY1NywiZHh5VXNlck5hbWUiOiJkeHlfNmFpZHN2ZHEiLCJub25jZSI6IjR6M1laM3p4NGZJRThPcFciLCJwcm9maWxlSWQiOjY5MjE2NTAwLCJzaWduIjoiMDcyOGQwNGM2MDk5ZWFmYzU3NDEzZmE5OTE2MGQxZjY0Y2UxMGJiOCIsInNpbXVpZCI6NjgwNzI2ODk1ODA4ODc1MzM5OCwidGVhbUlkIjo0ODUsInRpbWVzdGFtcCI6MTU4NDk5NzI1NX0',
                'category': '2',
                'id': drug_id
            }
            yield scrapy.FormRequest(url=detail_url, formdata=date, callback=self.yaopin_parse, dont_filter=True)
        # print(response.url)
        next_page = response.xpath('//div[@class="pagination"]//a[@title="下一页"]/@href').extract_first()
        if next_page:
            next_page = ''.join([sep2.split(response.url)[0], next_page])
            yield scrapy.Request(url=next_page, headers=self.headers, callback=self.erji_parse)

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
    cmdline.execute('scrapy crawl yongyaozhushou'.split())






