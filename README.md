# When Things Fall Apart - Twitter Sentiment Analyzer

A comprehensive Twitter sentiment analysis tool that scrapes user tweets and analyzes emotional patterns over time, with a special focus on identifying periods of sustained negativity.
https://hc-cdn.hel1.your-objectstorage.com/s/v3/d1c6ecb68f884e269c1f926043e109a68c6daa85_screen_recording_2025-10-26_181314.mp4
## Quick Start

1. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Run the Streamlit Demo**
   ```
   streamlit run app.py
   ```

3. **Enter a Twitter handle** and analyze their sentiment patterns!

## Components

### 1. Tweet Scraping

#### Why Our Approach Works

After testing multiple methods including `snscrape`, `requests` + `BeautifulSoup`, and third-party tools like `Octoparse` and `Apify`, we found they were either easily blocked or came with fees.

**Our Solution: Playwright + Network Monitoring**

**How It Works:**

1. **Setup Browser:** Uses `Playwright` to launch a headless Firefox browser that mimics real user behavior

2. **Navigate to Profile:** Goes to the Twitter/X profile page (e.g., https://x.com/username)

3. **Scroll and Capture:**
   - Scrolls down the page to load more tweets
   - Monitors network requests for Twitter's internal API calls (GraphQL endpoints)
   - Captures these API requests that contain tweet data
   - **The image below shows what we look for**:
  
![alt text](https://hc-cdn.hel1.your-objectstorage.com/s/v3/ae731fdcc349118aa202e4aaaf23494d4364e925_untitled_design__10_.png)

4. **Extract Data:** Replays the captured API requests to get the raw tweet data

#### Data Processing Pipeline

The system processes tweet data in two ways:

1. **Real-time Processing:**
   - Extracts clean data from Twitter's complex JSON responses during scraping
   - Automatically categorizes tweets: all tweets, tweets with quotes, and combined format
   - Saves processed data directly without storing raw files

2. **Post-processing:**
   - Can load previously saved raw JSON files using `Process().upload_data("filename.json")`
   - Allows for re-processing with different settings
   - Useful for testing and data analysis without re-scraping

**Output Formats:**
- **All Tweets** (`username_all.json`) - Clean individual tweets
- **With Quotes** (`username_with_quotes.json`) - Tweets that quote other tweets
- **Combined** (`username_combined.json`) - All tweets with quote data embedded

### 2. Sentiment Analysis

Two different approaches to sentiment analysis, each with their own strengths:

#### Pretrained Model Approach

**Technology Stack:**
- `cardiffnlp/twitter-roberta-base-sentiment-latest` - RoBERTa model fine-tuned on Twitter data
- Hugging Face Transformers pipeline for easy inference
- GPU acceleration when available (CUDA support)

**Process:**
1. Load the pretrained model via Transformers pipeline
2. Feed tweet text directly into the model
3. Get predictions: POSITIVE, NEGATIVE, or NEUTRAL with confidence scores
4. Process in batches for efficiency

**Advantages:**
- Ready to use immediately
- High accuracy on social media text
- Handles modern slang and Twitter-specific language
- No training data needed

#### Custom Training Approach

**Technology Stack:**
- **Dataset:** Sentiment140 (1.6M tweets) downloaded via Kaggle API
- **Model:** Logistic Regression with TF-IDF vectorization
- **Features:** Unigrams + bigrams, 200K max features

**Training Pipeline:**

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

**Advantages:**
- Full control over the model and features
- Can customize for specific use cases
- Explainable results (can see important features)

> **Note:** The pretrained model is used in the demo as it's faster and more accurate than the custom-trained model.

### 3. Streamlit Web Application

A user-friendly interface for analyzing Twitter sentiment patterns.

#### User Flow

1. **Input**: Enter a Twitter handle and specify tweet count (10-100 tweets)
2. **Processing**: 
   - Scraper collects tweets
   - Sentiment analysis model processes data
   - Visualizations are generated
3. **Results**: Multiple charts, statistics, and insights

#### Visualizations

**Core Analytics:**
- **Sentiment Distribution Pie Chart** - Overview of positive vs negative sentiment
- **Sentiment Score Histogram** - Distribution of scores from -1 (negative) to +1 (positive)
- **Timeline Scatter Plot** - Sentiment changes over time with engagement-based sizing

**Summary Statistics:**
- Average sentiment score
- Percentage of positive tweets  
- Most/least positive scores
- Extreme sentiment examples

#### "When Things Fall Apart" Feature

This special analysis identifies sustained periods of negativity (at least 3 days with multiple tweets showing consistent negativity).

**How It Works:**
- Scans all possible time periods in the data
- Filters for periods lasting at least 3 days with 3+ tweets
- Calculates average sentiment for each period
- Identifies the period with the lowest average sentiment

**Output:**
- Duration and date range of the darkest period
- All tweets from that period, sorted by sentiment
- Interactive timeline with the dark period highlighted in red
- Engagement statistics during the rough patch

#### Technical Implementation

**Visualization Stack:**
- **Plotly Express** for interactive charts
- **Custom HTML/CSS** for tweet displays with color-coded sentiment borders
- **Responsive layout** using Streamlit's column system

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nirvaankohli/when-things-fall-apart.git
   cd when-things-fall-apart
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Set up Playwright**
   ```
   playwright install firefox
   ```

4. **Configure Kaggle API** (for custom training)
   - Place your `kaggle.json` in `~/.kaggle/`
   - Or set environment variables `KAGGLE_USERNAME` and `KAGGLE_KEY`

## Usage

### Run the Web Application
```
streamlit run app.py
```

### Use Individual Components

**Scrape tweets:**
```
from scraping.scrape import TwitterScraper
scraper = TwitterScraper()
scraper.scrape_user("username", max_tweets=100)
```

**Analyze sentiment:**
```
from sentiment_analysis.pretrained.inference import analyze_sentiment
results = analyze_sentiment(["I love this!", "This is terrible"])
```


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- **Cardiff NLP** for the pretrained Twitter sentiment model
- **Sentiment140** dataset for training data
- **Playwright** for web scraping capabilities

