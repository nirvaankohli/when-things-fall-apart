import os
import re
import pandas as pd
import nltk
from pathlib import Path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def ensure_nltk():

    try:
        stopwords.words("english")

    except LookupError:

        nltk.download("stopwords")

    try:

        word_tokenize("test")

    except LookupError:

        nltk.download("punkt")

        try:

            nltk.download("punkt_tab")

        except Exception:

            pass


ensure_nltk()
stop_words = set(stopwords.words("english"))


def ensure_text(x):
    return x if isinstance(x, str) else ("" if x is None else str(x))


def remove_handles(text: str) -> str:
    text = ensure_text(text)
    return re.sub(r"@\w+", " ", text)


def preprocess_text(text: str):

    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = text.lower()
    tokens = word_tokenize(text)

    filtered_tokens = []

    for token in tokens:

        if token not in stop_words and len(token) > 3:

            filtered_tokens.append(token)

    return filtered_tokens


root_dir = Path(__file__).parent.parent

DATA_PATH = root_dir / "data/data.csv"
names = ["sentiment", "tweet_id", "date", "flag", "user", "tweet_text"]

df = pd.read_csv(
    DATA_PATH,
    encoding="ISO-8859-1",
    names=names,
    dtype={"sentiment": str, "tweet_id": str},
)

df.drop(columns=["tweet_id", "date", "flag", "user"], inplace=True, errors="ignore")

df["tweet_text"] = df["tweet_text"].apply(remove_handles)

df["cleaned_tweet"] = df["tweet_text"].apply(preprocess_text)

df.to_csv("cleaned_data.csv", index=False)
