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
            'https://www.marathonbet.ru/su/?cpcids=all'
        ]
    handle_httpstatus_list = [403, 451]
    controller = None

    def change_tor_ip(self):
        if self.controller.is_newnym_available():
            self.logger.info('Tor change ip of exitnode')
            self.controller.signal(Signal.NEWNYM)
        else:
            self.logger.info('Tor wait for {}s'.format(self.controller.get_newnym_wait()))

    def start_requests(self):
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate(password="KjujgtlbcN")
        #self.logger.info('Tor version: {}', self.controller.get_version())
        for u in self.start_urls:
            request = Request(url=u, callback=self.parse_index)
            #request.meta['proxy'] = 'http://127.0.0.1:8118'
            yield request
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
        if response.status in [403, 451]:
            self.change_tor_ip()
            self.logger.info('Sleep for 5s')
            sleep(5)
            yield Request(url=response.url, callback=self.parse_index)
        else:
            base_url = 'https://www.marathonbet.ru'
            #links = response.xpath('//div[@id="leftMenuLinks"]/a/@href').extract()
            links = response.xpath('//div[@class="hidden-links"]//@href').extract()
            links = [link for link in links if '/Football/' in link]
            for l in links:
                request = Request(url=base_url+l, callback=self.parse_competition)
                #request.meta['proxy'] = 'http://127.0.0.1:8118'
                yield request

    def parse_competition(self, response):
        if response.status in [403, 451]:
            self.change_tor_ip()
            self.logger.info('Sleep for 5s')
            sleep(5)
            yield Request(url=response.url, callback=self.parse_competition)
        else:
            base_url = 'https://www.marathonbet.ru/su/betting/'
            links = response.xpath('//div[@class="bg coupon-row"]/@data-event-path').extract()
            for l in links:
                request = Request(url=base_url+l, callback=self.parse_match)
                #request.meta['proxy'] = 'http://127.0.0.1:8118'
                yield request

    def parse_match(self, response):
        if response.status in [403, 451]:
            self.change_tor_ip()
            self.logger.info('Sleep for 5s')
            sleep(5)
            yield Request(url=response.url, callback=self.parse_match)
        else:
            lines = response.xpath('//td[contains(@class,"height-column-with-price")]/@data-sel').extract()
            for l in lines:
                item = Match()
                item['id'] = response.xpath('//div[@class="bg coupon-row"]//@data-event-treeid').extract_first()
                item['data'] = l
                item['updated'] = datetime.utcnow().isoformat(' ')
                yield item
