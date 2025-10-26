import sys
import streamlit as st
from scraping.scrape import Scraper
import pandas as pd
import asyncio
from sentiment_analysis.pretrained.pipeline.inference import infer_sentiment
import re
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import sys, subprocess

res = subprocess.run(
    [sys.executable, "-m", "playwright", "install", "--with-deps", "firefox"],
    capture_output=True,
    text=True,
)

res = subprocess.run(
    ["playwright", "install", "chromium"], capture_output=True, text=True
)

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def clean_text(text):

    new_text = text.replace(r"http\S+", "")

    if len(new_text) < 5:

        new_text = text

    text = new_text.replace("@", "")
    text = text.replace("\n", " ").replace("\r", " ").strip()
    return " ".join(text.split())


st.set_page_config(
    page_title="Twitter Sentiment Analysis", layout="wide", page_icon="🐦"
)


def home_page():

    st.title("Twitter Profile Sentiment Analysis App")

    user = st.text_input("Enter Twitter Handle", key="twitter_handle")
    tweets = st.number_input(
        "Number of Tweets to Scrape", min_value=10, max_value=100, value=50, step=2
    )

    submit = st.button("Start Analysis")

    if user and tweets and submit:

        with st.spinner("Initializing the Scraper..."):
            scraper = Scraper(user, max_tweets=tweets, max_scrolls=5)
        with st.spinner("Setting up Sentiment Analysis Model..."):
            sentiment_infer = infer_sentiment()
        with st.spinner("Estimating time to complete..."):
            estimated_time = scraper.get_estimated_time()
            st.info(f"Estimated time to complete: {estimated_time:.1f} seconds")

        with st.spinner("Scraping and processing tweets..."):

            all_tweets_file, quotes_file, combined_file = scraper.scrape_and_process(
                user
            )

            st.success("Scraping and processing completed successfully!")

            wanted_cols = ["text", "created_at", "favorite_count", "retweet_count"]

            df = pd.DataFrame(scraper.all_tweets_file)[wanted_cols]

            df["text"] = df["text"].apply(clean_text)
            st.subheader("Scraped Tweets")
            st.dataframe(df)

        with st.spinner("Analyzing sentiment..."):

            sentiment_results = sentiment_infer.batch_scores(df["text"].tolist())

            sentiment_df = df.copy()
            sentiment_df["sentiment_score"] = sentiment_results

            sentiment_df["sentiment_category"] = sentiment_df["sentiment_score"].apply(
                lambda x: (
                    "Positive" if x > 0.1 else "Negative" if x < -0.1 else "Neutral"
                )
            )

            st.success("Sentiment analysis completed successfully!")

            display_df = sentiment_df[
                [
                    "text",
                    "sentiment_score",
                    "sentiment_category",
                    "favorite_count",
                    "retweet_count",
                ]
            ]
            display_df.columns = [
                "Tweet",
                "Sentiment Score",
                "Category",
                "Likes",
                "Retweets",
            ]

            st.subheader("Sentiment Analysis Results")
            st.dataframe(display_df)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Sentiment Distribution")
                sentiment_counts = sentiment_df["sentiment_category"].value_counts()
                fig_pie = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title="Overall Sentiment Distribution",
                    color_discrete_map={
                        "Positive": "#28a745",
                        "Negative": "#dc3545",
                        "Neutral": "#6c757d",
                    },
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.subheader("Sentiment Score Distribution")
                fig_hist = px.histogram(
                    sentiment_df,
                    x="sentiment_score",
                    nbins=20,
                    title="Sentiment Score Distribution",
                    labels={
                        "sentiment_score": "Sentiment Score",
                        "count": "Number of Tweets",
                    },
                )
                fig_hist.update_traces(marker_color="#17a2b8")
                st.plotly_chart(fig_hist, use_container_width=True)

            if len(sentiment_df) > 5:
                st.subheader("Sentiment Over Time")
                try:
                    sentiment_df["created_at"] = pd.to_datetime(
                        sentiment_df["created_at"]
                    )
                    sentiment_df = sentiment_df.sort_values("created_at")

                    fig_time = px.scatter(
                        sentiment_df,
                        x="created_at",
                        y="sentiment_score",
                        color="sentiment_category",
                        size="favorite_count",
                        hover_data=["retweet_count"],
                        title="Sentiment Trends Over Time",
                        color_discrete_map={
                            "Positive": "#28a745",
                            "Negative": "#dc3545",
                            "Neutral": "#6c757d",
                        },
                    )
                    fig_time.add_hline(
                        y=0,
                        line_dash="dash",
                        line_color="gray",
                        annotation_text="Neutral",
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
                except:
                    st.info("Could not create time series visualization")

            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                avg_sentiment = sentiment_df["sentiment_score"].mean()
                st.metric("Average Sentiment", f"{avg_sentiment:.3f}")

            with col2:
                positive_pct = (
                    sentiment_df["sentiment_category"] == "Positive"
                ).mean() * 100
                st.metric("Positive %", f"{positive_pct:.1f}%")

            with col3:
                most_positive = sentiment_df.loc[
                    sentiment_df["sentiment_score"].idxmax()
                ]
                st.metric(
                    "Most Positive Score", f"{most_positive['sentiment_score']:.3f}"
                )

            with col4:
                most_negative = sentiment_df.loc[
                    sentiment_df["sentiment_score"].idxmin()
                ]
                st.metric(
                    "Most Negative Score", f"{most_negative['sentiment_score']:.3f}"
                )

            if len(sentiment_df) > 0:
                st.subheader("Notable Tweets")
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Most Positive Tweet:**")
                    st.write(f"Score: {most_positive['sentiment_score']:.3f}")
                    st.write(f"'{most_positive['text'][:200]}...'")

                with col2:
                    st.write("**Most Negative Tweet:**")
                    st.write(f"Score: {most_negative['sentiment_score']:.3f}")
                    st.write(f"'{most_negative['text'][:200]}...'")

            if len(sentiment_df) > 10:
                st.subheader("When It Falls Apart...")
                st.write(
                    "*Identifying the most negative period in the timeline (minimum 3 days, 3+ tweets)*"
                )

                try:

                    sentiment_df["created_at"] = pd.to_datetime(
                        sentiment_df["created_at"]
                    )
                    sentiment_df = sentiment_df.sort_values("created_at")

                    def find_darkest_period(df):
                        min_days = 3
                        min_tweets = 3
                        worst_avg = float("inf")
                        darkest_period = None

                        for start_idx in range(len(df)):
                            start_date = df.iloc[start_idx]["created_at"]

                            for end_idx in range(start_idx + min_tweets - 1, len(df)):
                                end_date = df.iloc[end_idx]["created_at"]

                                days_diff = (end_date - start_date).days
                                if days_diff < min_days:
                                    continue

                                period_tweets = df.iloc[start_idx : end_idx + 1]

                                if len(period_tweets) < min_tweets:
                                    continue

                                avg_sentiment = period_tweets["sentiment_score"].mean()

                                if avg_sentiment < worst_avg:
                                    worst_avg = avg_sentiment
                                    darkest_period = period_tweets.copy()

                        return darkest_period, worst_avg

                    darkest_period, worst_avg = find_darkest_period(sentiment_df)

                    if darkest_period is not None and len(darkest_period) >= 3:

                        col1, col2 = st.columns([1, 2])

                        with col1:
                            # Calculate period duration
                            period_start = darkest_period["created_at"].min()
                            period_end = darkest_period["created_at"].max()
                            period_days = (period_end - period_start).days + 1

                            st.metric(
                                "Darkest Period Avg",
                                f"{worst_avg:.3f}",
                                help="Average sentiment score during the darkest period",
                            )
                            st.metric(
                                "Period Duration",
                                f"{period_days} days",
                                help="Length of the darkest period",
                            )
                            st.metric(
                                "Date Range",
                                f"{period_start.strftime('%m/%d')} - {period_end.strftime('%m/%d')}",
                                help="When the darkest period occurred",
                            )

                            period_stats = {
                                "Avg Sentiment": darkest_period[
                                    "sentiment_score"
                                ].mean(),
                                "Tweets in Period": len(darkest_period),
                                "Negative Tweets": len(
                                    darkest_period[
                                        darkest_period["sentiment_score"] < -0.1
                                    ]
                                ),
                                "Worst Tweet": darkest_period["sentiment_score"].min(),
                                "Total Likes": darkest_period["favorite_count"].sum(),
                                "Total Retweets": darkest_period["retweet_count"].sum(),
                            }

                            st.write("**Period Statistics:**")
                            for key, value in period_stats.items():
                                if isinstance(value, float):
                                    st.write(f"• {key}: {value:.3f}")
                                else:
                                    st.write(f"• {key}: {value}")

                        with col2:
                            st.write("**Tweets from the darkest period:**")

                            # Sort tweets in the period by sentiment (worst first)
                            darkest_sorted = darkest_period.sort_values(
                                "sentiment_score"
                            )

                            for idx, tweet in darkest_sorted.iterrows():
                                if tweet["sentiment_score"] < -0.3:
                                    color = "🔴"
                                elif tweet["sentiment_score"] < -0.1:
                                    color = "🟡"
                                else:
                                    color = "🟢"

                                sentiment_color = (
                                    "red"
                                    if tweet["sentiment_score"] < -0.1
                                    else (
                                        "orange"
                                        if tweet["sentiment_score"] < 0.1
                                        else "green"
                                    )
                                )

                                st.markdown(
                                    f"""
                                <div style="border-left: 3px solid {sentiment_color}; padding-left: 10px; margin: 10px 0;">
                                    <small><strong>Score: {tweet['sentiment_score']:.3f}</strong> | {tweet['created_at'].strftime('%m/%d %H:%M')}</small><br>
                                    <em>"{tweet['text'][:150]}..."</em><br>
                                    <small>❤️ {tweet['favorite_count']} | 🔄 {tweet['retweet_count']}</small>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )

                        st.write(
                            "**Sentiment Timeline with Darkest Period Highlighted:**"
                        )

                        # Create timeline with all tweets
                        fig_timeline = px.scatter(
                            sentiment_df,
                            x="created_at",
                            y="sentiment_score",
                            color="sentiment_category",
                            size="favorite_count",
                            title="Sentiment Timeline - Darkest Period Highlighted",
                            color_discrete_map={
                                "Positive": "#28a745",
                                "Negative": "#dc3545",
                                "Neutral": "#6c757d",
                            },
                            labels={
                                "sentiment_score": "Sentiment Score",
                                "created_at": "Time",
                            },
                        )

                        # Highlight the darkest period
                        fig_timeline.add_vrect(
                            x0=darkest_period["created_at"].min(),
                            x1=darkest_period["created_at"].max(),
                            fillcolor="red",
                            opacity=0.3,
                            annotation_text=f"Darkest Period<br>Avg: {worst_avg:.3f}",
                            annotation_position="top left",
                        )

                        # Add trend line for the darkest period
                        darkest_period_sorted = darkest_period.sort_values("created_at")
                        fig_timeline.add_scatter(
                            x=darkest_period_sorted["created_at"],
                            y=darkest_period_sorted["sentiment_score"],
                            mode="lines+markers",
                            line=dict(color="red", width=3),
                            marker=dict(size=8, color="darkred"),
                            name="Darkest Period Trend",
                            hovertemplate="<b>Darkest Period</b><br>Score: %{y:.3f}<br>%{x}<extra></extra>",
                        )

                        fig_timeline.add_hline(y=0, line_dash="dash", line_color="gray")
                        fig_timeline.add_hline(
                            y=worst_avg,
                            line_dash="dot",
                            line_color="red",
                            annotation_text=f"Period Avg: {worst_avg:.3f}",
                        )
                        fig_timeline.update_layout(height=500)

                        st.plotly_chart(fig_timeline, use_container_width=True)

                    else:
                        st.warning(
                            "Could not find a period of at least 3 days with 3+ tweets for analysis."
                        )

                except Exception as e:
                    st.error(f"Could not analyze darkest period: {str(e)}")
                    st.info(
                        "This analysis requires tweets with valid timestamps spanning multiple days."
                    )
            else:
                st.info("Need more tweets (10+) to analyze sentiment periods.")


def about_page():

    st.title("How it works: Behind The Scenes")

    try:

        with open("bts.md", "r", encoding="utf-8") as file:

            content = file.read()

        st.markdown(content)

    except FileNotFoundError:

        st.error("bts.md file not found")


scraper = Scraper("elonmusk", max_tweets=50, max_scrolls=5)


home = st.Page(home_page, title="Home(Demo)", icon="🐦")
about = st.Page(about_page, title="How it works: Behind The Scenes", icon="📃")

pg = st.navigation([home, about])
pg.run()
