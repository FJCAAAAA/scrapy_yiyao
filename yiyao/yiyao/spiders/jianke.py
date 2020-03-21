#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : yongyaozhushou.py
@Author: Fengjicheng
@Date  : 2020/3/17
@Desc  :  健客网药品数据爬取
'''
import re
import scrapy
from yiyao.items import YiyaoJiankeItem


class JiankeSpider(scrapy.Spider):
    name = 'jianke'
    home_page = 'https://search.jianke.com/list-010301.html'
    # home_page = 'https://www.jianke.com/product/1370.html'

    def start_requests(self):
        yield scrapy.Request(url=self.home_page, callback=self.parse)

    # 一级类目
    def parse(self, response):
        yijileimu_list = response.xpath('//div[@class="itemChooseBox"]/h3[@class="no_bd_b"]/a/text()').extract()
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
        yaopin_url_list = response.xpath('//ul[@class="pro-con"]/li//div[@class="pro-botxt"]/p/a[@target="_blank"]/@href').extract()
        for yaopin_url in yaopin_url_list:
            yaopin_url = 'https:' + yaopin_url
            yield scrapy.Request(url=yaopin_url, callback=self.yaopin_parse, meta=date)
        # yaopin_page_list = response.xpath('//div[@class="pages"]/a[position()>2 and position() != last()]/@href').extract()  # 页数显示不全
        next_page = response.xpath('//div[@class="pages"]/a[last()]/@href').extract_first()
        if next_page and 'javascript' not in next_page:
            next_page = 'https:' + next_page
            yield scrapy.Request(url=next_page, callback=self.erji_parse, meta=date)

    # 药品详情
    def yaopin_parse(self, response):
        date = response.meta
        yaopin_dict = {'通用名称': '', '商品名称':'', '主要成份': '', '性 状': '', '适应症/功能主治': '', '用法用量': '',
                       '规格型号': '', '不良反应': '', '禁 忌': '', '注意事项': '', '儿童用药': '', '老年患者用药': '',
                       '孕妇及哺乳期妇女用药': '', '药物相互作用': '', '药物过量': '', '药理毒理': '', '药代动力学': '',
                       '贮 藏': '', '包 装': '', '有 效 期': '', '执行标准': '', '批准文号': '', '生产企业': '',
                       '处方药/OTC': '', '一级类目': date.get('yijileimu'), '二级类目': date.get('erjileimu'),
                       '相关资讯': '', '相关问答': ''}
        sep1 = re.compile('：')
        sep2 = re.compile('【(.*?)】')
        sep3 = re.compile('【.*?】')
        # 商品说明书
        tongyong = response.xpath('//div[@id="b_2_2"]//p[position()=2]/text()').extract_first().strip()
        shangpin = response.xpath('//div[@id="b_2_2"]//p[position()=3]/text()').extract_first().strip()
        chufang_otc = response.xpath('//dl[@class="assort tongyong"]/dd/img/@title').extract_first().strip()
        tongyongmingcheng = sep1.split(tongyong)[1]
        shangpinmingcheng = sep1.split(shangpin)[1]
        yaopin_dict['通用名称'] = tongyongmingcheng
        yaopin_dict['商品名称'] = shangpinmingcheng
        yaopin_dict['处方药/OTC'] = chufang_otc
        other_text_list = response.xpath('//div[@id="b_2_2"]//p//text()').extract()
        other_text = ''.join([value.strip() for value in other_text_list if value.strip() != '\\s' and value.strip() != ''])
        key_list = sep2.findall(other_text)[1:]
        value_list = sep3.split(other_text)[2:]
        if len(key_list) == len(value_list):
            for key, value in zip(key_list, value_list):
                if key_list:
                    yaopin_dict[key] = value
        # 相关咨询、药品问答为Ajax请求，本页面不显示
        zixun_url = 'https://searchapi.jianke.com/api?t=news&wd={}&pn=1&ps=8&read_cache=1'.format(shangpinmingcheng)
        yield scrapy.Request(url=zixun_url, callback=self.zixun_parse, meta=yaopin_dict)

    # 相关资讯
    def zixun_parse(self, response):
        date = response.meta
        qa_dict = []
        for line in response.xpath('//BaseResultNode_News'):  # 返回xml文档，同样使用xpath解析
            question = line.xpath('./NameCN/text()').extract_first()
            answer = line.xpath('./AllBody/text()').extract_first()
            qa_dict.append({'mingcheng': question, 'neirong': answer})
        date['相关资讯'] = qa_dict
        wenda_url = 'https://searchapi.jianke.com/api?t=ask&wd={}&pn=1&ps=8&read_cache=1'.format(date.get('商品名称'))
        yield scrapy.Request(url=wenda_url, callback=self.wenda_parse, meta=date)

    # 药品问答
    def wenda_parse(self, response):
        yaopin_dict = response.meta
        qa_dict = []
        for line in response.xpath('//BaseResultNode_Ask'):  # 返回xml文档，同样使用xpath解析
            question = line.xpath('./NameCN/text()').extract_first()
            answer = line.xpath('./AnswerContent/text()').extract_first()
            qa_dict.append({'mingcheng': question, 'neirong': answer})
        item = YiyaoJiankeItem()
        item['tongyongmingcheng'] = yaopin_dict.get('通用名称')
        item['shangpinmingcheng'] = yaopin_dict.get('商品名称')
        item['zhuyaochengfen'] = yaopin_dict.get('主要成份')
        item['xingzhuang'] = yaopin_dict.get('性 状')
        item['shiyingzheng'] = yaopin_dict.get('适应症/功能主治')
        item['yongfayongliang'] = yaopin_dict.get('用法用量')
        item['guigexinghao'] = yaopin_dict.get('规格型号')
        item['buliangfanying'] = yaopin_dict.get('不良反应')
        item['jinji'] = yaopin_dict.get('禁 忌')
        item['zhuyishixiang'] = yaopin_dict.get('注意事项')
        item['ertongyongyao'] = yaopin_dict.get('儿童用药')
        item['laonianhuanzheyongyao'] = yaopin_dict.get('老年患者用药')
        item['yunfuyongyao'] = yaopin_dict.get('孕妇及哺乳期妇女用药')
        item['yaowuxianghuzuoyong'] = yaopin_dict.get('药物相互作用')
        item['yaowuguoliang'] = yaopin_dict.get('药物过量')
        item['yaoliduli'] = yaopin_dict.get('药理毒理')
        item['yaodaidonglixue'] = yaopin_dict.get('药代动力学')
        item['zhucang'] = yaopin_dict.get('贮 藏')
        item['baozhuang'] = yaopin_dict.get('包 装')
        item['youxiaoqi'] = yaopin_dict.get('有 效 期')
        item['zhixingbiaozhun'] = yaopin_dict.get('执行标准')
        item['pizhunwenhao'] = yaopin_dict.get('批准文号')
        item['shengchanqiye'] = yaopin_dict.get('生产企业')
        item['chufangyao'] = yaopin_dict.get('处方药/OTC')
        item['yaopinwenda'] = qa_dict
        item['xiangguanzixun'] = yaopin_dict.get('相关资讯')
        item['yijileimu'] = yaopin_dict.get('一级类目')
        item['erjileimu'] = yaopin_dict.get('二级类目')
        yield item


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl jianke'.split())
