import snscrape.modules.twitter as sntwitter
import pandas as pd

tweets_list = []

# Config

user = "nirvaankohli"
max = 1000

for i, tweet in enumerate(sntwitter.TwitterUserScraper(user).get_items()):
    if i > max:
        break

    tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])

tweets_df = pd.DataFrame(
    tweets_list, columns=["Datetime", "Tweet Id", "Text", "Username"]
)
tweets_df.to_csv(f"{user}_tweets.csv", index=False)
