#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : hospital_ranking.py
@Author: Fengjicheng
@Date  : 2020/3/10
@Desc  : 中国医院排行 http://rank.cn-healthcare.com/hospital
'''
import scrapy
import json
from yiyao.items import YiyaoHospRankItem


class HospRank(scrapy.Spider):
    name = 'hospital_ranking'
    url = 'http://rank.cn-healthcare.com/hospital/search/{}/10?hosname=&level=&hos_count_start=&hos_count_end=&province={}&city=&type=&sortby=hos_level'
    hosp_url = 'http://rank.cn-healthcare.com/hospital/{}'

    def start_requests(self):
        province_list = ['北京', '天津', '上海', '重庆', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '江苏', '浙江',
                    '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', '海南', '四川', '贵州',
                    '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '香港', '澳门', '台湾']
        # province_list = ['香港', '西藏']
        for province in province_list:
            page = 1
            url = self.url.format(page, province)
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page, 'province': province})

    def parse(self, response):
        page = response.meta.get('page')
        province = response.meta.get('province')
        text = json.loads(response.text)
        content_list = text.get('content')
        if content_list:
            for content in content_list:
                hos_id = content.get('id')
                yield scrapy.Request(url=self.hosp_url.format(hos_id), callback=self.parse_hosp, meta=content)
            page += 1
            url = self.url.format(page, province)
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page, 'province': province})

    def parse_hosp(self, response):
        img_url = response.xpath('//div[@class="img-box"]/img/@src').extract_first()
        item = YiyaoHospRankItem()
        item['hos_name'] = response.meta.get('hos_name')
        item['hos_level'] = response.meta.get('hos_levl')
        item['hos_type'] = response.meta.get('type')
        item['hos_address'] = response.meta.get('address')
        item['hos_info'] = response.meta.get('hos_info')
        item['hos_img'] = img_url
        yield item


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute("scrapy crawl hospital_ranking".split())