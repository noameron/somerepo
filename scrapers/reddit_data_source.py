"""Reddit data source implementation."""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import sys

import praw
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))
from data_source import DataSource


class RedditDataSource(DataSource):
    """Reddit data source for scraping stock-related content."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Reddit data source."""
        # Load environment variables from project root first
        project_root = Path(__file__).parent.parent
        load_dotenv(project_root / ".env")
        
        super().__init__(config)
        
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
        )
        
        # Create ticker pattern for matching
        tickers = [t.upper() for t in self.get_config_value("tickers", [])]
        self.ticker_pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in tickers) + r")\b")
        
        # Ensure tickers exist in database
        self.ensure_stocks_exist(tickers)
    
    def _validate_config(self) -> None:
        """Validate Reddit configuration."""
        required_fields = ["subreddits", "tickers", "max_days"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required config field: {field}")
        
        # Validate environment variables
        required_env = ["CLIENT_ID", "CLIENT_SECRET", "USER_AGENT"]
        for env_var in required_env:
            if not os.getenv(env_var):
                raise RuntimeError(f"Missing Reddit API credential: {env_var}")
    
    def get_source_name(self) -> str:
        """Get the name of this data source."""
        return "reddit"
    
    def age_in_days(self, utc_timestamp: float) -> float:
        """Calculate age of content in days."""
        created = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - created).total_seconds() / 86400.0
    
    def extract_tickers_from_text(self, text: str) -> List[str]:
        """Extract ticker symbols from text content."""
        matches = self.ticker_pattern.findall(text.upper())
        return list(set(matches))  # Remove duplicates
    
    def is_within_time_range(self, age_days: float) -> bool:
        """Check if content age is within configured time range."""
        min_days = self.get_config_value("min_days", 0)
        max_days = self.get_config_value("max_days", 7)
        return min_days <= age_days <= max_days
    
    def get_submission_text(self, submission) -> str:
        """Extract combined text from Reddit submission."""
        title = submission.title or ""
        selftext = getattr(submission, "selftext", "") or ""
        return (title + "\n" + selftext).strip()
    
    def create_external_id(self, content_type: str, content_id: str) -> str:
        """Create external ID for database deduplication."""
        return f"reddit_{content_type}_{content_id}"
    
    def create_metadata(self, content_type: str, subreddit: str, author: str, 
                       age_days: float, tickers: List[str]) -> str:
        """Create metadata JSON for database storage."""
        return json.dumps({
            "type": content_type,
            "subreddit": subreddit,
            "author": author,
            "age_days": age_days,
            "tickers": tickers
        })
    
    def process_content_for_tickers(self, content: str, url: str, 
                                   external_id: str, metadata: str) -> int:
        """Process content and store data points for each ticker found."""
        found_tickers = self.extract_tickers_from_text(content)
        stored_count = 0
        
        if not found_tickers:
            return 0
        
        # Check if already exists (once per content, not per ticker)
        if self.is_duplicate(external_id):
            return 0
        
        # Store data point for each ticker mentioned
        for ticker in found_tickers:
            stock_id = self.get_stock_id(ticker)
            if stock_id and self.store_data_point(stock_id, content, url, external_id, metadata):
                stored_count += 1
                print(f"✓ Stored content {external_id.split('_')[-1]} for {ticker}")
        
        return stored_count
    
    def process_submissions(self, subreddit_name: str, subreddit) -> tuple[int, int]:
        """Process all submissions from a subreddit."""
        stored = 0
        skipped = 0
        max_days = self.get_config_value("max_days", 7)
        
        for submission in subreddit.new(limit=None):
            age = self.age_in_days(submission.created_utc)
            
            if age > max_days:
                break
            
            if not self.is_within_time_range(age):
                continue
            
            content = self.get_submission_text(submission)
            if not content:
                continue
            
            external_id = self.create_external_id("submission", submission.id)
            metadata = self.create_metadata("submission", subreddit_name, 
                                          str(submission.author), age, 
                                          self.extract_tickers_from_text(content))
            
            result = self.process_content_for_tickers(content, submission.url, 
                                                    external_id, metadata)
            if result > 0:
                stored += result
            else:
                skipped += 1
        
        return stored, skipped
    
    def process_comments(self, subreddit_name: str, subreddit) -> tuple[int, int]:
        """Process all comments from a subreddit."""
        stored = 0
        skipped = 0
        max_days = self.get_config_value("max_days", 7)
        
        for comment in subreddit.comments(limit=None):
            age = self.age_in_days(comment.created_utc)
            
            if age > max_days:
                break
            
            if not self.is_within_time_range(age):
                continue
            
            content = comment.body or ""
            if not content:
                continue
            
            external_id = self.create_external_id("comment", comment.id)
            url = f"https://reddit.com{comment.permalink}"
            metadata = self.create_metadata("comment", subreddit_name, 
                                          str(comment.author), age, 
                                          self.extract_tickers_from_text(content))
            
            result = self.process_content_for_tickers(content, url, 
                                                    external_id, metadata)
            if result > 0:
                stored += result
            else:
                skipped += 1
        
        return stored, skipped
    
    def scrape(self) -> Dict[str, int]:
        """Scrape Reddit data and store in database."""
        total_stored = 0
        total_skipped = 0
        
        subreddits = self.get_config_value("subreddits", [])
        
        for subreddit_name in subreddits:
            print(f"Scanning r/{subreddit_name}...")
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Process submissions and comments
            sub_stored, sub_skipped = self.process_submissions(subreddit_name, subreddit)
            comm_stored, comm_skipped = self.process_comments(subreddit_name, subreddit)
            
            total_stored += sub_stored + comm_stored
            total_skipped += sub_skipped + comm_skipped
            
            time.sleep(2)  # Rate limiting
        
        print(f"\nScraping complete! Stored: {total_stored}, Skipped: {total_skipped}")
        return {"stored": total_stored, "skipped": total_skipped}