import scrapy


class ResultScraper(scrapy.Spider):
    name = "results"

    start_urls = [
        "https://www.hltv.org/results"
    ]

    def parse(self, response):
        matches = response.css('.a-reset').xpath('@href').getall()
        for match in matches:
            match = response.urljoin(match)
            yield scrapy.Request(url=match, callback=self.parse_match)

        # next_page = response.css('.pagination-next').xpath('@href').get()
        # if next_page:
        #     yield scrapy.Request(next_page, callback=self.parse)

    def parse_match(self, response):
        maps = response.css('.results-stats').xpath('@href').getall()
        for m in maps:
            m = response.urljoin(m)
            yield scrapy.Request(url=m, callback=self.parse_map)

    def parse_map(self, response):
        map_name = response.css('.small-text').xpath('following-sibling::text()[1]').get()
        map_name = map_name.replace("\n", "").replace(" ", "")

        left_team = response.css('.team-left')
        left_name = left_team.css('a::text').get()
        left_score = left_team.css('.bold::text').get()

        right_team = response.css('.team-right')
        right_name = right_team.css('a::text').get()
        right_score = right_team.css('.bold::text').get()

        # Check who is winner
        if int(left_score) > int(right_score):
            winner = left_name
            winner_score = left_score
            loser = right_name
            loser_score = right_score
        else:
            winner = right_name
            winner_score = right_score
            loser = left_name
            loser_score = left_score

        yield {
            "map_name": map_name,
            "winner": winner,
            "loser": loser,
            "winner_score": winner_score,
            "loser_score": loser_score,
        }