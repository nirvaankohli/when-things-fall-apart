import json
import datetime
from dateutil import parser


def test_json_keys(*args):
    args_list = list(args)[1:]
    data = args[0]

    for item in args_list:
        if isinstance(item, str):
            try:
                data = data[item]
            except (KeyError, TypeError):
                return False
            except Exception:
                return False

        elif isinstance(item, int):
            try:
                data = data[item]
            except (IndexError, TypeError):
                return False
            except Exception:
                return False

    return True


class Process:
    def __init__(self, data_type=None):
        self.data = []
        self.data_type = data_type
        self.tweets = []
        self.tweets_with_quotes = []
        self.all_tweets_combined = []

    def get_data_type_off_input(self, data, additional_info=None) -> bool:
        if type(data) is str:
            self.data_type = "path" if self.data_type is None else self.data_type
            return True

        if additional_info == "loop" and not self.data_type:
            self.data_type = "item_loop_raw"
        elif not self.data_type:
            self.data_type = "raw"

        return False

    def upload_data(self, data):
        is_path = self.get_data_type_off_input(data)

        if is_path:
            with open(data, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = data

    def get_data(self):
        return self.data

    def extract_tweet_info(self, tweet_legacy):
        created_at_raw = tweet_legacy.get("created_at", "")
        created_at_parsed = None
        created_at_iso = None

        if created_at_raw:
            try:
                created_at_parsed = parser.parse(created_at_raw)
                created_at_iso = created_at_parsed.isoformat()
            except:
                created_at_iso = created_at_raw

        return {
            "id": tweet_legacy.get("id_str", ""),
            "text": tweet_legacy.get("full_text", ""),
            "created_at": created_at_iso,
            "created_at_timestamp": (
                created_at_parsed.timestamp() if created_at_parsed else 0
            ),
            "retweet_count": tweet_legacy.get("retweet_count", 0),
            "favorite_count": tweet_legacy.get("favorite_count", 0),
            "reply_count": tweet_legacy.get("reply_count", 0),
            "quote_count": tweet_legacy.get("quote_count", 0),
            "lang": tweet_legacy.get("lang", ""),
            "in_reply_to_status_id": tweet_legacy.get("in_reply_to_status_id_str", ""),
            "in_reply_to_user_id": tweet_legacy.get("in_reply_to_user_id_str", ""),
            "in_reply_to_screen_name": tweet_legacy.get("in_reply_to_screen_name", ""),
        }

    def process_tweet_entry(self, entry):
        tweets_found = []

        if entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}):
            tweet_result = entry["content"]["itemContent"]["tweet_results"]["result"]

            if "legacy" in tweet_result:
                main_tweet = self.extract_tweet_info(tweet_result["legacy"])
                quoted_tweet = None

                if "quoted_status_result" in tweet_result:
                    quoted_result = tweet_result["quoted_status_result"]["result"]
                    if "legacy" in quoted_result:
                        quoted_tweet = self.extract_tweet_info(quoted_result["legacy"])
                        self.tweets_with_quotes.append(
                            {"main_tweet": main_tweet, "quoted_tweet": quoted_tweet}
                        )

                tweets_found.append(
                    {"type": "main", "tweet": main_tweet, "quoted_tweet": quoted_tweet}
                )

                combined_tweet = main_tweet.copy()
                combined_tweet["quote"] = quoted_tweet if quoted_tweet else None
                self.all_tweets_combined.append(combined_tweet)

        return tweets_found

    def get_instructions(self):
        for item in self.data:
            if isinstance(item, dict) and "data" in item:
                success = test_json_keys(
                    item,
                    "data",
                    "user",
                    "result",
                    "timeline",
                    "timeline",
                    "instructions",
                )
                if success:
                    timeline_data = item["data"]["user"]["result"]["timeline"][
                        "timeline"
                    ]
                    return timeline_data["instructions"]
        return []

    def process_instructions(self):
        instructions = self.get_instructions()
        all_tweets = []

        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries = instruction.get("entries", [])

                for entry in entries:
                    if (
                        entry.get("content", {}).get("entryType")
                        == "TimelineTimelineItem"
                    ):
                        if (
                            entry.get("content", {})
                            .get("itemContent", {})
                            .get("itemType")
                            == "TimelineTweet"
                        ):
                            tweets_from_entry = self.process_tweet_entry(entry)
                            all_tweets.extend(tweets_from_entry)

        self.tweets = [tweet_data["tweet"] for tweet_data in all_tweets]

        self.tweets.sort(key=lambda x: x["created_at_timestamp"], reverse=True)
        self.all_tweets_combined.sort(
            key=lambda x: x["created_at_timestamp"], reverse=True
        )
        self.tweets_with_quotes.sort(
            key=lambda x: x["main_tweet"]["created_at_timestamp"], reverse=True
        )

        return {
            "total_tweets": len(self.tweets),
            "tweets_with_quotes": len(self.tweets_with_quotes),
            "combined_tweets": len(self.all_tweets_combined),
        }

    def save_tweets(self, filename_prefix="tweets", save=True):

        if save:

            tweets_filename = f"{filename_prefix}_all.json"

            with open(tweets_filename, "w", encoding="utf-8") as f:
                json.dump(self.tweets, f, indent=2, ensure_ascii=False)

            quotes_filename = None
            if self.tweets_with_quotes:
                quotes_filename = f"{filename_prefix}_with_quotes.json"
                with open(quotes_filename, "w", encoding="utf-8") as f:
                    json.dump(self.tweets_with_quotes, f, indent=2, ensure_ascii=False)

            combined_filename = f"{filename_prefix}_combined.json"
            with open(combined_filename, "w", encoding="utf-8") as f:
                json.dump(self.all_tweets_combined, f, indent=2, ensure_ascii=False)

        return self.tweets, self.tweets_with_quotes, self.all_tweets_combined
    
    def return_tweets(self, processed_type="all"):
        if processed_type == "all_types":
        
            return self.tweets, self.tweets_with_quotes, self.all_tweets_combined
        elif processed_type == "all":
            return self.tweets
        elif processed_type == "with_quotes":
        
            return self.tweets_with_quotes
        elif processed_type == "combined":
            return self.all_tweets_combined
        else:
            return []


def main():
    p = Process()
    p.upload_data("elonmusk_tweets_raw.json")
    result = p.process_instructions()
    all_tweets_file, quotes_file, combined_file = p.save_tweets("elonmusk")


if __name__ == "__main__":
    main()
