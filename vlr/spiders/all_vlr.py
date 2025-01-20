import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
import datetime


class AllVlrSpider(scrapy.Spider):
    name = "vlr"
    allowed_domains = ["vlr.gg"]
    base_url = "https://www.vlr.gg"
    start_urls = ["https://www.vlr.gg/threads"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "FEEDS": {
            f"vlr_threads_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv": {
                "format": "csv",
                "encoding": "utf-8",
            }
        },
    }

    def parse(self, response):
        # Get the number of pages to scrape
        max_pages = response.css("div.action-container-pages a.btn.mod-page::text").getall()
        max_pages = int(max_pages[-1]) if max_pages else 1

        # Iterate over each page
        for page in range(1, max_pages + 1):
            yield scrapy.Request(
                url=f"{self.base_url}/threads/?page={page}",
                callback=self.parse_threads,
            )

    def parse_threads(self, response):
        # Extract thread links, skipping pinned threads
        thread_links = response.css(".thread-item-header-title::attr(href)").getall()[5:]
        for link in thread_links:
            full_url = urljoin(self.base_url, link)
            yield scrapy.Request(url=full_url, callback=self.parse_thread)

    def parse_thread(self, response):
        usernames = response.css(".post-header-author::text").getall()
        frag_counts = response.xpath("//div[contains(@class,'post-frag-count')]/text()").getall()
        comments = [" ".join(comment.xpath(".//text()").getall()).replace("\n", "").strip() for comment in response.css(".post-body")]
        frag_counts = [frag_count.strip() for frag_count in frag_counts if frag_count.strip()]

        # Handle first post's special frag count
        first_post_frag_count = response.css("#thread-frag-count::text").get()
        first_post_frag_count = first_post_frag_count.strip() if first_post_frag_count else None

        for index, username in enumerate(usernames):
            yield {
                "username": username.strip(),
                "frag_count": first_post_frag_count if index == 0 else (frag_counts[index - 1].strip() if index - 1 < len(frag_counts) else None),
                "comment": comments[index] if index < len(comments) else None,
                "thread_url": response.url,
            }

        # Follow "continue thread" links, ensuring no external links
        continue_thread_link = response.css("a.wf-card[href*='/threads']::attr(href)").get()
        if continue_thread_link:
            self.logger.info(f"Following continue thread link: {continue_thread_link}")
            yield scrapy.Request(
                url=urljoin(self.base_url, continue_thread_link),
                callback=self.parse_thread,
            )

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(AllVlrSpider)
    process.start()