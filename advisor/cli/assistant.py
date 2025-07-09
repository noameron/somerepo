"""Assistant CLI - Data collection orchestrator."""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from advisor.scrapers.reddit import scrape as reddit_scrape


def main():
    """Main CLI entry point for the assistant."""
    parser = argparse.ArgumentParser(description="Advisor Assistant - Data Collection Tool")
    parser.add_argument(
        "source", 
        choices=["reddit", "all"], 
        help="Data source to scrape"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Starting data collection for: {args.source}")
    
    if args.source == "reddit":
        result = reddit_scrape()
        if args.verbose:
            print(f"Reddit scraping completed: {result}")
    
    elif args.source == "all":
        if args.verbose:
            print("Scraping all sources...")
        
        # Reddit
        reddit_result = reddit_scrape()
        if args.verbose:
            print(f"Reddit: {reddit_result}")
        
        # TODO: Add SEC and News scrapers when implemented
        print("Note: SEC and News scrapers not yet implemented")


if __name__ == "__main__":
    main()