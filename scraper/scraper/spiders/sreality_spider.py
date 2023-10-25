from typing import Any, Iterable, Optional
import scrapy
from scrapy.http import Response
from scrapy.http import Request
from scraper.items import RealityItem


class SrealitySpider(scrapy.Spider):
    name = "sreality_spider"

    def __init__(self, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name, **kwargs)

    def start_requests(self) -> Iterable[Request]:
        yield scrapy.Request(
            "https://www.sreality.cz/hledani/prodej/byty", meta={"playwright": True}
        )

    def parse(self, response):
        next_page = response.xpath(
            "//a[contains(@class, 'paging-next')][1]/@href"
        ).get()

        # Sometime playwright returns loading screen instead of the content list.
        # Naive solution just gives playwright and scrapy sync another chance
        if next_page is None:
            self.logger.info("Next page button not found! Retrying...")
            yield response.follow(
                response.url,
                callback=self.parse,
                meta={"playwright": True},
                dont_filter=True,
            )
        else:
            for offer_element in response.xpath(
                "//*[@class='dir-property-list']/div[@class='property ng-scope']"
            ):
                yield RealityItem(
                    title=offer_element.xpath(".//h2/a/span/text()").get()
                    + " "
                    + offer_element.xpath(
                        ".//span[@class='locality ng-binding']/text()"
                    ).get(),
                    image_url=offer_element.xpath(".//preact//a[2]/img/@src").get(),
                )
            yield response.follow(
                next_page, callback=self.parse, meta={"playwright": True}
            )
