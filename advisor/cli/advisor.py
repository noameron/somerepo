"""Advisor CLI - Analysis and recommendation engine."""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from advisor.core.database import Database


def show_data_summary():
    """Show summary of collected data."""
    db = Database()
    
    stocks = db.get_stocks()
    mentions = db.get_mentions()
    
    print(f"\n=== Data Summary ===")
    print(f"Tracked stocks: {len(stocks)}")
    print(f"Total mentions: {len(mentions)}")
    
    if stocks:
        print(f"\nStocks:")
        for stock in stocks:
            count = len(db.get_mentions(stock_id=stock['id']))
            print(f"  {stock['symbol']}: {count} mentions")
    
    if mentions:
        print(f"\nRecent mentions:")
        for mention in mentions[:5]:  # Show first 5
            print(f"  [{mention['source']}] {mention['content'][:50]}...")


def main():
    """Main CLI entry point for the advisor."""
    parser = argparse.ArgumentParser(description="Advisor - Investment Recommendation Tool")
    parser.add_argument(
        "command",
        choices=["analyze", "summary"],
        help="Command to execute"
    )
    parser.add_argument(
        "--symbol", "-s",
        help="Stock symbol to analyze (optional)"
    )
    
    args = parser.parse_args()
    
    if args.command == "summary":
        show_data_summary()
    
    elif args.command == "analyze":
        print("Analysis engine not yet implemented.")
        print("TODO: Implement LLM sentiment analysis and scoring")
        if args.symbol:
            print(f"Would analyze: {args.symbol}")
        else:
            print("Would analyze all tracked stocks")


if __name__ == "__main__":
    main()