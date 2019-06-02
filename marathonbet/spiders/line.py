# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from marathonbet.items import Match
from urllib.parse import parse_qs
from datetime import date, datetime, timezone, timedelta


class LineSpider(Spider):
    name = "line"
    allowed_domains = ['marathonbet.ru']
    today  = date.today()
    tomorrow  = date.today()+timedelta(days=1)
    start_urls = [
            'https://www.marathonbet.ru'
        ]

    def start_requests(self):
        for u in self.start_urls:
            request = Request(url=u, callback=self.parse_index)
            request.meta['proxy'] = 'http://127.0.0.1:8118'
            yield request

    def parse_index(self, response):
        base_url = 'https://www.marathonbet.ru'
        links = response.xpath('//div[@id="leftMenuLinks"]/a/@href').extract()
        links = [link for link in links if '/Football/' in link]
        for l in links:
            request = Request(url=base_url+l, callback=self.parse_competition)
            request.meta['proxy'] = 'http://127.0.0.1:8118'
            yield request

    def parse_competition(self, response):
        base_url = 'https://www.marathonbet.ru'
        links = response.xpath('//div[@class="bg coupon-row"]/@data-event-page').extract()
        for l in links:
            request = Request(url=base_url+l, callback=self.parse_match)
            request.meta['proxy'] = 'http://127.0.0.1:8118'
            yield request

    def parse_match(self, response):
        lines = response.xpath('//td[contains(@class,"height-column-with-price")]/@data-sel').extract()
        for l in lines:
            item = Match()
            item['id'] = response.xpath('//div[@class="bg coupon-row"]//@data-event-treeid').extract_first()
            item['data'] = l
            item['updated'] = datetime.utcnow().isoformat(' ')
            yield item
