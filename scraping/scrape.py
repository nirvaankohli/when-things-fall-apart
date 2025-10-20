# IMPORTS - Thinking of using playwright
from playwright.sync_api import sync_playwright
import json, re, datetime

# CONFIG

timezone = datetime.timezone.utc
user = "elonmusk"
start = datetime.date(2025, 5, 1).strftime("%Y-%m-%dT%H:%M:%SZ")
end = datetime.date(2025, 6, 1).strftime("%Y-%m-%dT%H:%M:%SZ")

print(f"Scraping posts from {user} between {start} and {end}")

with sync_playwright() as p:

    # SETUP BROWSER

    b = p.firefox.launch(headless=True)
    ctx = b.new_context()
    page = ctx.new_page()
    captured = []

    # INTERCEPT REQUESTS

    def log_request(req):

        # this basically filters out the requests we want

        if "graphql" in req.url and (
            "UserTweets" in req.url or "TweetResultByRestId" in req.url
        ):

            if start in req.url or end in req.url or "timeline" in req.url:

                captured.append(req)

    # NAVIGATE TO PAGE & OTHER STUFF

    page.on("request", log_request)
    page.goto(f"https://x.com/{user}")
    page.wait_for_timeout(8000)
    page.mouse.wheel(0, 50000)
    page.wait_for_timeout(4000)

    # PROCESS CAPTURED REQUESTS

    records = []

    for req in captured:

        try:

            r = page.request.fetch(req.url, method=req.method, headers=req.headers)
            data = r.json()
            records.append(data)

        except Exception:

            pass

    with open(f"{user}_tweets_raw.json", "w") as f:

        json.dump(records, f)
