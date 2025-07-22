"""Assistant CLI for data collection."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from advisor.core.config import init_config
from advisor.scrapers.reddit.data_source import RedditDataSource


def collect_reddit_data(config_path: Optional[str] = None) -> None:
    """Collect data from Reddit sources."""
    # Initialize configuration
    if config_path:
        config = init_config(config_path)
    else:
        config = init_config()
    
    # Load Reddit-specific configuration
    reddit_config_path = Path(__file__).parent.parent / "scrapers" / "reddit" / "config.json"
    
    if not reddit_config_path.exists():
        print(f"❌ Reddit config not found at: {reddit_config_path}")
        sys.exit(1)
    
    with open(reddit_config_path, 'r') as f:
        reddit_config = json.load(f)
    
    print("🚀 Starting Reddit data collection...")
    print(f"📊 Tracking stocks: {reddit_config.get('tickers', [])}")
    print(f"🗣️  Monitoring subreddits: {reddit_config.get('subreddits', [])}")
    
    try:
        # Initialize Reddit scraper
        reddit_source = RedditDataSource(reddit_config)
        
        # Validate Reddit credentials
        if not config.validate_reddit_credentials():
            print("❌ Missing Reddit API credentials in .env file")
            print("Required: CLIENT_ID, CLIENT_SECRET, USER_AGENT")
            sys.exit(1)
        
        # Run scraping
        results = reddit_source.scrape()
        
        print("\n✅ Reddit scraping completed!")
        print(f"📈 Stored mentions: {results['stored']}")
        print(f"⏭️  Skipped duplicates: {results['skipped']}")
        
    except Exception as e:
        print(f"❌ Error during Reddit scraping: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Advisor Assistant - Data Collection Tool")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file (optional)"
    )
    parser.add_argument(
        "--source",
        choices=["reddit", "all"],
        default="reddit",
        help="Data source to collect from (default: reddit)"
    )
    
    args = parser.parse_args()
    
    print("📊 Advisor Assistant - Data Collection")
    print("=" * 40)
    
    if args.source in ["reddit", "all"]:
        collect_reddit_data(args.config)
    
    if args.source == "all":
        print("\n🔄 Future: Will add SEC and News collection here")
    
    print("\n🎉 Data collection complete!")


if __name__ == "__main__":
    main()