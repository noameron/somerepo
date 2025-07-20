"""Tests for advisor.core.data_source module."""
import pytest
from unittest.mock import Mock, patch
from abc import ABC

from advisor.core.data_source import DataSource


class ConcreteDataSource(DataSource):
    """Concrete implementation of DataSource for testing."""
    
    def _validate_config(self) -> None:
        """Test implementation of config validation."""
        required_keys = ["api_key", "source_url"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
    
    def get_source_name(self) -> str:
        """Test implementation of source name."""
        return "test_source"
    
    def scrape(self) -> dict:
        """Test implementation of scrape method."""
        return {"scraped_items": 10, "new_mentions": 5}


class TestDataSource:
    """Test suite for DataSource abstract base class."""

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_initialization_success(self, mock_db_class, mock_get_config):
        """
        Given: Valid configuration provided
        When: Creating DataSource instance
        Then: Should initialize successfully with database
        """
        mock_config = Mock()
        mock_config.get_database_path.return_value = "test.db"
        mock_get_config.return_value = mock_config
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        
        data_source = ConcreteDataSource(config)
        
        assert data_source.config == config
        mock_db_class.assert_called_once_with("test.db")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_initialization_config_validation_failure(self, mock_db_class, mock_get_config):
        """
        Given: Invalid configuration provided
        When: Creating DataSource instance
        Then: Should raise ValueError during validation
        """
        mock_config = Mock()
        mock_config.get_database_path.return_value = "test.db"
        mock_get_config.return_value = mock_config
        
        config = {"api_key": "test_key"}  # Missing source_url
        
        with pytest.raises(ValueError, match="Missing required config key: source_url"):
            ConcreteDataSource(config)

    def test_abstract_methods_cannot_instantiate_base_class(self):
        """
        Given: DataSource base class
        When: Attempting to instantiate directly
        Then: Should raise TypeError due to abstract methods
        """
        config = {"test": "value"}
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class DataSource"):
            DataSource(config)

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_get_config_value_existing_key(self, mock_db_class, mock_get_config):
        """
        Given: DataSource with configuration
        When: Getting existing config value
        Then: Should return the value
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        config = {"api_key": "test_key", "source_url": "https://example.com", "timeout": 30}
        data_source = ConcreteDataSource(config)
        
        assert data_source.get_config_value("api_key") == "test_key"
        assert data_source.get_config_value("timeout") == 30

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_get_config_value_missing_key_no_default(self, mock_db_class, mock_get_config):
        """
        Given: DataSource with configuration
        When: Getting non-existent config value without default
        Then: Should return None
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        assert data_source.get_config_value("nonexistent") is None

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_get_config_value_missing_key_with_default(self, mock_db_class, mock_get_config):
        """
        Given: DataSource with configuration
        When: Getting non-existent config value with default
        Then: Should return default value
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        assert data_source.get_config_value("timeout", 60) == 60
        assert data_source.get_config_value("retries", 3) == 3

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_ensure_stocks_exist_single_ticker(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance
        When: Ensuring single stock exists
        Then: Should add stock to database with uppercase symbol
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        data_source.ensure_stocks_exist(["aapl"])
        
        mock_db.add_stock.assert_called_once_with("AAPL")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_ensure_stocks_exist_multiple_tickers(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance
        When: Ensuring multiple stocks exist
        Then: Should add all stocks to database with uppercase symbols
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        tickers = ["aapl", "tsla", "GOOG", "msft"]
        data_source.ensure_stocks_exist(tickers)
        
        expected_calls = [
            (("AAPL",),),
            (("TSLA",),),
            (("GOOG",),),
            (("MSFT",),)
        ]
        
        assert mock_db.add_stock.call_count == 4
        actual_calls = mock_db.add_stock.call_args_list
        assert len(actual_calls) == len(expected_calls)
        
        for actual, expected in zip(actual_calls, expected_calls):
            assert actual == expected

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_ensure_stocks_exist_empty_list(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance
        When: Ensuring stocks exist with empty list
        Then: Should not make any database calls
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        data_source.ensure_stocks_exist([])
        
        mock_db.add_stock.assert_not_called()

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_get_stock_id_existing_stock(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance and existing stock
        When: Getting stock ID
        Then: Should return stock ID with uppercase symbol
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.get_stock_id.return_value = 123
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        stock_id = data_source.get_stock_id("aapl")
        
        assert stock_id == 123
        mock_db.get_stock_id.assert_called_once_with("AAPL")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_get_stock_id_nonexistent_stock(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance and non-existent stock
        When: Getting stock ID
        Then: Should return None
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.get_stock_id.return_value = None
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        stock_id = data_source.get_stock_id("NONEXISTENT")
        
        assert stock_id is None
        mock_db.get_stock_id.assert_called_once_with("NONEXISTENT")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_store_mention_success(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance
        When: Storing mention successfully
        Then: Should call database add_mention and return True
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.add_mention.return_value = True
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        result = data_source.store_mention(
            stock_id=123,
            content="AAPL is doing great!",
            url="https://example.com/post1",
            external_id="post_1",
            metadata='{"score": 100}'
        )
        
        assert result is True
        mock_db.add_mention.assert_called_once_with(
            123, "AAPL is doing great!", "https://example.com/post1", "post_1", '{"score": 100}'
        )

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_store_mention_failure(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance
        When: Storing mention fails (e.g., duplicate)
        Then: Should return False
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.add_mention.return_value = False
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        result = data_source.store_mention(
            stock_id=123,
            content="Duplicate content"
        )
        
        assert result is False

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_store_mention_minimal_params(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance
        When: Storing mention with minimal parameters
        Then: Should call database with None for optional params
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.add_mention.return_value = True
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        result = data_source.store_mention(
            stock_id=456,
            content="Minimal content"
        )
        
        assert result is True
        mock_db.add_mention.assert_called_once_with(456, "Minimal content", "", "", "")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_is_duplicate_exists(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance and existing external_id
        When: Checking if duplicate
        Then: Should return True
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.is_duplicate.return_value = True
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        result = data_source.is_duplicate("existing_id")
        
        assert result is True
        mock_db.is_duplicate.assert_called_once_with("existing_id")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_is_duplicate_not_exists(self, mock_db_class, mock_get_config):
        """
        Given: DataSource instance and non-existent external_id
        When: Checking if duplicate
        Then: Should return False
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_db = Mock()
        mock_db.is_duplicate.return_value = False
        mock_db_class.return_value = mock_db
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        result = data_source.is_duplicate("new_id")
        
        assert result is False
        mock_db.is_duplicate.assert_called_once_with("new_id")

    @patch('advisor.core.data_source.get_config')
    @patch('advisor.core.data_source.Database')
    def test_concrete_implementation_methods(self, mock_db_class, mock_get_config):
        """
        Given: Concrete DataSource implementation
        When: Calling implemented abstract methods
        Then: Should return expected values
        """
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        config = {"api_key": "test_key", "source_url": "https://example.com"}
        data_source = ConcreteDataSource(config)
        
        assert data_source.get_source_name() == "test_source"
        assert data_source.scrape() == {"scraped_items": 10, "new_mentions": 5}


class InvalidDataSource(DataSource):
    """DataSource implementation missing required abstract methods."""
    
    def _validate_config(self) -> None:
        pass
    
    # Missing get_source_name and scrape methods


class TestAbstractMethods:
    """Test abstract method enforcement."""
    
    def test_missing_abstract_methods_prevents_instantiation(self):
        """
        Given: DataSource subclass missing abstract methods
        When: Attempting to instantiate
        Then: Should raise TypeError
        """
        config = {"test": "value"}
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class InvalidDataSource"):
            InvalidDataSource(config)