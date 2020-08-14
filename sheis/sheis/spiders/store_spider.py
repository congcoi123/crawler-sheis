# -*- coding: utf-8 -*-
import time
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from sheis.items import SheisItem

index = 0

class StoreSpider(CrawlSpider):
    
    name = "store"
    allowed_domains = ["sheis.vn"]
    start_urls = ["https://www.sheis.vn/tim-kiem/dia-diem?q=&sort=0&ca=42,22,29,17,19,14,18&l=27"]

    def start_requests(self):

        #scroll to load
        # script = """
        # function main(splash)
        #     local url = splash.args.url
        #     local num_scrolls = 500
        #     local scroll_delay = 1

        #     local scroll_to = splash:jsfunc("window.scrollTo")
        #     local get_body_height = splash:jsfunc(
        #         "function() {return document.body.scrollHeight;}"
        #     )
        #     assert(splash:go(url))
        #     assert(splash:wait(1))

        #     for _ = 1, num_scrolls do
        #         local height = get_body_height()
        #         for i = 1, 10 do
        #             scroll_to(0, height * i/10)
        #             assert(splash:wait(scroll_delay/10))
        #         end
        #     end        
        #     return splash:html()
        # end
        # """

        script = """
        function main(splash)
            local url = splash.args.url
            local num_loads = 400

            assert(splash:go(url))
            assert(splash:wait(1))

            for _ = 1, num_loads do
                local btn_load = splash:select('a[class^=btn-loadmore]')
                
                if not btn_load then
                    break
                end

                btn_load:click()
                assert(splash:wait(5))
            end

            return {
                html = splash:html()
            }
        end
        """

        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_result, meta={
                'splash': {
                    'args': {'lua_source': script, 'timeout': 1800},
                    'endpoint': 'execute',
                }
            })

    def parse_result(self, response):
        stores = response.xpath('//div[@class="info-search-top"]')

        for store in stores:
            url = store.xpath(
                'a[@class="title-product"]/@href').extract_first()
            full_url = response.urljoin(url)
            yield scrapy.Request(full_url, callback=self.parse_store)

    def parse_store(self, response):
        stores = response.xpath('//div[@class="top-place-detail"]')

        for store in stores:

            info = store.xpath('div[@class="place-info"]/div[@class="top-place-info"]')
            imgs = store.xpath('div[@class="place-img-info"]/div[@class="place-slide-photo"]')

            item = SheisItem()

            #index
            global index
            item["index"] = index
            
            #name
            name = info.xpath('h2/text()').extract_first()
            name = name.replace("\r\n", "")
            name = name.lstrip()
            name = name.rstrip()

            item["name"] = name

            #location
            location = info.xpath('div[@class="place-info-detail"]/div[@class="content"]/p/a/@title').extract_first()
            item["location"] = location

            #open time
            open_time = info.xpath('div[@class="place-info-detail"]/div[@class="content"]/p[@class="place-time"]/span[3]/text()').extract_first()
            item["open_time"] = open_time

            #price
            price = info.xpath('div[@class="place-info-detail"]/div[@class="content"]/p[3]/text()').extract()[1]
            price = price.replace("\r\n", "")
            price = price.lstrip()
            price = price.rstrip()
            item["price"] = price

            #tel
            tel = info.xpath('div[@class="place-info-detail"]/div[@class="content"]/p[4]/text()').extract()[1]
            tel = tel.replace("\r\n", "")
            tel = tel.lstrip()
            tel = tel.rstrip()
            item["tel"] = tel

            #collections
            collections = info.xpath('p[@class="place-type"]/a/@title').extract()
            item["collections"] = {}

            count = 0
            for collection in collections:
                item["collections"][count] = collection
                count = count + 1

            #images
            images = imgs.xpath('div[@class="slide-item"]/a/img/@src').extract()
            item["images"] = {}

            count = 0
            for image in images:
                item["images"][count] = image
                count = count + 1

            #counting
            index = index + 1

            yield item