import scrapy
import re
from urllib.parse import urlencode
from spider_steam.items import SpiderSteamItem

class SteamspiderSpider(scrapy.Spider):
    name = 'SteamSpider'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['http://store.steampowered.com/']

    def start_requests(self):
        queries = ['гонки','стратегия','симулятор'] 
        for query in queries:
            for i in range(1,3):
                url = 'https://store.steampowered.com/search/?' + urlencode({'term': query,'page' : i})
                yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        games = response.xpath('//div[@id="search_results"]//a[contains(@href,"app")]')
        for game in games:
            game_ref = game.attrib['href']
            platforms = list(map(lambda x: x.attrib['class'].replace('platform_img ',''),
                            response.xpath(f'//a[@href="{game_ref}"]//span[contains(@class,"platform_img")]')))
            price = response.xpath(f'//a[@href="{game_ref}"]//div[@class="col search_price discounted responsive_secondrow"]/text()').extract()
            if(len(price) == 0):
                price = response.xpath(f'//a[@href="{game_ref}"]//div[@class="col search_price  responsive_secondrow"]/text()').extract()
            if('Free' not in price):
                price = price[-1].replace(' ','')
            price = price.replace('\r','').replace('\n','')
            yield scrapy.Request(url=game_ref, callback=self.parse_game_page,cb_kwargs = {'platforms':platforms,'price':price})

    def parse_game_page(self, response,platforms,price):
        item = SpiderSteamItem()
        item['name'] = response.xpath('//div[@id="appHubAppName"]/text()').extract()[0]
        item['price'] = price
        number_of_reviews = response.xpath('//meta[@itemprop="reviewCount"]')
        if len(number_of_reviews) == 0 :
            item['number_of_reviews'] = 0
        else:
            item['number_of_reviews'] = number_of_reviews[0].attrib['content']
        rating = response.xpath('//meta[@itemprop="ratingValue"]')
        if len(rating) == 0:
            item['rating'] = 'No rating'
        else:
            item['rating'] = rating[0].attrib['content']
        item['release_date'] = response.xpath('//div[@class="release_date"]//div[@class="date"]/text()').extract()[0]
        item['developer'] = response.xpath('//div[@class="dev_row"]//div[@class="summary column"]/a/text()').extract()[0]
        tags = response.xpath('//div[@class="glance_tags popular_tags"]//a/text()').extract()
        category = response.xpath('//div[@class="blockbg"]//a//text()').extract()
        tags = list(map(lambda s:s.replace('\t','').replace('\n','').replace('\r',''),tags))
        item['category'] = '/'.join(category).strip()
        item['tags'] = ','.join(tags).strip()
        item['platforms'] = platforms
        yield item
