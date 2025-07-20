"""Tests for advisor.analysis.sentiment module."""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from advisor.analysis.sentiment import SentimentAnalyzer
from advisor.core.database import Database


class TestSentimentAnalyzer:
    """Test suite for SentimentAnalyzer class."""

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_initialization_default(self, mock_db_class, mock_get_config):
        """
        Given: No API URL or key provided
        When: Creating SentimentAnalyzer instance
        Then: Should use default API URL and initialize database
        """
        mock_config = Mock()
        mock_config.get_database_path.return_value = "test.db"
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        assert analyzer.api_url == "https://api.openai.com/v1/chat/completions"
        assert analyzer.api_key is None
        mock_db_class.assert_called_once_with("test.db")

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_initialization_custom(self, mock_db_class, mock_get_config):
        """
        Given: Custom API URL and key provided
        When: Creating SentimentAnalyzer instance
        Then: Should use provided values
        """
        mock_config = Mock()
        mock_config.get_database_path.return_value = "test.db"
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer(
            api_url="https://custom-api.com/chat",
            api_key="custom_key"
        )
        
        assert analyzer.api_url == "https://custom-api.com/chat"
        assert analyzer.api_key == "custom_key"

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_text_calls_simple_analysis(self, mock_db_class, mock_get_config):
        """
        Given: Text content and ticker
        When: Analyzing text sentiment
        Then: Should call simple sentiment analysis
        """
        mock_config = Mock()
        mock_config.get_database_path.return_value = "test.db"
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        with patch.object(analyzer, '_simple_sentiment_analysis', return_value=0.5) as mock_simple:
            result = analyzer.analyze_text("AAPL is looking great!", "AAPL")
            
            mock_simple.assert_called_once_with("AAPL is looking great!", "AAPL")
            assert result == 0.5

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_simple_sentiment_analysis_ticker_not_mentioned(self, mock_db_class, mock_get_config):
        """
        Given: Content that doesn't mention the ticker
        When: Performing simple sentiment analysis
        Then: Should return neutral sentiment (0.0)
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        result = analyzer._simple_sentiment_analysis("The market is doing well", "AAPL")
        assert result == 0.0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_simple_sentiment_analysis_positive_words(self, mock_db_class, mock_get_config):
        """
        Given: Content with positive sentiment words about ticker
        When: Performing simple sentiment analysis
        Then: Should return positive sentiment score
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        result = analyzer._simple_sentiment_analysis("AAPL is bullish and going to the moon!", "AAPL")
        assert result > 0.0
        assert result <= 1.0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_simple_sentiment_analysis_negative_words(self, mock_db_class, mock_get_config):
        """
        Given: Content with negative sentiment words about ticker
        When: Performing simple sentiment analysis
        Then: Should return negative sentiment score
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        result = analyzer._simple_sentiment_analysis("TSLA is bearish and will crash", "TSLA")
        assert result < 0.0
        assert result >= -1.0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_simple_sentiment_analysis_mixed_sentiment(self, mock_db_class, mock_get_config):
        """
        Given: Content with both positive and negative words
        When: Performing simple sentiment analysis
        Then: Should return balanced sentiment score
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        result = analyzer._simple_sentiment_analysis("GOOG has good growth but may fall", "GOOG")
        # Should be closer to neutral due to mixed sentiment
        assert -1.0 <= result <= 1.0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_simple_sentiment_analysis_no_sentiment_words(self, mock_db_class, mock_get_config):
        """
        Given: Content mentioning ticker but no sentiment words
        When: Performing simple sentiment analysis
        Then: Should return neutral sentiment
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        result = analyzer._simple_sentiment_analysis("MSFT quarterly report discussion", "MSFT")
        assert result == 0.0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_simple_sentiment_analysis_case_insensitive(self, mock_db_class, mock_get_config):
        """
        Given: Content with mixed case ticker and sentiment words
        When: Performing simple sentiment analysis
        Then: Should handle case insensitively
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        result = analyzer._simple_sentiment_analysis("aapl is BULLISH and GREAT!", "AAPL")
        assert result > 0.0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_mentions_for_stock_no_mentions(self, mock_db_class, mock_get_config):
        """
        Given: Stock with no mentions in database
        When: Analyzing mentions for stock
        Then: Should return zero values
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.get_mentions_for_stock.return_value = []
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_mentions_for_stock("NVDA")
        
        expected = {"average_sentiment": 0.0, "total_mentions": 0, "analyzed": 0}
        assert result == expected

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_mentions_for_stock_with_existing_scores(self, mock_db_class, mock_get_config):
        """
        Given: Mentions with existing sentiment scores
        When: Analyzing mentions for stock
        Then: Should use existing scores without re-analysis
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_mentions = [
            {"content": "AAPL is great", "sentiment_score": 0.8},
            {"content": "AAPL is okay", "sentiment_score": 0.2}
        ]
        mock_db.get_mentions_for_stock.return_value = mock_mentions
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_mentions_for_stock("AAPL")
        
        assert result["average_sentiment"] == 0.5  # (0.8 + 0.2) / 2
        assert result["total_mentions"] == 2
        assert result["analyzed"] == 2

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_mentions_for_stock_new_analysis(self, mock_db_class, mock_get_config):
        """
        Given: Mentions without sentiment scores
        When: Analyzing mentions for stock
        Then: Should analyze and update database
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_mentions = [
            {
                "content": "TSLA is bullish and great!",
                "sentiment_score": None,
                "url": "https://reddit.com/post1",
                "metadata": '{"type": "submission"}'
            }
        ]
        mock_db.get_mentions_for_stock.return_value = mock_mentions
        mock_db.update_sentiment_score.return_value = True
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        
        with patch.object(analyzer, 'analyze_text', return_value=0.7) as mock_analyze:
            result = analyzer.analyze_mentions_for_stock("TSLA")
            
            mock_analyze.assert_called_once_with("TSLA is bullish and great!", "TSLA")
            mock_db.update_sentiment_score.assert_called_once_with("reddit_submission_post1", 0.7)
            
            assert result["average_sentiment"] == 0.7
            assert result["total_mentions"] == 1
            assert result["analyzed"] == 1

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_mentions_external_id_generation(self, mock_db_class, mock_get_config):
        """
        Given: Mention with different metadata and URL formats
        When: Analyzing mentions
        Then: Should generate correct external_id
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_mentions = [
            {
                "content": "Test content",
                "sentiment_score": None,
                "url": "https://reddit.com/r/stocks/comments/abc123/title",
                "metadata": '{"type": "comment"}'
            }
        ]
        mock_db.get_mentions_for_stock.return_value = mock_mentions
        mock_db.update_sentiment_score.return_value = True
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        
        with patch.object(analyzer, 'analyze_text', return_value=0.5):
            analyzer.analyze_mentions_for_stock("TEST")
            
            mock_db.update_sentiment_score.assert_called_once_with("reddit_comment_title", 0.5)

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_mentions_update_fails(self, mock_db_class, mock_get_config):
        """
        Given: Database update fails for sentiment score
        When: Analyzing mentions
        Then: Should not include failed update in results
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_mentions = [
            {
                "content": "Test content",
                "sentiment_score": None,
                "url": "https://reddit.com/post1",
                "metadata": '{"type": "submission"}'
            }
        ]
        mock_db.get_mentions_for_stock.return_value = mock_mentions
        mock_db.update_sentiment_score.return_value = False  # Update fails
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        
        with patch.object(analyzer, 'analyze_text', return_value=0.5):
            result = analyzer.analyze_mentions_for_stock("TEST")
            
            assert result["average_sentiment"] == 0.0  # No analyzed mentions
            assert result["total_mentions"] == 1
            assert result["analyzed"] == 0

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')  
    def test_get_recommendation_insufficient_mentions(self, mock_db_class, mock_get_config):
        """
        Given: Sentiment score but insufficient mention count
        When: Getting recommendation
        Then: Should return HOLD
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        recommendation = analyzer.get_recommendation(0.9, 3)  # High sentiment, low count
        assert recommendation == "HOLD"

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_get_recommendation_buy_signal(self, mock_db_class, mock_get_config):
        """
        Given: High sentiment score and sufficient mentions
        When: Getting recommendation
        Then: Should return BUY
        """
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default: {
            "analysis.sentiment_threshold_buy": 0.7,
            "analysis.sentiment_threshold_sell": 0.3
        }.get(key, default)
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        recommendation = analyzer.get_recommendation(0.8, 10)  # High sentiment, enough mentions
        assert recommendation == "BUY"

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_get_recommendation_sell_signal(self, mock_db_class, mock_get_config):
        """
        Given: Low sentiment score and sufficient mentions
        When: Getting recommendation
        Then: Should return SELL
        """
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default: {
            "analysis.sentiment_threshold_buy": 0.7,
            "analysis.sentiment_threshold_sell": 0.3
        }.get(key, default)
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        recommendation = analyzer.get_recommendation(0.2, 10)  # Low sentiment, enough mentions
        assert recommendation == "SELL"

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_get_recommendation_hold_signal(self, mock_db_class, mock_get_config):
        """
        Given: Moderate sentiment score and sufficient mentions
        When: Getting recommendation
        Then: Should return HOLD
        """
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default: {
            "analysis.sentiment_threshold_buy": 0.7,
            "analysis.sentiment_threshold_sell": 0.3
        }.get(key, default)
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        recommendation = analyzer.get_recommendation(0.5, 10)  # Moderate sentiment
        assert recommendation == "HOLD"

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_get_recommendation_custom_thresholds(self, mock_db_class, mock_get_config):
        """
        Given: Custom sentiment thresholds in config
        When: Getting recommendation
        Then: Should use custom thresholds
        """
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default: {
            "analysis.sentiment_threshold_buy": 0.8,  # Higher threshold
            "analysis.sentiment_threshold_sell": 0.2   # Lower threshold
        }.get(key, default)
        mock_get_config.return_value = mock_config
        
        analyzer = SentimentAnalyzer()
        
        # 0.75 would be BUY with default (0.7) but HOLD with custom (0.8)
        recommendation = analyzer.get_recommendation(0.75, 10)
        assert recommendation == "HOLD"

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_all_stocks_empty_database(self, mock_db_class, mock_get_config):
        """
        Given: Database with no stocks
        When: Analyzing all stocks
        Then: Should return empty results
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.get_all_stocks.return_value = []
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_all_stocks()
        
        assert result == {}

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_all_stocks_with_data(self, mock_db_class, mock_get_config):
        """
        Given: Database with multiple stocks
        When: Analyzing all stocks
        Then: Should return analysis for each stock
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.get_all_stocks.return_value = ["AAPL", "TSLA"]
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        
        # Mock the analyze_mentions_for_stock method
        def mock_analyze_mentions(symbol):
            return {
                "average_sentiment": 0.8 if symbol == "AAPL" else 0.2,
                "total_mentions": 10,
                "analyzed": 8
            }
        
        with patch.object(analyzer, 'analyze_mentions_for_stock', side_effect=mock_analyze_mentions):
            with patch.object(analyzer, 'get_recommendation', side_effect=lambda s, c: "BUY" if s > 0.5 else "SELL"):
                result = analyzer.analyze_all_stocks()
        
        assert "AAPL" in result
        assert "TSLA" in result
        assert result["AAPL"]["recommendation"] == "BUY"
        assert result["TSLA"]["recommendation"] == "SELL"
        assert result["AAPL"]["average_sentiment"] == 0.8
        assert result["TSLA"]["average_sentiment"] == 0.2

    @patch('advisor.analysis.sentiment.get_config')
    @patch('advisor.analysis.sentiment.Database')
    def test_analyze_mentions_malformed_metadata(self, mock_db_class, mock_get_config):
        """
        Given: Mention with malformed JSON metadata
        When: Analyzing mentions
        Then: Should raise JSONDecodeError
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_mentions = [
            {
                "content": "Test content",
                "sentiment_score": None,
                "url": "https://reddit.com/post1",
                "metadata": "invalid json"  # Malformed JSON
            }
        ]
        mock_db.get_mentions_for_stock.return_value = mock_mentions
        mock_db.update_sentiment_score.return_value = True
        mock_db_class.return_value = mock_db
        
        analyzer = SentimentAnalyzer()
        
        with patch.object(analyzer, 'analyze_text', return_value=0.5):
            # Should raise JSONDecodeError due to malformed metadata
            with pytest.raises(json.JSONDecodeError):
                analyzer.analyze_mentions_for_stock("TEST")