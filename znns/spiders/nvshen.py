# -*- coding: utf-8 -*-
import os

import scrapy
from znns.items import ZnnsItem


class NvshenSpider(scrapy.Spider):
    name = 'znns'
    allowed_domains = ['']
    start_urls = ['https://www.nvshens.com/rank/sum/']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    }

    # 排行榜循环
    def parse(self, response):
        exp = u'//div[@class="pagesYY"]//a[text()="下一页"]/@href'  # 下一页的地址
        _next = response.xpath(exp).extract_first()
        # next_page = os.path.join("https://www.nvshens.com/", _next)
        yield scrapy.Request(response.urljoin(_next), callback=self.parse, dont_filter=True)

        for p in response.xpath('//li[@class="rankli"]//div[@class="rankli_imgdiv"]//a/@href').extract():  # 某一个妹子简介详情页
            item_page = "https://www.nvshens.com/" + p + "album/"  # 拼接 全部相册页面
            yield scrapy.Request(item_page, callback=self.parse_item, dont_filter=True)

    # 单个介绍详情页
    def parse_item(self, response):
        item = ZnnsItem()
        # 某个人的名字，也就是一级文件夹
        item['name'] = response.xpath('//div[@id="post"]//div[@id="map"]//div[@class="browse"]/a[2]/@title').extract()[
            0].strip()

        exp = '//li[@class="igalleryli"]//div[@class="igalleryli_div"]//a/@href'
        for p in response.xpath(exp).extract():  # 遍历妹子全部相册
            item_page = "https://www.nvshens.com/" + p  # 拼接图片的详情页
            yield scrapy.Request(item_page, meta={'item': item}, callback=self.parse_item_details, dont_filter=True)

    # 图片主页，开始抓取
    def parse_item_details(self, response):
        item = response.meta['item']
        item['image_urls'] = response.xpath('//ul[@id="hgallery"]//img/@src').extract()  # 图片链接
        item['albumname'] = response.xpath('//h1[@id="htilte"]/text()').extract()[0].strip()  # 二级文件夹
        yield item

        new_url = response.xpath('//div[@id="pages"]//a[text()="下一页"]/@href').extract_first()  # 翻页
        new_url = "https://www.nvshens.com/" + new_url
        if new_url:
            yield scrapy.Request(new_url, meta={'item': item}, callback=self.parse_item_details, dont_filter=True)
