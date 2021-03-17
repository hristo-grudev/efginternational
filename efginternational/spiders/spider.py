import scrapy

from scrapy.loader import ItemLoader

from ..items import EfginternationalItem
from itemloaders.processors import TakeFirst

base = "https://www.efginternational.com/Media/fullArea/0.html?ajax=true&currentPage={}"

class EfginternationalSpider(scrapy.Spider):
	name = 'efginternational'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//ul[@class="media-list"]/li')
		for post in post_links:
			url = post.xpath('.//a[h3]/@href').get()
			date = post.xpath('.//time/text()').get()
			if url:
				yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		last_page = response.xpath('//div[@class="pagination"]/ul/li[position()=last()]/a/@href').get().split('=')[1]
		if self.page < int(last_page):
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "text-left", " " ))]//p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=EfginternationalItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
