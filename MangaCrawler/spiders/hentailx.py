# -*- coding: utf-8 -*-
import os
import scrapy
from weasyprint import HTML, CSS
import re


class HentailxSpider(scrapy.Spider):
    name = 'hentailx'
    allowed_domains = ['hentailx.com']
    start_urls = ['http://www.hentailx.com']

    def __init__(self, url, output_directory, chapter, **kwargs):
        super().__init__(**kwargs)

        self.start_urls.append(url)
        self.output_directory = output_directory
        self.chapter = chapter.lower()
        self.chapter_urls = []
        self.chapter_titles = []

    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        urls = response.css("div#list-chap > div.item_chap > a::attr(href)")[::-1].extract()
        titles = response.css("div#list-chap > div.item_chap > a::text")[::-1].extract()

        for url in urls:
            yield self.chapter_urls.append(response.urljoin(url))

        for title in titles:
            yield self.chapter_titles.append(title)

        # Follow pagination link
        has_next_page_icon = response.css("div#list-chap > div.item_chap > nav.pagerhamtruyen > ul.pagination > li > a > span.glyphicon").extract_first()
        if has_next_page_icon:
            next_page_url = response.css("div#list-chap > div.item_chap > nav.pagerhamtruyen > ul.pagination > li:last-child > a::attr(href)").extract_first()
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            next_page_url = response.css("div#list-chap > div.item_chap > nav.pagerhamtruyen > ul.pagination > li.active + li > a::attr(href)").extract_first()
            if next_page_url:
                next_page_url = response.urljoin(next_page_url)
                yield scrapy.Request(url=next_page_url, callback=self.parse)

        if self.chapter:
            if "-" in self.chapter:
                chapters = self.chapter.split("-")
                chapter_begin, chapter_end = self.get_chapter_index(chapters[0], chapters[1], self.chapter_titles)
                self.chapter_urls = self.chapter_urls[chapter_begin:] if chapter_end == -1 else self.chapter_urls[
                                                                                      chapter_begin:chapter_end]
            else:
                chapter_index = self.get_chapter_index(self.chapter, self.chapter, self.chapter_titles)
                self.chapter_urls = [self.chapter_urls[chapter_index[0]]]

        print("{0} chapter(s) was founded!".format(len(self.chapter_urls)))

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        for chapter_url in self.chapter_urls:
            yield scrapy.Request(url=chapter_url, callback=self.parse_details)

    def parse_details(self, response):
        file_name = response.css("div#chapter-detail li.reading-chapter > a::text").extract_first()
        file_name = re.sub(">|<|:|\"|/|\|||\?|\*", "", file_name).strip() + ".pdf"

        print(file_name)

        html_string = response.css("div#content_chap").extract_first()
        css = CSS(string='''
            @page {
                size: Letter;
                margin: 0in 0in 0in 0in;
            }

            img {
                height: 100%;
                width: 100%;
                max-height: 1060px;
                max-width: 800px;
            }
        ''')
        html = HTML(string=html_string)
        html.write_pdf(os.path.join(self.output_directory, file_name), stylesheets=[css])
        print("{0} .Done.".format(file_name))

    def get_chapter_index(self, chapter_begin, chapter_end, chapter_titles):
        start, end = 0, -1

        for index, value in enumerate(chapter_titles):
            if any(x in value.lower() for x in
                   ("chap " + chapter_begin, "chapter " + chapter_begin, "episode " + chapter_begin)):
                start = index
                break

        if chapter_begin == chapter_end:
            end = start + 1
        elif chapter_end == "end":
            end = -1
        else:
            for index, value in enumerate(chapter_titles):
                if any(x in value.lower() for x in
                       ("chap " + chapter_end, "chapter " + chapter_end, "episode " + chapter_end)):
                    end = index + 1
                    break

        return start, end