# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MarathonbetItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Match(Item):
    id = Field()
    data = Field()
    updated = Field()

class Competition(Item):
    id = Field()
    link = Field()
    updated = Field()
