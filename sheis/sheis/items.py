# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SheisItem(scrapy.Item):
    # define the fields for your item here like:
    index = scrapy.Field()
    name = scrapy.Field()
    location = scrapy.Field()
    open_time = scrapy.Field()
    price = scrapy.Field()
    tel = scrapy.Field()
    collections = scrapy.Field()
    images = scrapy.Field()
    pass
