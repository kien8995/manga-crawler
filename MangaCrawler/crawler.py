import os
import sys
from urllib.parse import urlparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from MangaCrawler.spiders.hocvientruyentranh import HocvientruyentranhSpider
from MangaCrawler.spiders.mangak import MangakSpider
from MangaCrawler.spiders.hentailx import HentailxSpider


class Crawler:

    def __init__(self):
        self.settings_file_path = 'MangaCrawler.settings'  # The path seen from root, ie. from main.py
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', self.settings_file_path)
        self.process = CrawlerProcess(get_project_settings())

    def start(self, url, output_directory, chapter, image):
        crawler = None

        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        if "hocvientruyentranh.com" in domain:
            crawler = HocvientruyentranhSpider
        elif "mangak.info" in domain:
            crawler = MangakSpider
        elif "hentailx.com" in domain:
            crawler = HentailxSpider
        else:
            print('This domain do not support!')
            sys.exit()

        self.process.crawl(crawler, url=url, output_directory=output_directory, chapter=chapter, image=image)
        self.process.start()  # the script will block here until all crawling jobs are finished
