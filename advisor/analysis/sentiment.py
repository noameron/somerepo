"""Sentiment analysis using LLM integration."""

import json
from typing import Dict, Optional, Any
from advisor.core.database import Database
from advisor.core.config import get_config


class SentimentAnalyzer:
    """LLM-based sentiment analyzer for stock mentions."""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize sentiment analyzer."""
        self.api_url = api_url or "https://api.openai.com/v1/chat/completions"
        self.api_key = api_key
        self.db = Database(get_config().get_database_path())
    
    def analyze_text(self, content: str, ticker: str) -> float:
        """Analyze sentiment of text content for a specific ticker.
        
        Returns:
            float: Sentiment score between -1.0 (very negative) and 1.0 (very positive)
        """
        # For now, implement a simple keyword-based fallback
        # This can be replaced with actual LLM API calls when available
        return self._simple_sentiment_analysis(content, ticker)
    
    def _simple_sentiment_analysis(self, content: str, ticker: str) -> float:
        """Simple keyword-based sentiment analysis as fallback."""
        content_lower = content.lower()
        ticker_lower = ticker.lower()
        
        # Only analyze if ticker is mentioned
        if ticker_lower not in content_lower:
            return 0.0
        
        positive_words = [
            'buy', 'bullish', 'moon', 'rocket', 'gains', 'up', 'rise', 'good', 
            'great', 'excellent', 'strong', 'beat', 'winning', 'profit', 'growth',
            'increase', 'bull', 'positive', 'optimistic', 'upgrade'
        ]
        
        negative_words = [
            'sell', 'bearish', 'crash', 'dump', 'loss', 'down', 'fall', 'bad',
            'terrible', 'weak', 'miss', 'losing', 'decline', 'decrease', 'bear',
            'negative', 'pessimistic', 'downgrade', 'short'
        ]
        
        positive_score = sum(1 for word in positive_words if word in content_lower)
        negative_score = sum(1 for word in negative_words if word in content_lower)
        
        total_sentiment_words = positive_score + negative_score
        
        if total_sentiment_words == 0:
            return 0.0
        
        # Normalize to -1 to 1 range
        sentiment = (positive_score - negative_score) / max(total_sentiment_words, 1)
        return max(-1.0, min(1.0, sentiment))
    
    def analyze_mentions_for_stock(self, symbol: str, limit: Optional[int] = None) -> Dict[str, float]:
        """Analyze sentiment for all mentions of a stock."""
        mentions = self.db.get_mentions_for_stock(symbol, limit)
        
        if not mentions:
            return {"average_sentiment": 0.0, "total_mentions": 0, "analyzed": 0}
        
        total_sentiment = 0.0
        analyzed_count = 0
        
        for mention in mentions:
            # Skip if already analyzed
            if mention.get('sentiment_score') is not None:
                total_sentiment += mention['sentiment_score']
                analyzed_count += 1
                continue
            
            # Analyze sentiment
            sentiment = self.analyze_text(mention['content'], symbol)
            
            # Update database with sentiment score
            metadata = json.loads(mention.get('metadata', '{}'))
            external_id = f"reddit_{metadata.get('type', 'unknown')}_{mention.get('url', '').split('/')[-1]}"
            
            if self.db.update_sentiment_score(external_id, sentiment):
                total_sentiment += sentiment
                analyzed_count += 1
        
        average_sentiment = total_sentiment / analyzed_count if analyzed_count > 0 else 0.0
        
        return {
            "average_sentiment": average_sentiment,
            "total_mentions": len(mentions),
            "analyzed": analyzed_count
        }
    
    def get_recommendation(self, sentiment_score: float, mention_count: float) -> str:
        """Get BUY/SELL/HOLD recommendation based on sentiment."""
        config = get_config()
        buy_threshold = config.get("analysis.sentiment_threshold_buy", 0.7)
        sell_threshold = config.get("analysis.sentiment_threshold_sell", 0.3)
        min_mentions = 5  # Minimum mentions needed for confident recommendation
        
        if mention_count < min_mentions:
            return "HOLD"  # Not enough data
        
        if sentiment_score >= buy_threshold:
            return "BUY"
        elif sentiment_score <= sell_threshold:
            return "SELL"
        else:
            return "HOLD"
    
    def analyze_all_stocks(self) -> Dict[str, Dict[str, Any]]:
        """Analyze sentiment for all stocks in database."""
        stocks = self.db.get_all_stocks()
        results = {}
        
        for stock in stocks:
            analysis = self.analyze_mentions_for_stock(stock)
            recommendation = self.get_recommendation(
                analysis["average_sentiment"], 
                analysis["total_mentions"]
            )
            
            results[stock] = {
                **analysis,
                "recommendation": recommendation
            }
        
        return results