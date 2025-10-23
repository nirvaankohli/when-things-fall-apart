from scrape import Scraper
import json
import time


def demo():

    small_scraper = Scraper(
        user="elonmusk",
        max_tweets=10,
        max_scrolls=3,
        scroll_pause_min=1,
        scroll_pause_max=2,
    )

    small_scraper.scrape_and_process("elonmusk")
    small_scraper.download(type=["all", "with_quotes", "combined"], path="./")

    print(f"   Max tweets: {small_scraper.MAX_TWEETS}")
    print(f"   Max scrolls: {small_scraper.MAX_SCROLLS}")


if __name__ == "__main__":
    demo()
