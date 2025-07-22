"""Advisor CLI for analysis and recommendations."""

import argparse
from typing import List, Optional
from advisor.core.config import init_config
from advisor.analysis.sentiment import SentimentAnalyzer


def analyze_sentiment(stocks: Optional[List[str]] = None) -> None:
    """Analyze sentiment for specified stocks or all stocks."""
    analyzer = SentimentAnalyzer()
    
    if stocks:
        print(f"📊 Analyzing sentiment for: {', '.join(stocks)}")
        for stock in stocks:
            print(f"\n🔍 Analyzing {stock}...")
            analysis = analyzer.analyze_mentions_for_stock(stock.upper())
            recommendation = analyzer.get_recommendation(
                analysis["average_sentiment"],
                analysis["total_mentions"]
            )
            
            print(f"📈 {stock}: {recommendation}")
            print(f"   Sentiment Score: {analysis['average_sentiment']:.3f}")
            print(f"   Total Mentions: {analysis['total_mentions']}")
            print(f"   Analyzed: {analysis['analyzed']}")
    else:
        print("📊 Analyzing all tracked stocks...")
        results = analyzer.analyze_all_stocks()
        
        if not results:
            print("❌ No stocks found in database. Run data collection first.")
            return
        
        print("\n" + "=" * 60)
        print("📈 INVESTMENT RECOMMENDATIONS")
        print("=" * 60)
        
        for stock, data in results.items():
            recommendation = data["recommendation"]
            sentiment = data["average_sentiment"]
            mentions = data["total_mentions"]
            
            # Format recommendation with emoji
            rec_emoji = {
                "BUY": "🟢",
                "SELL": "🔴", 
                "HOLD": "🟡"
            }
            
            print(f"{rec_emoji.get(recommendation, '⚪')} {stock:6} | {recommendation:4} | "
                  f"Sentiment: {sentiment:6.3f} | Mentions: {mentions:3d}")
        
        print("=" * 60)
        print("\n💡 Recommendation Logic:")
        print("   BUY:  Sentiment ≥ 0.7 with ≥5 mentions")
        print("   SELL: Sentiment ≤ 0.3 with ≥5 mentions") 
        print("   HOLD: Otherwise (neutral sentiment or insufficient data)")


def show_stock_details(symbol: str) -> None:
    """Show detailed analysis for a specific stock."""
    analyzer = SentimentAnalyzer()
    
    print(f"🔍 Detailed Analysis for {symbol.upper()}")
    print("=" * 50)
    
    # Get recent mentions
    mentions = analyzer.db.get_mentions_for_stock(symbol.upper(), limit=10)
    
    if not mentions:
        print(f"❌ No mentions found for {symbol.upper()}")
        return
    
    # Overall analysis
    analysis = analyzer.analyze_mentions_for_stock(symbol.upper())
    recommendation = analyzer.get_recommendation(
        analysis["average_sentiment"],
        analysis["total_mentions"]
    )
    
    print(f"📊 Overall Recommendation: {recommendation}")
    print(f"📈 Average Sentiment: {analysis['average_sentiment']:.3f}")
    print(f"💬 Total Mentions: {analysis['total_mentions']}")
    print(f"🔬 Analyzed: {analysis['analyzed']}")
    
    print("\n📝 Recent Mentions:")
    print("-" * 50)
    
    for i, mention in enumerate(mentions[:5], 1):
        content = mention['content'][:100] + "..." if len(mention['content']) > 100 else mention['content']
        sentiment = mention.get('sentiment_score', 'Not analyzed')
        
        print(f"{i}. {content}")
        print(f"   Sentiment: {sentiment}")
        print(f"   URL: {mention.get('url', 'N/A')}")
        print()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Advisor - Investment Recommendation Tool")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (optional)"
    )
    parser.add_argument(
        "--stocks",
        nargs="+",
        help="Specific stocks to analyze (e.g., AAPL TSLA)"
    )
    parser.add_argument(
        "--detail",
        type=str,
        help="Show detailed analysis for a specific stock"
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    if args.config:
        init_config(args.config)
    else:
        init_config()
    
    print("🎯 Advisor - Investment Recommendation Tool")
    print("=" * 50)
    
    if args.detail:
        show_stock_details(args.detail)
    elif args.stocks:
        analyze_sentiment(args.stocks)
    else:
        analyze_sentiment()


if __name__ == "__main__":
    main()