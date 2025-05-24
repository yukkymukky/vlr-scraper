import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import os
import json                                   
from datetime import datetime, timedelta      
from dateutil import parser as dateparser 
from collections import defaultdict    
from urllib.parse import urljoin

tzinfos = {
    # North America
    'EST': -5 * 3600,
    'EDT': -4 * 3600,
    'CST': -6 * 3600,
    'CDT': -5 * 3600,
    'MST': -7 * 3600,
    'MDT': -6 * 3600,
    'PST': -8 * 3600,
    'PDT': -7 * 3600,
    'AKST': -9 * 3600,
    'AKDT': -8 * 3600,
    'HST': -10 * 3600,

    # Atlantic
    'AST': -4 * 3600,
    'ADT': -3 * 3600,
    'NST': -3.5 * 3600,  # Newfoundland Standard Time
    'NDT': -2.5 * 3600,

    # South America
    'BRT': -3 * 3600,    # Brazil
    'ART': -3 * 3600,    # Argentina
    'CLT': -4 * 3600,    # Chile
    'CLST': -3 * 3600,

    # Europe
    'GMT': 0,
    'BST': 1 * 3600,     # British Summer Time
    'CET': 1 * 3600,
    'CEST': 2 * 3600,
    'EET': 2 * 3600,
    'EEST': 3 * 3600,

    # Africa
    'WAT': 1 * 3600,
    'CAT': 2 * 3600,
    'EAT': 3 * 3600,

    # Asia
    'IST': 5.5 * 3600,   # India
    'PKT': 5 * 3600,     # Pakistan
    'ICT': 7 * 3600,     # Indochina
    'CST-CHINA': 8 * 3600,  # China Standard Time (not US CST!)
    'JST': 9 * 3600,     # Japan
    'KST': 9 * 3600,     # Korea

    # Australia
    'AEST': 10 * 3600,
    'AEDT': 11 * 3600,
    'ACST': 9.5 * 3600,
    'ACDT': 10.5 * 3600,
    'AWST': 8 * 3600,

    # UTC offsets (as fallback)
    '-12': -12 * 3600,
    '-11': -11 * 3600,
    '-10': -10 * 3600,
    '-09': -9 * 3600,
    '-08': -8 * 3600,
    '-07': -7 * 3600,
    '-06': -6 * 3600,
    '-05': -5 * 3600,
    '-04': -4 * 3600,
    '-03': -3 * 3600,
    '-02': -2 * 3600,
    '-01': -1 * 3600,
    '+00': 0,
    '+01': 1 * 3600,
    '+02': 2 * 3600,
    '+03': 3 * 3600,
    '+04': 4 * 3600,
    '+05': 5 * 3600,
    '+06': 6 * 3600,
    '+07': 7 * 3600,
    '+08': 8 * 3600,
    '+09': 9 * 3600,
    '+10': 10 * 3600,
    '+11': 11 * 3600,
    '+12': 12 * 3600,
}


class AllVlrSpider(scrapy.Spider):
    name = "vlr"
    allowed_domains = ["vlr.gg"]
    base_url = "https://vlr.gg"

    def __init__(self, username=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [f"https://vlr.gg/user/{username}"]
        self.username = username

        # de‑dupe helpers
        self.processed_urls = set()
        self.processed_replies = set()
        self.counted_post_ids = set()

        # year / streak helpers                        
        self.this_year = '2025'
        self.year_posts = 0
        self.year_upvotes = 0
        self.year_downvotes = 0
        self.day_posts_this_year = set()
        self.month_counts = defaultdict(int)
        self.interacted_posts = []      
        self.reply_counter = defaultdict(int)

        self.user_item = {
            "upvotes": 0,
            "downvotes": 0,
            "upvote_count": 0,
            "downvote_count": 0,
            "dead_count": 0,
            "biggest_upvote": -1,
            "biggest_upvote_url": "",
            "biggest_downvote": 0,
            "biggest_downvote_url": "",
            "biggest_upvote_quote": "",
            "biggest_downvote_quote": "",
            "reply_user": {},
            "flag_url": "",
            "flair_url": "",
            "total_comment_length": 0,
            "interaction_count": 0,
        }

    def parse(self, response):
        page_links = response.css("a.btn.mod-page::attr(href)").getall()
        last_page_number = int(page_links[-1].split("=")[-1]) if page_links else 1
        for page_number in range(1, last_page_number + 1):
            url = f"/user/{self.username}/?page={page_number}"
            yield response.follow(url, self.parse_user_page)

    def parse_user_page(self, response):
        post_cards = response.css("div.wf-card.ge-text-light")
        for card in post_cards:
            link = card.css("a::attr(href)").get()
            posted_text_raw = card.css("div::text").getall()
            posted_text = next(
                (t.strip() for t in posted_text_raw if t.strip().startswith("posted")),
                None,
            )
            if posted_text and any(
                old in posted_text
                for old in [
                    "6 months",
                    "7 months",
                    "8 months",
                    "9 months",
                    "10 months",
                    "11 months",
                    "year",
                ]
            ):
                continue
            if link:
                yield response.follow(link, self.parse_discussion)

    def parse_discussion(self, response):
        original_up, original_down = self.user_is_poster(response)
        if original_up != -1:          # user is thread starter
            op_date_title = (response.xpath(
                '//div[@class="post-footer"]//span[contains(@class,"js-date-toggle")]/@title'
            ).get() or
            response.xpath(
                '//div[@class="post-footer"]//span[contains(@class,"js-date-toggle")]/text()'
            ).get())

            if op_date_title and str(self.this_year) in op_date_title:
                op_date = dateparser.parse(op_date_title.strip(), tzinfos=tzinfos).date()

                op_post_url = response.xpath(
                    '(//div[contains(@class,"post-footer")]/div[contains(@class,"noselect")]'
                    '/a[contains(@class,"post-action link")]/@href)[1]'
                ).get()

                if op_post_url:
                    op_post_url = response.urljoin(op_post_url).split('#')[0].rstrip('/')

                    if op_post_url not in self.counted_post_ids:
                        op_quote = self.get_full_quote(
                            response.xpath('//a[@id="1"]/following-sibling::div[contains(@class,"post-header")]')
                        )
                        # add it to processed sets so the loop later will skip it
                        self.processed_urls.add(op_post_url)
                        self._count_year_post(op_date, original_up, original_down,
                                              op_post_url, op_quote, original=True)

        user_posts = response.css(
            f'a.post-header-author[href*="/user/{self.username}"]'
        )
        post_url_xpath = (
            "./ancestor::div[contains(@class,'wf-card post')]/div[contains(@class,'post-footer')]"
            "/div[contains(@class,'noselect')]/a[contains(@class,'post-action link')]/@href"
        )

        for post_author in user_posts:
            post_url = self.get_full_url(post_author, post_url_xpath, response).split('#')[0].rstrip('/')
            if post_url in self.processed_urls:
                continue
            if not self.user_item.get("flag_code") and not self.user_item.get("flair_url"):
              post_card = post_author.xpath("./ancestor::div[contains(@class,'wf-card post')]")

              flag_class = post_card.xpath('.//i[contains(@class,"post-header-flag")]/@class').get()
              flair_url = post_card.xpath('.//img[contains(@class,"post-header-flair")]/@src').get()

              if flair_url and flair_url.startswith("//"):
                  flair_url = "https:" + flair_url

              flag_code = None
              if flag_class and "mod-" in flag_class:
                  parts = flag_class.split("mod-")
                  if len(parts) > 1:
                      flag_code = parts[1].strip()

              self.user_item["flag_code"] = flag_code
              self.user_item["flair_url"] = flair_url
            self.processed_urls.add(post_url)

            date_title = post_author.xpath(
                './ancestor::div[contains(@class,"wf-card post")]'
                '//span[contains(@class,"js-date-toggle")]/@title'
            ).get()
            if not date_title or str(self.this_year) not in date_title:
                continue
            post_date = dateparser.parse(date_title.strip(), tzinfos=tzinfos).date()

            upvotes, downvotes = self._extract_votes(post_author)

            # year metrics
            if post_url not in self.counted_post_ids:
                full_quote = self.get_full_quote(post_author)
                self.user_item["total_comment_length"] += len(full_quote)
                self._count_year_post(post_date, upvotes, downvotes, post_url, full_quote)

            # all‑time vote totals & biggest ±votes
            self._maybe_set_biggest(post_author, upvotes, downvotes, post_url)

            # fan / reply counts
            self._update_reply_counts(post_author)

        # follow “continue thread” links
        for link in response.css('a:contains("continue thread")::attr(href)').getall():
            yield response.follow(link, self.parse_discussion)

    def _extract_votes(self, post_author):
        up = int(
            post_author.xpath(
                './following-sibling::div[contains(@class,"post-frag-container")]/'
                'div[contains(@class,"positive")]/text()'
            ).get()
            or 0
        )
        down = int(
            post_author.xpath(
                './following-sibling::div[contains(@class,"post-frag-container")]/'
                'div[contains(@class,"negative")]/text()'
            ).get()
            or 0
        )
        return up, down

    def _count_year_post(self, post_date, up, down, unique_id, quote="", original=False):
        # if not original:
        self.year_posts += 1  
        self.year_upvotes += up
        self.year_downvotes += down
        if up == 0 and down == 0:
          self.user_item["dead_count"] += 1
        self.day_posts_this_year.add(post_date)
        self.month_counts[post_date.month] += 1
        interaction = abs(up) + abs(down)
        self.interacted_posts.append(
            {
                "url": unique_id,
                "upvotes": up,
                "downvotes": down,
                "interaction": interaction,
                "comment": quote
            }
        )
        self.counted_post_ids.add(unique_id)

    def _update_totals(self, up, down):
        self.user_item["upvotes"] += up
        self.user_item["downvotes"] += down
        if up > 0 and down == 0:
            self.user_item["upvote_count"] += 1
        elif down < 0 and up == 0:
            self.user_item["downvote_count"] += 1
        elif up == 0 and down == 0:
            self.user_item["dead_count"] += 1

    def _maybe_set_biggest(self, post_author, up, down, url):
        full_quote = self.get_full_quote(post_author)
        if up > self.user_item["biggest_upvote"]:
            self.user_item["biggest_upvote"] = up
            self.user_item["biggest_upvote_url"] = url
            self.user_item["biggest_upvote_quote"] = full_quote
        if down < self.user_item["biggest_downvote"]:
            self.user_item["biggest_downvote"] = down
            self.user_item["biggest_downvote_url"] = url
            self.user_item["biggest_downvote_quote"] = full_quote

    def _update_reply_counts(self, post_author):
        reply_usernames = post_author.xpath(
            "./ancestor::div[contains(@class,'threading')]/div[contains(@class,'threading')]/"
            "descendant::a[contains(@class,'post-header-author')]/text()"
        ).getall()
        reply_ids = post_author.xpath(
            "./ancestor::div[contains(@class,'threading')]/div[contains(@class,'threading')]/"
            "descendant::div[contains(@class,'report-form')]/@data-post-id"
        ).getall()
        for name, pid in zip(reply_usernames, reply_ids):
            name = name.strip()
            if name and name != self.username and pid not in self.processed_replies:
                self.reply_counter[name] += 1
                self.processed_replies.add(pid)

    def get_full_quote(self, post_author):
        post_body = post_author.xpath(
            "./ancestor::div[contains(@class,'wf-card post')]/div[contains(@class,'post-body')]"
        )
        return " ".join(post_body.xpath(".//text()").getall()).strip()

    def get_full_url(self, post_author, post_url_xpath, response):
        return response.urljoin(post_author.xpath(post_url_xpath).get())

    def user_is_poster(self, response):
        author = response.xpath(
            '//a[@id="1"]/following::div[contains(@class,"post-header")]//a[contains(@class,"post-header-author")]/text()'
        ).get()
        if not author or author.strip() != self.username:
            return -1, -1          

        frag_txt = response.xpath("//div[@id='thread-frag-count']/text()").get()

        if frag_txt is None:        
            return -1, -1          
         
        count = int(frag_txt.strip() or 0)
        return (count, 0) if count > 0 else (0, count) if count < 0 else (0, 0)

    def closed(self, reason):
        longest = 0
        if self.day_posts_this_year:
            sorted_days = sorted(self.day_posts_this_year)
            streak = cur = 1
            for prev, nxt in zip(sorted_days, sorted_days[1:]):
                if (nxt - prev).days == 1:
                    cur += 1
                    streak = max(streak, cur)
                else:
                    cur = 1
            longest = streak

        most_active_month = (
            max(self.month_counts, key=self.month_counts.get) if self.month_counts else None
        )

        top_posts = sorted(
            self.interacted_posts, key=lambda d: d["interaction"], reverse=True
        )[:5]

        top_fans = sorted(self.reply_counter.items(), key=lambda kv: kv[1], reverse=True)[:10]

        with open('team_logos.json', 'r') as f:
          team_logos = json.load(f)

        light_url = self.user_item.get("flair_url")
        dark_url = None
        for entry in team_logos:
            team_name, urls = next(iter(entry.items()))
            if urls.get("light_mode_url") == light_url:
                dark_url = urls.get("dark_mode_url")
                break

        wrapped = {
            "username": self.username,
            "year": self.this_year,
            "total_posts_this_year": self.year_posts,
            "upvotes_this_year": self.year_upvotes,
            "downvotes_this_year": self.year_downvotes,
            "net_votes_this_year": self.year_upvotes + self.year_downvotes,
            "dead_posts_this_year": self.user_item.get("dead_count"),
            "most_active_month": most_active_month,  # 1‑Jan … 12‑Dec
            "longest_post_streak_days": longest,
            "top_5_posts_by_interaction": top_posts,
            "top_5_biggest_fans": [{"user": u, "replies": n} for u, n in top_fans],
            "flag_code": self.user_item.get("flag_code"),
            "flair_url": dark_url or light_url,
            "average_comment_length": self.user_item.get("total_comment_length") / self.year_posts if self.year_posts else 0,
        }

        os.makedirs("wrapped-data", exist_ok=True)
        with open(f"wrapped-data/{self.username}_wrapped.json", "w", encoding="utf-8") as fp:
            json.dump(wrapped, fp, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(AllVlrSpider)
    process.start()