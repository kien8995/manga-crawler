# -*- coding: utf-8 -*-
import os
import scrapy
from weasyprint import HTML
import re
import requests


class HocvientruyentranhSpider(scrapy.Spider):
    name = 'hocvientruyentranh'
    allowed_domains = ['hocvientruyentranh.com']
    start_urls = []

    def __init__(self, url, output_directory, chapter, image, **kwargs):
        super().__init__(**kwargs)

        self.start_urls.append(url)
        self.output_directory = output_directory
        self.chapter = chapter.lower()
        self.image = image

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
        if self.image:
            folder_name = response.css("title::text").extract_first()
            folder_name = re.sub(">|<|:|\"|/|\|||\?|\*", "", folder_name).replace("Học Viện Truyện Tranh","").strip()

            image_urls = response.css("div.manga-container > img::attr(src)").extract()

            if not os.path.exists(self.output_directory + "/" + folder_name):
                os.makedirs(self.output_directory + "/" + folder_name)

            for index, url in enumerate(image_urls):
                self.download_image(url, self.output_directory + "/" + folder_name + "/" + str(index) + ".jpg")

            print("{0} .Done.".format(folder_name))
        else:
            file_name = response.css("title::text").extract_first()
            file_name = re.sub(">|<|:|\"|/|\|||\?|\*", "", file_name).replace("Học Viện Truyện Tranh", "").strip() + ".pdf"

            html_string = response.css("div.manga-container").extract_first()

            html = HTML(string=html_string)
            html.write_pdf(os.path.join(self.output_directory, file_name),
                           stylesheets=["MangaCrawler/assets/styles/page.css"])
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

    def download_image(self, url, filename=None):
        if filename is None:
            local_filename = url.split('/')[-1].split("?")[0]
        else:
            local_filename = filename

        r = requests.get(url, allow_redirects=True)
        open(local_filename, 'wb').write(r.content)
