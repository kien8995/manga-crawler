import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from MangaCrawler.spiders.hocvientruyentranh import HocvientruyentranhSpider
from MangaCrawler.spiders.hentailx import HentailxSpider


class Crawler:

    def __init__(self):
        self.settings_file_path = 'MangaCrawler.settings'  # The path seen from root, ie. from main.py
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', self.settings_file_path)
        self.process = CrawlerProcess(get_project_settings())

    def start(self, url, output_directory, chapter):
        crawler = None

        if "hocvientruyentranh.com" in url:
            crawler = HocvientruyentranhSpider
        else:
            crawler = HentailxSpider

        self.process.crawl(crawler, url=url, output_directory=output_directory, chapter=chapter)
        self.process.start()  # the script will block here until all crawling jobs are finished
