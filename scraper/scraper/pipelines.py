# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scraper.spiders.sreality_spider import SrealitySpider
from scrapy.exceptions import DropItem
import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


class RealityDBWriterPipeline:
    """
    Duplicate items are received either due to a playwright sync issue or because the web pages might be showing the same offers.
    I remove these duplicates using PostgreSQL's UNIQUE mechanism.
    """

    TABLE_NAME = "reality"

    def process_item(self, item, spider):
        # close_spider doesn't stop the crawling immediately. Thus the weird order of actions
        insert_sql = f"INSERT INTO {self.TABLE_NAME} (title, image_url) VALUES (%s, %s) ON CONFLICT DO NOTHING;"
        count_sql = f"SELECT count(*) FROM reality;"

        self.cursor.execute(count_sql)
        item_count = self.cursor.fetchall()[0][0]
        if item_count >= spider.settings.getint("ITEM_LIMIT", 10):
            spider.crawler.engine.close_spider(spider)
            raise DropItem()

        self.cursor.execute(insert_sql, (item.title, item.image_url))
        return item

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOSTNAME"],
            port="5432",
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (title TEXT, image_url TEXT, UNIQUE(title, image_url)); DELETE FROM {self.TABLE_NAME};"
        )

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
