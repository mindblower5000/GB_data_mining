# -*- coding: utf-8 -*-
import scrapy
from ico_parser.items import IcoParserItem, PersonItem

from scrapy.http import HtmlResponse
from pymongo import MongoClient
from time import sleep

CLIENT = MongoClient('localhost', 27017)
MONGO_DB = CLIENT.ico
COLLECTION = MONGO_DB.icobench


class IcobenchSpider(scrapy.Spider):
    name = 'icobench'
    allowed_domains = ['icobench.com']
    start_urls = ['https://icobench.com/icos?filterSort=name-asc']

    def ico_page_parse(self, response):
        # sleep(0.5)

        data_persons = response.css('div#team.tab_content div.row')
        # tmp_team = []
        # for item in data_persons[0].css('div.col_3'):
        #     tmp_person = PersonItem(
        #         source_page_url=item.css('a.image::attr(href)').get(),
        #         name=item.css('h3::text').get(),
        #         links=item.css('div.socials a::attr(href)').extract()
        #     )
        #     final_strict = {'person': tmp_person, 'position': item.css('h4::text').get()}
        #     tmp_team.append(final_strict)

        try:

            team = [
                {
                    'person': PersonItem(
                        source_page_url=item.css('a.image::attr(href)').get(),
                        name=item.css('h3::text').get(),
                        links=item.css('div.socials a::attr(href)').extract()),
                    'position': item.css('h4::text').get()}
                for item in data_persons[0].css('div.col_3')
            ]
        except IndexError as e:
            print(e)
            team = []

        try:

            advisors = [
                {
                    'person': PersonItem(
                        source_page_url=item.css('a.image::attr(href)').get(),
                        name=item.css('h3::text').get(),
                        links=item.css('div.socials a::attr(href)').extract()),
                    'position': item.css('h4::text').get()}
                for item in data_persons[1].css('div.col_3')
            ]
        except IndexError as e:
            print(e)
            advisors = []

        data = {'name': response.css('div.ico_information div.name h1::text').get(),
                'slogan': response.css('div.ico_information div.name h2::text').get(),
                'description': response.css('div.ico_information p::text').get(),
                'team': team,
                'advisors': advisors,
                }

        item = IcoParserItem(**data)

        yield item

    def parse(self, response):

        next_page = response.css('div.ico_list div.pages a.next::attr(href)').get()
        ico_pages = response.css('div.ico_list td.ico_data div.content a.name::attr(href)').extract()

        for page in ico_pages:
            tmp = response.follow(page, callback=self.ico_page_parse)
            yield response.follow(page, callback=self.ico_page_parse)

            # sleep(1)

        yield response.follow(next_page, callback=self.parse)

        print(next_page)