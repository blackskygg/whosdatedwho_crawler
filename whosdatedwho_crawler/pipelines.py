# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import cymysql
from items import EventItem

class SQLPipeline(object):
    #once reach this value, a commit will be performed
    max_record = 10

    def __init__(self, *args, **kwargs):
        super(SQLPipeline, self).__init__(*args, **kwargs)

    def open_spider(self, spider):
        self.conn = cymysql.connect(host='localhost', user='sky',
                                    passwd='password', db='learnsql',
                                    charset='utf8')
        self.cur = self.conn.cursor()
        self.nrecords = 0;

    def check_if_submit(self):
        self.nrecords += 1
        if(self.nrecords > self.max_record):
            self.conn.commit()
            self.nrecords = 0

    def process_item(self, item, *args, **kwargs):
        field_list = []
        value_list = []

        for key in item:
            field_list.append(key)
            value = item.fields[key]["serializer"](item[key])
            if isinstance(value, unicode):
                value_list.append(cymysql.escape_string(value))
            elif isinstance(value, int):
                value_list.append(str(value))

        self.cur.execute("insert into whosdatedwho(%s) values(%s)"%
                         (",".join(field_list),
                          ",".join(value_list)))
        
        self.check_if_submit()
        return item


    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
