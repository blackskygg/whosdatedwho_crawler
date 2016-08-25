# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EventItem(scrapy.Item):
    name1 = scrapy.Field(serializer=unicode)
    name2 = scrapy.Field(serializer=unicode)
    height1 = scrapy.Field(serializer=int)
    height2 = scrapy.Field(serializer=int)
    gender1 = scrapy.Field(serializer=unicode)
    gender2 = scrapy.Field(serializer=unicode)
    age1 = scrapy.Field(serializer=int)
    age2 = scrapy.Field(serializer=int)
    zodiac1 = scrapy.Field(serializer=unicode)
    zodiac2 = scrapy.Field(serializer=unicode)
    occupation1 = scrapy.Field(serializer=unicode)
    occupation2 = scrapy.Field(serializer=unicode)
    haircolor1 = scrapy.Field(serializer=unicode)
    haircolor2 = scrapy.Field(serializer=unicode)
    eyecolor1 = scrapy.Field(serializer=unicode)
    eyecolor2 = scrapy.Field(serializer=unicode)
    nationality1 = scrapy.Field(serializer=unicode)
    nationality2 = scrapy.Field(serializer=unicode)
    event = scrapy.Field(serializer=unicode)
    duration = scrapy.Field(serializer=int)
    score = scrapy.Field(serializer=int)
    date = scrapy.Field(serializer=unicode)
