"""Reddit scraper using the new RedditDataSource class."""

import json
import os

from .data_source import RedditDataSource

def scrape():
    """Scrape Reddit data using RedditDataSource."""
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Initialize and run Reddit scraper
    reddit_source = RedditDataSource(config)
    result = reddit_source.scrape()
    
    return result

if __name__ == "__main__":
    scrape()