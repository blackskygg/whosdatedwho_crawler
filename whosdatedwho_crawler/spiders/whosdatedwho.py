# -*- coding: utf-8 -*-
import scrapy
import redis
import dateutil.parser

from whosdatedwho_crawler.items import EventItem

class EventSpider(scrapy.Spider):
    name = "whosdatedwho"
    allowed_domains = ["www.whosdatedwho.com"]
    index = 1
    max_retry = 5

    event_xpath = '//div[@class="ff-latest-list"]/div[@class="left ff-panel"]/a'
    comparison_xpath = '//*[@id="ff-couple-comparison"]/div/div'
    fact_xpath = '//div[@class="ff-fact-box small"]'
    page_url = "http://www.whosdatedwho.com/timeline?page=%d&_block=page.latestEvents"
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                 "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                 "Sep": 9, "Oct": 10, "Dec": 11, "Nov": 12}
             


    def __init__(self, *args, **kwargs):
    	super(scrapy.Spider, self).__init__(*args, **kwargs)
        self.comparison_map = {"Age": {'name': "age"},
                               "Name": {'name': "name"},
                               "Height": {'name': "height",
                                          'preprocess': self.parse_height},
                               "Zodiac": {'name': "zodiac"},
                               "Occupation": {'name': "occupation"},
                               "Hair Color": {'name': "haircolor"},
                               "Eye Color": {'name': "eyecolor"},
                               "Nationality": {'name': "nationality"}}
        self.err_count = {}
        
    def parse_event(self, string):
        wl = string.split(" ")
        datestr = string[string.find("-") + 1:]
        date = dateutil.parser.parse(datestr)
        return (wl[0].strip(), "%s-%s-%s"%(date.year, date.month, date.day))

    def parse_height(self, string):
        lb = string.find("(")
        rb = string.find("cm")

        return string[lb+1:rb-1]

    def start_requests(self):
        return [scrapy.Request(self.page_url % 1,
                               callback=self.parse_list,
                               errback = self.errback)]

    def parse_list(self, response):
        #parse the "timeline" lists
        data = {}
        for sel in response.xpath(self.event_xpath):
            event, date = self.parse_event(sel.xpath(".//span[2]/text()").extract()[0])
            url = sel.xpath("@href").extract()[0]
            print url
            yield scrapy.Request(url, callback=self.parse_page,
                                 meta = {"date": date, "event": event})

        self.index = self.index + 1
        yield scrapy.Request(self.page_url % self.index,
                             callback=self.parse_list,
                             errback = self.errback)

    def errback(self, failure):
        request = failure.value.request

        if request.url in self.err_count:
            self.err_count[request.url] = self.err_count[request.url] + 1
        else:
            self.err_count[request.url] = 1

        if err_count[request.url] > self.max_retry:
            self.index = self.index + 1
            
        yield scrapy.Request(self.page_url % self.index,
                             callback=self.parse_list,
                             errback = self.errback)
        
    def parse_page(self, response):
        item = EventItem()
        item['date'] = response.meta['date']
        item['event'] = response.meta['event']

        #parse the "fact" column
        for sel in response.xpath(self.fact_xpath):
            s = sel.xpath(".//div[@class='header']/text()").extract()[0]
            if -1 != s.find("Relationship"):
                item['duration'] = sel.xpath(".//div[@class='fact ']/text()").extract()[0].strip()
            elif -1 != s.find("Fact Check"):
                #if it's not true, ignore it
                status = sel.xpath(".//div[@class='footer']/text()").extract()[0].strip()
                if -1 == status.find("True"):
                    return
            elif -1 != s.find("Compatibility"):
                item['score'] = sel.xpath(".//div[@class='footer']/text()").extract()[0].strip()
                item['score'] = item['score'][0:-1]

        #parse the "comparison" column
        com_iter = response.xpath(self.comparison_xpath).__iter__()
        try:
            while True:
                self.parse_comparison(com_iter, item)
        except StopIteration:
            pass
        
        yield item

    def detect_gender_order(self, sel, item):
        #whosdatedwho sometimes will change the order of F and M :(
        try:
            gl = sel.xpath(".//img/@alt").extract()
            item["gender1"] = gl[0].strip()
            item["gender2"] = gl[1].strip()
        except IndexError:
            pass
        
    def parse_comparison(self, iterator, item):
        sel = iterator.next()

        try:
            s = sel.xpath("div/text()").extract()[0]
        except IndexError:
            return

        for tag, attr in self.comparison_map.items():
            if -1 != s.find(tag):
                sel = iterator.next()
                vl = sel.xpath("div/h5//text()").extract()

                if attr.get("preprocess", None):
                    vl[0] = attr["preprocess"](vl[0])
                    vl[1] = attr["preprocess"](vl[1])
                
                item[attr["name"]+'1'] = vl[0].strip()
                item[attr["name"]+'2'] = vl[1].strip()

            if -1 != s.find("Height"):
                self.detect_gender_order(sel, item)
