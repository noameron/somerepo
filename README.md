# Investment Advisor

A Reddit-based sentiment analysis tool for stock investment recommendations.

## Overview

This tool collects stock mentions from Reddit, analyzes sentiment, and provides BUY/SELL/HOLD recommendations based on community sentiment.

## Features

- **Data Collection**: Scrapes stock mentions from Reddit (r/WallStreetBets)
- **Sentiment Analysis**: Analyzes sentiment of mentions using keyword-based scoring
- **Investment Recommendations**: Provides BUY/SELL/HOLD advice based on sentiment thresholds
- **CLI Tools**: Easy-to-use command line interfaces for data collection and analysis

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Configure Reddit API

1. Go to https://www.reddit.com/prefs/apps
2. Create a new "script" application
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` with your Reddit API credentials:
   ```
   CLIENT_ID="your_reddit_client_id"
   CLIENT_SECRET="your_reddit_client_secret"
   USER_AGENT="script:advisor-sentiment:v1.0 (by /u/your_username)"
   ```

### 3. Collect Data

```bash
python3 run_assistant.py
```

This will:
- Connect to Reddit API
- Scan r/WallStreetBets for stock mentions (AAPL, TSLA, GOOG)
- Store mentions in local SQLite database

### 4. Get Investment Recommendations

```bash
python3 run_advisor.py
```

This will:
- Analyze sentiment of all collected mentions
- Provide BUY/SELL/HOLD recommendations
- Show sentiment scores and mention counts

## CLI Usage

### Data Collection (Assistant)

```bash
# Collect data from Reddit (default)
python3 run_assistant.py

# Specify source explicitly
python3 run_assistant.py --source reddit

# Use custom config file
python3 run_assistant.py --config my_config.json
```

### Analysis & Recommendations (Advisor)

```bash
# Analyze all tracked stocks
python3 run_advisor.py

# Analyze specific stocks
python3 run_advisor.py --stocks AAPL TSLA

# Get detailed analysis for one stock
python3 run_advisor.py --detail AAPL
```

## Configuration

### Stock Symbols

Edit `advisor/scrapers/reddit/config.json` to change tracked stocks:

```json
{
  "max_days": 3,
  "min_days": 1,
  "subreddits": ["WallStreetBets"],
  "tickers": ["AAPL", "TSLA", "GOOG", "MSFT"]
}
```

### Sentiment Thresholds

Recommendation logic (configured in `advisor/core/config.py`):
- **BUY**: Sentiment ≥ 0.7 with ≥5 mentions
- **SELL**: Sentiment ≤ 0.3 with ≥5 mentions  
- **HOLD**: Otherwise (neutral sentiment or insufficient data)

## Project Structure

```
advisor/
├── core/           # Core functionality
│   ├── config.py   # Configuration management
│   ├── database.py # SQLite operations
│   └── data_source.py # Base scraper class
├── scrapers/       # Data collection
│   └── reddit/     # Reddit scraper
├── analysis/       # Sentiment analysis
│   └── sentiment.py
└── cli/           # Command line interfaces
    ├── assistant.py # Data collection CLI
    └── advisor.py   # Analysis CLI
```

## Database

The tool uses SQLite with two main tables:
- `stocks`: Stock symbols being tracked
- `mentions`: Individual Reddit mentions with sentiment scores

Database file: `advisor.db` (created automatically)

## Security

- API credentials are stored in `.env` file (not committed to git)
- No sensitive data is logged or exposed
- All database queries use parameterized statements

## Extending

### Add New Data Sources

1. Create new scraper in `advisor/scrapers/`
2. Inherit from `DataSource` base class
3. Implement required methods
4. Add to assistant CLI

### Enhanced Sentiment Analysis

The current implementation uses keyword-based sentiment analysis. To integrate with LLM APIs:

1. Add API credentials to `.env`
2. Modify `SentimentAnalyzer.analyze_text()` method
3. Replace keyword logic with API calls

## License

This project is for educational purposes. Ensure compliance with Reddit's API terms and rate limits.