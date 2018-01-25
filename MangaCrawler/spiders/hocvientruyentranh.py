# -*- coding: utf-8 -*-
import os
import scrapy
from weasyprint import HTML, CSS
import re


class HocvientruyentranhSpider(scrapy.Spider):
    name = 'hocvientruyentranh'
    allowed_domains = ['hocvientruyentranh.com']
    start_urls = []

    def __init__(self, url, output_directory, chapter, **kwargs):
        super().__init__(**kwargs)

        self.start_urls.append(url)
        self.output_directory = output_directory
        self.chapter = chapter.lower()

    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        chapter_urls = response.css("div.table-scroll > table > tbody > tr > td > a::attr(href)")[::-1].extract()
        chapter_titles = response.css("div.table-scroll > table > tbody > tr > td > a::attr(title)")[::-1].extract()

        if self.chapter:
            if "-" in self.chapter:
                chapters = self.chapter.split("-")
                chapter_begin, chapter_end = self.get_chapter_index(chapters[0], chapters[1], chapter_titles)
                chapter_urls = chapter_urls[chapter_begin:] if chapter_end == -1 else chapter_urls[
                                                                                      chapter_begin:chapter_end]
            else:
                chapter_index = self.get_chapter_index(self.chapter, self.chapter, chapter_titles)
                chapter_urls = [chapter_urls[chapter_index[0]]]

        print("{0} chapter(s) was founded!".format(len(chapter_urls)))

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        for chapter_url in chapter_urls:
            yield scrapy.Request(url=chapter_url, callback=self.parse_details)

    def parse_details(self, response):
        file_name = response.css("title::text").extract_first()
        file_name = re.sub(">|<|:|\"|/|\|||\?|\*", "", file_name).replace("Học Viện Truyện Tranh", "").strip() + ".pdf"

        html_string = response.css("div.manga-container").extract_first()
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
