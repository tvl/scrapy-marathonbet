# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from marathonbet.items import Match
from urllib.parse import parse_qs
from datetime import date, datetime, timezone, timedelta
from stem import Signal
from stem.control import Controller
import csv
from time import sleep, time


class LineSpider(Spider):
    name = "line"
    allowed_domains = ['marathonbet.ru', 'marathonbet.com']
    today  = date.today()
    tomorrow  = date.today()+timedelta(days=1)
    start_urls = [
            #'https://www.marathonbet.ru/su/?cpcids=all',
            'https://www.marathonbet.ru/su/popular/Football+-+11?interval=H24'
        ]

    """
    def start_requests(self):
        start_url = 'https://www.marathonbet.ru/su/popular/Football+-+11?interval=ALL_TIME'
        request = Request(url=start_url, callback=self.parse_competition)
        yield request

    """
    def start_requests(self):
        request = Request(url=self.start_urls[0], callback=self.parse_index)
        yield request
        #request = Request(url=self.start_urls[1], callback=self.parse_competition)
        #yield request

    """
    def start_requests(self):
        base_url = 'https://www.marathonbet.ru/su/betting/'
        with open('competitions.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                request = Request(url=base_url+row['link'], callback=self.parse_competition)
                request.meta['proxy'] = 'http://127.0.0.1:8118'
                yield request
    """

    def parse_index(self, response):
        base_url = 'https://www.marathonbet.ru'
        #links = response.xpath('//div[@id="leftMenuLinks"]/a/@href').extract()
        links = response.xpath('//div[@class="hidden-links"]//@href').extract()
        links = [link for link in links if '/Football/' in link]
        links = [link for link in links if link.count('/') == 4]
        links = [link for link in links if (not 'Women' in link) and (not 'Outright' in link)]
        self.logger.info('Links count: {}'.format(len(links)))
        for l in links:
            request = Request(url=base_url+l+'?interval=H24', callback=self.parse_competition)
            yield request

    def parse_competition(self, response):
        base_url = 'https://www.marathonbet.com/su/betting/'
        events = response.xpath('//span[@class="event-more-view"]/text()').extract()
        links = response.xpath('//div[@class="bg coupon-row"]/@data-event-path').extract()
        links = [link for link in links if (not 'U-19' in link) and (not 'U-20' in link) and (not 'U-20' in link) and (not 'U-23' in link) \
                 and (not 'Spain/Tercera' in link) and (not 'England/National' in link) and (not 'Serie+D' in link)]
        for l, e in zip(links, events):
            if int(e) > 80:
                request = Request(url=base_url+l, callback=self.parse_match)
                yield request
            else:
                self.logger.info('Skip: {}'.format(base_url+l))

    def parse_match(self, response):
        lines = response.xpath('//td[contains(@class,"height-column-with-price")]/@data-sel').extract()
        for l in lines:
            item = Match()
            item['id'] = response.xpath('//div[@class="bg coupon-row"]//@data-event-treeid').extract_first()
            item['data'] = l
            item['updated'] = datetime.utcnow().isoformat(' ')
            yield item
