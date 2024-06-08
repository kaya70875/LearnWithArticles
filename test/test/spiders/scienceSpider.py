import scrapy
from scrapy.crawler import CrawlerProcess
from config import config

import datetime

class CrawlScienceNews(scrapy.Spider):
    name = 'crawlscienceNews'
    allowed_domains = ['sciencenews.org']
    start_urls = ['https://www.sciencenews.org/all-stories/']
    page = 0

    custom_settings= {
            'FEEDS' : {'data/science/scienceNews.json' : {'format' : 'json',
                                                  'overwrite' : True}}
        }

    def parse(self, response):
        self.page +=1
        if self.page > config.SCIENCENEWS_PAGE:
            self.crawler.engine.close_spider(self, 'Reached max. page count!')
        links = response.css('h3.post-item-river__title___vyz1w a::attr(href)').getall()
        
        for link in links:
            next_url = response.urljoin(link)
            yield scrapy.Request(next_url, callback=self.parse_article)

        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self , response):
        body = response.css('div.rich-text.rich-text--with-sidebar.single__rich-text___RmCDp p::text').getall()
        for text in body:
            yield{
                'text' : text
            }

class CrawlLiveScience(scrapy.Spider):
    name = 'crawlliveScience'
    date = datetime.datetime.now()
    start_urls = [f'https://www.livescience.com/archive/{date.year}/{date.month:02d}']
    page = 0
    custom_settings = {
        'FEEDS': {
            'data/science/liveScience.json': {
                'format': 'json',
                'overwrite': True,
            }
        }
    }

    def parse(self, response):
        self.page += 1
        if self.page > config.LIVESC_PAGE:
            self.crawler.engine.close_spider(self, 'Reached max. page count!')

        links = response.css('li.day-article a::attr(href)').getall()

        for link in links:
            next_url = response.urljoin(link)
            yield scrapy.Request(next_url, callback=self.parse_article)

        if self.page < config.LIVESC_PAGE:
            self.date = self.date.replace(day=1) - datetime.timedelta(days=1)
            next_page_url = f'https://www.livescience.com/archive/{self.date.year}/{self.date.month:02d}'
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        body = response.css('div.text-copy.bodyCopy.auto p::text').getall()
        for text in body:
            yield {
                'text': text
            }


process = CrawlerProcess()

process.crawl(CrawlScienceNews)
process.crawl(CrawlLiveScience)
