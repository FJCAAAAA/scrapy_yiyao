#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : yiyaowang.py
@Author: Fengjicheng
@Date  : 2020/3/25
@Desc  : 1药网药品数据爬取 https://www.111.com.cn/
'''
import scrapy
import re
import json
from yiyao.items import YiyaoYiyaowangItem


class YiyaoWangSpider(scrapy.Spider):
    name = 'yiyaowang'
    home_page = 'https://www.111.com.cn/categories/953710-j1'
    wenda_url = 'https://www.111.com.cn/interfaces/review/questionlist/html.action?goodsId={}&pageIndex={}&type=-1'

    def start_requests(self):
        yield scrapy.Request(url=self.home_page, callback=self.parse)
        # yield scrapy.Request(url='https://www.111.com.cn/product/971865.html', callback=self.yaopin_parse, meta={'yijileimu': '滋补调养', 'erjileimu': '补肾'})
        # yield scrapy.Request(url='https://www.111.com.cn/product/50088643.html', callback=self.yaopin_parse,
        #                      meta={'yijileimu': '滋补调养', 'erjileimu': '补肾'})
    # 一级类目
    def parse(self, response):
        yijileimu_list = response.xpath('//div[@class="itemChooseBox"]/h3[@class="no_bd_b"]/a[position()=2]/text()').extract()
        erjileimu_sele_list = response.xpath('//div[@class="itemChooseBox"]/ul[@class="list_ul"]')
        for yijileimu, erjileimu_li in zip(yijileimu_list, erjileimu_sele_list):
            erjileimu_list = erjileimu_li.xpath('./li/a/text()').extract()
            erjileimu_url_list = erjileimu_li.xpath('./li/a/@href').extract()
            for erjileimu, erjileimu_url in zip(erjileimu_list, erjileimu_url_list):
                erjileimu_url = 'https:' + erjileimu_url
                date = {'yijileimu': yijileimu.strip(), 'erjileimu': erjileimu.strip()}
                yield scrapy.Request(url=erjileimu_url, callback=self.erji_parse, meta=date)

    # 二级类目
    def erji_parse(self, response):
        date = response.meta
        yaopin_url_list = response.xpath(
            '//div[@class="itemSearchResult clearfix fashionList"]//li/div[@class="itemSearchResultCon"]/a/@href').extract()
        for yaopin_url in yaopin_url_list:
            yaopin_url = 'https:' + yaopin_url
            yield scrapy.Request(url=yaopin_url, callback=self.yaopin_parse, meta=date)
        next_page = response.xpath('//a[@class="page_next"]/@href').extract_first()
        if next_page and 'javascript' not in next_page:
            next_page = 'https:' + next_page
            yield scrapy.Request(url=next_page, callback=self.erji_parse, meta=date)

    # 药品详情
    def yaopin_parse(self, response):
        date = response.meta
        yaopin_dict = {'通用名称': '', '商品名称': '', '成份': '', '性状': '', '功能主治': '', '适应症': '', '用法用量': '',
                       '规格': '', '不良反应': '', '禁忌': '', '注意事项': '', '药物相互作用': '', '药理毒理': '',
                       '药代动力学': '', '妊娠期妇女及哺乳期妇女用药': '', '儿童用药': '', '老年患者用药': '', '药物过量': '',
                       '贮藏': '', '包装': '', '有效期': '', '批准文号': '', '企业名称': '',
                       '处方药/OTC': '', '一级类目': date.get('yijileimu'), '二级类目': date.get('erjileimu'),
                        '相关问答': []}
        sep1 = re.compile('//www.111.com.cn/product/(\d+).html')
        # 商品说明书
        tr_list = response.xpath('//table[@class="specificationBox"]/tbody/tr[position()>2]')
        if tr_list:
            for tr in tr_list:
                key = tr.xpath('./th/text()').extract_first()
                value_list = tr.xpath('./td//text()').extract()
                if key:
                    yaopin_dict[key.strip(' :').strip('：').strip()] = ''.join(value_list)
        # 处方药
        if response.xpath('//div[@class="toast"]'):
            yaopin_dict['处方药/OTC'] = '处方药'
        else:
            yaopin_dict['处方药/OTC'] = '非处方药'
        # 商品问答为Ajax请求，本页面不显示
        drug_id = sep1.findall(response.url)[0]
        yaopin_dict['drug_id'] = drug_id
        yield scrapy.Request(url=self.wenda_url.format(drug_id, '1'), callback=self.wenda_parse, meta=yaopin_dict)

    # 药品问答
    def wenda_parse(self, response):
        sep1 = re.compile('共(\d+)页')
        sep2 = re.compile('pageIndex=(\d+)&type=-1')
        yaopin_dict = response.meta
        q_list = response.xpath('//dl/dt/text()').extract()
        a_list = response.xpath('//dl/dd/text()').extract()
        for question, answer in zip(q_list, a_list):
            yaopin_dict['相关问答'].append({'mingcheng': question, 'neirong': answer})
        page_num = response.xpath('//ul[@class="pageNavi clearfix"]/li[last()]/text()').extract_first()
        if page_num:
            page_num = int(sep1.findall(page_num)[0])
            for page_id in range(2, page_num+1):
                wenda_url = self.wenda_url.format(yaopin_dict.get('drug_id'), page_id)
                yield scrapy.Request(url=wenda_url, callback=self.wenda_parse, meta=yaopin_dict)

        item = YiyaoYiyaowangItem()
        item['tongyongmingcheng'] = yaopin_dict.get('通用名称')
        item['shangpinmingcheng'] = yaopin_dict.get('商品名称')
        item['chengfen'] = yaopin_dict.get('成份')
        item['xingzhuang'] = yaopin_dict.get('性状')
        if yaopin_dict.get('功能主治'):
            item['gongnengzhuzhi'] = yaopin_dict.get('功能主治')
        else:
            item['gongnengzhuzhi'] = yaopin_dict.get('适应症')
        item['guige'] = yaopin_dict.get('规格')
        item['yongfayongliang'] = yaopin_dict.get('用法用量')
        item['buliangfanying'] = yaopin_dict.get('不良反应')
        item['jinji'] = yaopin_dict.get('禁忌')
        item['zhuyishixiang'] = yaopin_dict.get('注意事项')
        item['yaowuxianghuzuoyong'] = yaopin_dict.get('药物相互作用')
        item['yaoliduli'] = yaopin_dict.get('药理毒理')
        item['yaodaidonglixue'] = yaopin_dict.get('药代动力学')
        item['ertongyongyao'] = yaopin_dict.get('儿童用药')
        item['laonianhuanzheyongyao'] = yaopin_dict.get('老年患者用药')
        item['yunfuyongyao'] = yaopin_dict.get('妊娠期妇女及哺乳期妇女用药')
        item['yaowuguoliang'] = yaopin_dict.get('药物过量')
        item['zhucang'] = yaopin_dict.get('贮藏')
        item['baozhuang'] = yaopin_dict.get('包装')
        item['youxiaoqi'] = yaopin_dict.get('有效期')
        item['pizhunwenhao'] = yaopin_dict.get('批准文号')
        item['shengchanqiye'] = yaopin_dict.get('企业名称')
        item['chufangyao'] = yaopin_dict.get('处方药/OTC')
        item['shangpinwenda'] = yaopin_dict.get('相关问答')
        item['yijileimu'] = yaopin_dict.get('一级类目')
        item['erjileimu'] = yaopin_dict.get('二级类目')
        item['drugid'] = yaopin_dict.get('drug_id')
        yield item


if __name__ == '__main__':
    from scrapy import cmdline

    cmdline.execute('scrapy crawl yiyaowang'.split())
