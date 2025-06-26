import json
import os
import re
import time
from datetime import datetime, timezone

import praw
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")

if not (CLIENT_ID and CLIENT_SECRET and USER_AGENT):
    raise RuntimeError("Missing Reddit API credentials. Check your .env file.")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

max_days = config.get("max_days", 7)
min_days = config.get("min_days", 0)
subreddits = config.get("subreddits", [])
tickers = [t.upper() for t in config.get("tickers", [])]

ticker_pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in tickers) + r")\b")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

def age_in_days(utc_timestamp: float) -> float:
    created = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return (now - created).total_seconds() / 86400.0

def scrape():
    results = []
    for subreddit_name in subreddits:
        print(f"Scanning r/{subreddit_name}...")
        sub = reddit.subreddit(subreddit_name)

        for submission in sub.new(limit=None):
            age = age_in_days(submission.created_utc)
            if age > max_days:
                break

            if age < min_days:
                continue

            text = (submission.title or "") + "\n" + (getattr(submission, "selftext", "") or "")
            if ticker_pattern.search(text.upper()):
                results.append({
                    "type": "submission",
                    "subreddit": subreddit_name,
                    "id": submission.id,
                    "author": str(submission.author),
                    "age_days": round(age, 2),
                    "content": text.strip(),
                    "url": submission.url
                })

        for comment in sub.comments(limit=None):
            age = age_in_days(comment.created_utc)
            if age > max_days:
                break
            if age < min_days:
                continue

            body = comment.body or ""
            if ticker_pattern.search(body.upper()):
                results.append({
                    "type": "comment",
                    "subreddit": subreddit_name,
                    "id": comment.id,
                    "author": str(comment.author),
                    "age_days": round(age, 2),
                    "content": body.strip(),
                    "permalink": f"https://reddit.com{comment.permalink}"
                })

        time.sleep(2)

    for item in results:
        print(f"[{item['subreddit']}] {item['type']} ({item['age_days']} days) by {item['author']}: {item['content'][:100]}... -> {item.get('url', item.get('permalink'))}")

if __name__ == "__main__":
    scrape()