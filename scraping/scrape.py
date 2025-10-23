from playwright.sync_api import sync_playwright
import json, re, datetime, time, random
from process import Process


class Scraper:

    def __init__(
        self,
        user,
        max_tweets=5000,
        scroll_pause_min=2,
        scroll_pause_max=5,
        request_delay_min=0.5,
        request_delay_max=2,
        max_scrolls=200,
        scroll_distance=4000,
    ):

        self.user = user
        self.MAX_TWEETS = max_tweets
        self.SCROLL_PAUSE_MIN = scroll_pause_min
        self.SCROLL_PAUSE_MAX = scroll_pause_max
        self.REQUEST_DELAY_MIN = request_delay_min
        self.REQUEST_DELAY_MAX = request_delay_max
        self.MAX_SCROLLS = max_scrolls
        self.SCROLL_DISTANCE = scroll_distance
        self.proc = Process()

    def setup_browser(self, p):

        b = p.firefox.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        ctx = b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            viewport={"width": 1920, "height": 1080},
        )

        page = ctx.new_page()
        captured = []
        unique_requests = set()

        return b, ctx, page, captured, unique_requests

    def set_settings(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

    def log_request(self, req):

        if "graphql" in req.url and (
            "UserTweets" in req.url
            or "TweetResultByRestId" in req.url
            or "UserMedia" in req.url
            or "timeline" in req.url.lower()
        ):

            req_id = f"{req.method}:{req.url}"

            if req_id not in self.unique_requests:
                self.unique_requests.add(req_id)
                self.captured.append(req)

    def browse(self, page):
        start_time = time.time()

        try:
            page.goto(f"https://x.com/{self.user}", wait_until="networkidle")
            page.wait_for_timeout(random.randint(5000, 10000))

            scroll_count = 0
            last_tweet_count = 0
            no_new_tweets_count = 0

            while (
                scroll_count < self.MAX_SCROLLS and len(self.captured) < self.MAX_TWEETS
            ):
                scroll_distance = random.randint(
                    self.SCROLL_DISTANCE // 2, self.SCROLL_DISTANCE
                )
                page.mouse.wheel(0, scroll_distance)

                wait_time = random.uniform(self.SCROLL_PAUSE_MIN, self.SCROLL_PAUSE_MAX)
                page.wait_for_timeout(int(wait_time * 1000))

                current_tweet_count = len(self.captured)

                if current_tweet_count == last_tweet_count:
                    no_new_tweets_count += 1
                    if no_new_tweets_count > 10:

                        break
                else:
                    no_new_tweets_count = 0
                    last_tweet_count = current_tweet_count

                scroll_count += 1

                if len(self.captured) >= self.MAX_TWEETS:
                    print(f"Reached tweet limit of {self.MAX_TWEETS}, stopping")
                    break

                if random.random() < 0.2:
                    page.mouse.wheel(0, -random.randint(1000, 2000))
                    page.wait_for_timeout(random.randint(500, 1500))

        except Exception as e:
            print(f"Error during browsing: {e}")

        elapsed_time = time.time() - start_time

        return self.captured, page

    def scrape(self):
        start_time = time.time()

        with sync_playwright() as p:

            b, ctx, page, captured, unique_requests = self.setup_browser(p)
            self.captured = captured
            self.unique_requests = unique_requests

            page.on("request", self.log_request)

            captured, page = self.browse(page)

            records = []
            successful_requests = 0
            failed_requests = 0

            requests_to_process = (
                captured[: self.MAX_TWEETS]
                if len(captured) > self.MAX_TWEETS
                else captured
            )

            for i, req in enumerate(requests_to_process):
                try:
                    if i > 0:
                        delay = random.uniform(
                            self.REQUEST_DELAY_MIN, self.REQUEST_DELAY_MAX
                        )
                        time.sleep(delay)

                    r = page.request.fetch(
                        req.url, method=req.method, headers=req.headers
                    )

                    if r.status == 200:
                        data = r.json()
                        records.append(data)
                        successful_requests += 1

                    else:
                        failed_requests += 1
                        if r.status == 429:
                            time.sleep(60)

                except Exception as e:
                    failed_requests += 1
                    time.sleep(random.uniform(2, 5))

            ctx.close()
            b.close()

            elapsed_time = time.time() - start_time

            self.raw_file = records
            return records

    def scrape_and_process(self, user):

        estimated_scroll_time = (
            self.MAX_SCROLLS * (self.SCROLL_PAUSE_MIN + self.SCROLL_PAUSE_MAX) / 2
        )
        estimated_request_time = (
            self.MAX_TWEETS * (self.REQUEST_DELAY_MIN + self.REQUEST_DELAY_MAX) / 2
        )
        estimated_total = estimated_scroll_time + estimated_request_time
        print(f"Estimated total time: {estimated_total:.1f} seconds")

        records = self.scrape()

        if not records:
            return None, None, None

        proc = Process()
        proc.upload_data(records)
        processing_result = proc.process_instructions()

        if processing_result["total_tweets"] > 0:

            if len(proc.tweets) > self.MAX_TWEETS:
                proc.tweets = proc.tweets[: self.MAX_TWEETS]
                proc.all_tweets_combined = proc.all_tweets_combined[: self.MAX_TWEETS]

            all_tweets_file, quotes_file, combined_file = proc.save_tweets(user, False)

            self.all_tweets_file = proc.tweets
            self.quotes_file = proc.tweets_with_quotes
            self.combined_file = proc.all_tweets_combined

            return self.all_tweets_file, self.quotes_file, self.combined_file

        return None, None, None

    def download(self, type=["all", "with_quotes", "combined"], path="./"):

        for t in type:

            if t == "all":

                with open(
                    path + self.user + "_all_tweets.json", "w", encoding="utf-8"
                ) as f:

                    json.dump(self.all_tweets_file, f, indent=2, ensure_ascii=False)

            elif t == "with_quotes":

                with open(
                    path + self.user + "_tweets_with_quotes.json", "w", encoding="utf-8"
                ) as f:

                    json.dump(self.quotes_file, f, indent=2, ensure_ascii=False)

            elif t == "combined":
                with open(
                    path + self.user + "_combined_tweets.json", "w", encoding="utf-8"
                ) as f:

                    json.dump(self.combined_file, f, indent=2, ensure_ascii=False)

            elif t == "raw":

                with open(
                    path + self.user + "_raw_tweets.json", "w", encoding="utf-8"
                ) as f:

                    json.dump(self.raw_file, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    scraper = Scraper("elonmusk", max_tweets=50, max_scrolls=5)
