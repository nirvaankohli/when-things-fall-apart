## Overview

This piece of documentation is meant to give yall a view into the production of the project. This project is essentially split into 3 major parts.

1. [Scraping Twitter User's Tweets](#scraping-tweets)
2. [Sentiment Analysis on the User's Tweets: Both Pretrained & Trained from Scratch](#sentiment-analysis-on-tweets)
3. Displaying and Visualizing the Data on a Streamlit App

### Scraping Tweets

#### Failed Methods

Before landing on the method I currently use to scrape tweets off of Twitter. 
1. The First of these Methods was Trying to use *Other Python Libraries for Web Scraping*
   1. This included but not limited to the following:
      1. `snscrape` - This option was very promising but ended up being a flop. Everywhere I looked `snscrape` was recommended. When I tried it, however, *it was easily blocked by twitter's anti-scraping measures.*
      2. `requests` & `BeautifulSoup` - This was a last ditch effort in this first category and *flopped horrible.*
2. *Utilizing Third-Party Scraping Tools*
   * Even though no-code solutions like like `Octoparse`, `Apify`, and `ScrapeHero` *offered user-friendly interfaces, they came with a fee.*
   * *Templates and pre-built scrapers*: These often provided pre-built templates for scraping tasks, like as collecting tweets by username or search query. There was one fundamental issue; they didn't work 😭

So now you might be wondering-- *Nirvaan, if you didn't use those methods what did you use?*

Don't worry youngling, there is a solution:

*✨ Tada ✨*

#### How we get tweets

1. **Setup Browser:** We use `Playwright` to launch a headless Firefox browser that mimics a real user

2. **Navigate to Profile:** It goes to the Twitter/X profile page (e.g., https://x.com/username)

3. **Scroll and Capture:**

   * Scrolls down the page to load more tweets
   * Monitors network requests for Twitter's internal API calls (GraphQL endpoints)
   * Captures these API requests that contain tweet data
   * **The image below shows what we look for**:
  
![alt text](https://hc-cdn.hel1.your-objectstorage.com/s/v3/ae731fdcc349118aa202e4aaaf23494d4364e925_untitled_design__10_.png)

1. **Extract Data:** Replays the captured API requests to get the raw tweet data

#### How we process and save results

The system can process tweet data in two ways:

1. **During Scraping (Real-time):**
     * As tweets are scraped, the `Process` class immediately extracts clean data from Twitter's complex JSON responses
     * It automatically separates tweets into 3 categories: all tweets, tweets with quotes, and combined format
     * Saves processed data directly without storing raw files

2. **From Raw Files (Post-processing):**
     - Can load previously saved raw JSON files using `Process().upload_data("filename.json")`
     - Processes the same way but allows for re-processing with different settings
     - Useful for testing and data analysis without re-scraping

* **Save Formats:**
  1. **All Tweets** (`username_all.json`) - Clean individual tweets
  2. **With Quotes** (`username_with_quotes.json`) - Tweets that quote other tweets (nested structure)
  3. **Combined** (`username_combined.json`) - All tweets with quote data embedded

* **What Processing Does:**
  - Extracts key fields: text, timestamps, engagement metrics, language
  - Handles quoted tweets and reply chains
  - Sorts tweets chronologically (newest first)
  - Converts timestamps to standardized format

### Sentiment Analysis on Tweets

This project implements **two different approaches** to sentiment analysis, each with their own strengths:

####  Pretrained Model Approach

* **What it uses:**
  - `cardiffnlp/twitter-roberta-base-sentiment-latest` - A RoBERTa model specifically fine-tuned on Twitter data
  - Hugging Face Transformers pipeline for easy inference
  - GPU acceleration when available (CUDA support)

* **How it works:**
  1. Load the pretrained model via Transformers pipeline
  2. Feed tweet text directly into the model
  3. Get predictions: POSITIVE, NEGATIVE, or NEUTRAL with confidence scores
  4. Process in batches for efficiency

* **Pros:** 
  - Ready to use immediately
  - High accuracy on social media text
  - Handles modern slang and Twitter-specific language
  - No training data needed

#### From-Scratch Training Approach

* **What it uses:**
  - **Dataset:** Sentiment140 (1.6M tweets) downloaded via Kaggle API
  - **Model:** Logistic Regression with TF-IDF vectorization
  - **Features:** Unigrams + bigrams, 200K max features

* **The Process:**

  1. **Data Collection & Cleaning:**
     - Downloads Sentiment140 dataset using `kaggle_download.py`
     - Removes handles (@mentions), URLs, punctuation
     - Tokenizes and removes stopwords
     - Filters tokens (length > 3 characters)

  2. **Feature Engineering:**
     - TF-IDF vectorization converts text to numerical features
     - Uses 1-2 gram combinations (single words + word pairs)
     - Limits to top 200K features to prevent overfitting

  3. **Model Training:**
     - Logistic Regression with elastic net regularization
     - Balanced class weights to handle imbalanced data
     - 80/20 train/test split with stratification

  4. **Evaluation & Saving:**
     - Reports accuracy, precision, recall, F1-score
     - Saves trained model, vectorizer, and config files
     - Creates confusion matrix for detailed analysis

* **Pros:**
  - Full control over the model and features
  - Can customize for specific use cases
  - Explainable results (can see important features)

However only the pretrained the model is usable in the demo because the model trained from scratch is slower and is worse than the pretrained one.

### Streamlit Demo

After scraping and analysis, we needed a way to actually *see* what we built. Our choice of tool is streamlit, a python library for demo-ing various projects.

#### The Demo Flow

The app follows a pretty straightforward user journey:

1. **User Input**: Enter a Twitter handle and specify how many tweets to analyze (10-100 tweets)
2. **The Magic Happens**: 
   - Scraper fires up and does its thing
   - Sentiment analysis model loads up
   - Everything gets processed and visualized
3. **Results**: Multiple charts, stats, and insights get displayed

#### What You'll See

**Basic Visualizations:**
- **Sentiment Distribution Pie Chart** - Pie chart showing positive vs negative vibes
- **Sentiment Score Histogram** - Shows the spread of sentiment scores from -1 (pure negativity) to +1 (rainbows and sunshine)
- **Timeline Scatter Plot** - See how someone's mood changes over time, with tweet size based on engagement

**Summary Statistics:**
- Average sentiment score
- Percentage of positive tweets  
- Most/least positive scores
- The actual tweets that hit the extremes

**"When It Falls Apart"**
This segment basically t identifies sustained periods of negativity(at least 3 days with multiple tweets showing consistent negativity)

**How "When It Falls Apart" Works:**
- Scans through all possible time periods in the data
- Filters for periods lasting at least 3 days with 3+ tweets
- Calculates average sentiment for each period
- Identifies the period with the lowest average sentiment

**What It Shows:**
- Duration and date range of the darkest period
- All tweets from that period, sorted by sentiment (worst first)
- Interactive timeline with the dark period highlighted in red
- Statistics about engagement during the rough patch

#### The Technical Bits

**Visualization Stack:**
- **Plotly Express** for interactive charts (because static charts are so 2010)
- **Custom HTML/CSS** for tweet displays with color-coded sentiment borders
- **Responsive layout** using Streamlit's column system

#### Behind the Scenes Page

This document!!!!
