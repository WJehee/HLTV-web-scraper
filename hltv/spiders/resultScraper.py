import scrapy


class ResultScraper(scrapy.spider):
    name = "results"

    start_urls = [
        "https://www.hltv.org/results"
    ]

    def parse(self, response):
        page = response