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
        # For schedule
        self.logger.info('Matches data<<<id,datetime,area,competition,home_team,away_team,home,draw,away,odds,updated')
        for l in links:
            request = Request(url=base_url+l+'?interval=H24', callback=self.parse_competition)
            yield request

    def parse_competition(self, response):
        base_url = 'https://www.marathonbet.com/su/betting/'
        events = response.xpath('//span[@class="event-more-view"]/text()').extract()
        links = response.xpath('//div[@class="bg coupon-row"]/@data-event-path').extract()
        links = [link for link in links if (not 'U-19' in link) and (not 'U-20' in link) and (not 'U-21' in link) and (not 'U-23' in link) \
                 and (not 'Spain/Tercera' in link) and (not 'England/National' in link) and (not 'Serie+D' in link)]
        for l, e in zip(links, events):
            if int(e) > 80:
                request = Request(url=base_url+l, callback=self.parse_match)
                yield request
            else:
                self.logger.info('Skip: {}'.format(base_url+l))

    def parse_match(self, response):
        # For schedule
        monthes = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

        match_id = response.xpath('//div[@class="bg coupon-row"]//@data-event-treeid').extract_first()
        dates_list = response.xpath('//td[contains(@class,"date")]/text()').extract()
        if len(dates_list) < 4:
            date_time = dates_list[0].strip()
        else:
            date_time = dates_list[2].strip()
        #date_time = response.xpath('//td[contains(@class,"date")]/text()').extract()[0].strip()
        dt = datetime.now()
        if len(date_time) == 17: # 27 дек 2021 12:00
            d, month, y, hh_mm = date_time.split(' ')
            m = monthes.index(month.capitalize()) + 1
            hh, mm  = hh_mm.split(':')
            date_time = dt.replace(day = int(d), month = m, year = int(y), hour = int(hh), minute = int(mm), second = 0).isoformat(' ', timespec='seconds')
        elif len(date_time) == 12: # 28 фев 10:00
            d, month, hh_mm = date_time.split(' ')
            m = monthes.index(month.capitalize()) + 1
            hh, mm  = hh_mm.split(':')
            date_time = dt.replace(day = int(d), month = m, hour = int(hh), minute = int(mm), second = 0).isoformat(' ', timespec='seconds')
        elif len(date_time) == 5: # 23:00
            hh, mm = date_time.split(':')
            date_time = dt.replace(hour = int(hh), minute = int(mm), second = 0).isoformat(' ', timespec='seconds')
        home_team, away_team = response.xpath('//a[contains(@class,"member-link")]//span/text()').extract()
        #home_team, away_team = response.xpath('//div[@class="bg coupon-row"]//@data-event-name').extract_first().split(' - ')
        area = response.xpath('//h1[contains(@class,"category-label")]/span/text()').extract()[0].strip('.')
        competition = ' '.join(response.xpath('//h1[contains(@class,"category-label")]/span/text()').extract()[1:])
        home, draw, away = response.xpath('//span[contains(@data-selection-key,"Match_Result")]/text()').extract()
        odds = int(response.xpath('//span[contains(@class,"event-more-view")]/text()').extract_first())
        updated = datetime.utcnow().isoformat(' ', timespec='seconds')
        self.logger.info(f'Matches data<<<{match_id},{date_time},{area},{competition},{home_team},{away_team},{home},{draw},{away},{odds},{updated}')
        # For odds
        lines = response.xpath('//td[contains(@class,"height-column-with-price")]/@data-sel').extract()
        for l in lines:
            item = Match()
            item['id'] = response.xpath('//div[@class="bg coupon-row"]//@data-event-treeid').extract_first()
            item['data'] = l
            item['updated'] = datetime.utcnow().isoformat(' ', timespec='seconds')
            yield item
