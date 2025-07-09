# Product Definition: Advisor

## 1. Overview
**Advisor** is a command-line application that delivers investment recommendations (`BUY`, `SELL`, `HOLD`) for a configurable list of stock symbols.

The system comprises two primary components:

1. **The Assistant** – a background Python **scraper** that periodically gathers data from  
   - official SEC filings  
   - financial-news APIs  
   - designated Reddit forums
2. **The Advisor** – a CLI **analysis engine** that reads the collected data, calculates a weighted sentiment score, and prints a concise recommendation report on demand.

> *Sentiment classification of qualitative data (news, filings, forum posts) is performed by an external Large Language Model (LLM) via API.*

---

## 2. Core Components

### 2.1 The Assistant – Data Scraper
| Aspect      | Detail                                                                                                                                        |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Function** | Runs on schedule to collect & store data.                                                                                                     |
| **Execution** | `assistant.py`, triggered by cron (or any scheduler).                                                                                         |
| **Sources** | • **Financial Reports:** SEC EDGAR (10-K, 10-Q)  <br>• **Financial News:** free news API  <br>• **Public Forums:** Reddit subreddits via PRAW |
| **Storage** | Writes to local SQLite DB `stocks.db`.                                                                                                        |

### 2.2 The Advisor – Analysis Engine
| Aspect      | Detail |
|-------------|--------|
| **Function** | Fetches data, performs analysis, emits report. |
| **Execution** | `advisor.py`, run manually from terminal. |
| **Analysis steps** | 1. Pull latest data for each symbol.<br>2. Send text to LLM API → get sentiment & summary.<br>3. Compute final weighted sentiment score. |
| **Output** | Prints formatted recommendations to console. |

---

## 3. Feature Breakdown

### 3.1 Data Collection (`assistant.py`)
* **SEC Filings** – query EDGAR for latest 10-K/10-Q, download text.  
* **Financial News** – call free news API (e.g., Alpha Vantage, FMP) for articles.  
* **Reddit** – pull recent posts + top comments from configured subreddits with PRAW.

### 3.2 Data Storage – SQLite (`sentinel.db`)
| Table | Columns | Purpose |
|-------|---------|---------|
| `stocks` | `id`, `symbol` | List of monitored tickers |
| `data_points` | `id`, `stock_id`, `source`, `content`, `url`, `collected_at` | Raw text artifacts |

### 3.3 Sentiment Analysis (LLM)
1. Advisor selects unanalyzed rows.  
2. Builds prompt → sends to LLM.  
3. Expects JSON:  
   ```jsonc
   {
     "score": 0.23,            // -1.0 … 1.0
     "summary": "One-paragraph gist"
   }
