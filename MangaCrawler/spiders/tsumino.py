# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver


class TsuminoSpider(scrapy.Spider):
    name = 'tsumino'
    allowed_domains = ['tsumino.com']
    start_urls = ['http://tsumino.com/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Firefox()

    def parse(self, response):
        self.driver.get('https://www.example.org/abc')

        while True:
            try:
                next = self.driver.find_element_by_xpath('//*[@id="BTN_NEXT"]')
                next.click()
            except:
                break
        self.driver.close()

    def parse2(self, response):
        print('you are here!')
