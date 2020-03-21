# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# 百度
class YiyaoBaiduItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    med_name = scrapy.Field()
    med_url = scrapy.Field()
    med_intro = scrapy.Field()
    med_type = scrapy.Field()
    med_purp = scrapy.Field()


# 药监局
class YiyaoSfdaItem(scrapy.Item):
    approval_number = scrapy.Field()  # 批准文号
    product_name = scrapy.Field()  # 产品名称
    english_name = scrapy.Field()  # 英文名称
    trade_name = scrapy.Field()  # 商品名
    dosage_form = scrapy.Field()  # 剂型
    specifications = scrapy.Field()  # 规格
    listing_permit_holder = scrapy.Field()  # 上市许可持有人
    production_unit = scrapy.Field()  # 生产单位
    production_address = scrapy.Field()  # 生产地址
    product_category = scrapy.Field()  # 产品类别
    approval_date = scrapy.Field()  # 批准日期
    original_approval_no = scrapy.Field()  # 原批准文号
    drug_standard_code = scrapy.Field()  # 药品本位码
    remarks_drug_standard_code = scrapy.Field()  # 药品本位码备注


# 中国医院排行榜
class YiyaoHospRankItem(scrapy.Item):
    hos_name = scrapy.Field()  # 医院名称
    hos_level = scrapy.Field()  # 医院等级
    hos_type = scrapy.Field()  # 医院类型
    hos_address = scrapy.Field()  # 医院地址
    hos_info = scrapy.Field()  # 医院详情
    hos_img = scrapy.Field()  # 医院图片


# 健客网
class YiyaoJiankeItem(scrapy.Item):
    tongyongmingcheng = scrapy.Field()
    shangpinmingcheng = scrapy.Field()
    zhuyaochengfen = scrapy.Field()
    xingzhuang = scrapy.Field()
    shiyingzheng = scrapy.Field()
    yongfayongliang = scrapy.Field()
    guigexinghao = scrapy.Field()
    buliangfanying = scrapy.Field()
    jinji = scrapy.Field()
    zhuyishixiang = scrapy.Field()
    ertongyongyao = scrapy.Field()
    laonianhuanzheyongyao = scrapy.Field()
    yunfuyongyao = scrapy.Field()
    yaowuxianghuzuoyong = scrapy.Field()
    yaowuguoliang = scrapy.Field()
    yaoliduli = scrapy.Field()
    yaodaidonglixue = scrapy.Field()
    zhucang = scrapy.Field()
    baozhuang = scrapy.Field()
    youxiaoqi = scrapy.Field()
    zhixingbiaozhun = scrapy.Field()
    pizhunwenhao = scrapy.Field()
    shengchanqiye = scrapy.Field()
    chufangyao = scrapy.Field()
    yaopinwenda = scrapy.Field()
    xiangguanzixun = scrapy.Field()
    yijileimu = scrapy.Field()
    erjileimu = scrapy.Field()


# 用药助手
class YiyaoYongyazhushouItem(scrapy.Item):
    tongyongmingcheng = scrapy.Field()
    shangpinmingcheng = scrapy.Field()
    chengfen = scrapy.Field()
    shiyingzheng = scrapy.Field()
    ertongyongyao = scrapy.Field()
    laonianyongyao = scrapy.Field()
    buliangfanying = scrapy.Field()
    jinji = scrapy.Field()
    zhuyishixiang = scrapy.Field()
    yaowuxianghuzuoyong = scrapy.Field()
    yaolizuoyong = scrapy.Field()
    yaodaidonglixue = scrapy.Field()
    yaowuguoliang = scrapy.Field()
    huanzhejiaoyu = scrapy.Field()
    yaowufenlei = scrapy.Field()
    xingzhuang = scrapy.Field()
    zhucang = scrapy.Field()
    baozhuang = scrapy.Field()
    youxiaoqi = scrapy.Field()
    zhixingbiaozhun = scrapy.Field()
    shengchanqiye = scrapy.Field()
    yongfayongliang = scrapy.Field()
    chaoshuomingshuyongyao = scrapy.Field()
    chaoshuomingshushiyingzheng = scrapy.Field()
    yunfuyongyao = scrapy.Field()
    xiudingjinzheng = scrapy.Field()
    yaowujierong = scrapy.Field()
    zhishiyanshen = scrapy.Field()
    yaowuguoliangjijiejiu = scrapy.Field()
    yunfujiburuqiweixianfenji = scrapy.Field()


