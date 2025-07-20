"""Tests for advisor.core.config module."""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from advisor.core.config import Config, get_config, init_config


class TestConfig:
    """Test suite for Config class."""
    
    def test_default_config_initialization(self):
        """
        Given: No config file provided
        When: Creating a Config instance
        Then: Should have default configuration values
        """
        config = Config()
        
        assert config.get("database.path") == "advisor.db"
        assert config.get("reddit.max_days") == 3
        assert config.get("reddit.min_days") == 1
        assert config.get("reddit.subreddits") == ["WallStreetBets"]
        assert config.get("reddit.tickers") == ["AAPL", "TSLA", "GOOG"]
        assert config.get("analysis.sentiment_threshold_buy") == 0.7
        assert config.get("analysis.sentiment_threshold_sell") == 0.3

    def test_config_file_loading(self, test_config_file):
        """
        Given: A valid config file exists
        When: Creating Config with config file path
        Then: Should merge file config with defaults
        """
        config = Config(str(test_config_file))
        
        assert config.get("database.path") == "test.db"
        assert config.get("reddit.client_id") == "test_client_id"
        assert config.get("reddit.subreddits") == ["stocks", "investing"]
        assert config.get("reddit.days_back") == 7
        
        # Default values should still be present if not overridden
        assert config.get("reddit.max_days") == 3
        assert config.get("analysis.sentiment_threshold_buy") == 0.7

    def test_config_file_nonexistent(self):
        """
        Given: Config file path that doesn't exist
        When: Creating Config instance
        Then: Should use only default configuration
        """
        config = Config("/nonexistent/path/config.json")
        
        assert config.get("database.path") == "advisor.db"
        assert config.get("reddit.tickers") == ["AAPL", "TSLA", "GOOG"]

    def test_dot_notation_get(self):
        """
        Given: Config with nested values
        When: Using dot notation to access values
        Then: Should return correct nested values
        """
        config = Config()
        
        assert config.get("database.path") == "advisor.db"
        assert config.get("reddit.max_days") == 3
        assert config.get("analysis.sentiment_threshold_buy") == 0.7

    def test_dot_notation_get_nonexistent_key(self):
        """
        Given: Config instance
        When: Accessing non-existent key with dot notation
        Then: Should return default value
        """
        config = Config()
        
        assert config.get("nonexistent.key") is None
        assert config.get("nonexistent.key", "default") == "default"
        assert config.get("reddit.nonexistent", 42) == 42

    def test_dot_notation_get_partial_path(self):
        """
        Given: Config with nested structure
        When: Accessing partial path that doesn't lead to value
        Then: Should return default value
        """
        config = Config()
        
        assert config.get("reddit.nested.nonexistent") is None
        assert config.get("reddit.nested.nonexistent", "fallback") == "fallback"

    def test_merge_config_nested_dict(self, temp_dir):
        """
        Given: Config file with nested dictionary updates
        When: Merging configurations
        Then: Should merge nested dictionaries correctly
        """
        # Create config file with partial reddit config
        partial_config = {
            "reddit": {
                "client_id": "new_client_id",
                "new_field": "new_value"
            },
            "new_section": {
                "field": "value"
            }
        }
        
        config_file = temp_dir / "partial_config.json"
        config_file.write_text(json.dumps(partial_config))
        
        config = Config(str(config_file))
        
        # Should merge reddit section, keeping existing fields
        assert config.get("reddit.client_id") == "new_client_id"
        assert config.get("reddit.new_field") == "new_value"
        assert config.get("reddit.max_days") == 3  # Original default preserved
        assert config.get("reddit.tickers") == ["AAPL", "TSLA", "GOOG"]  # Original default preserved
        
        # Should add new section
        assert config.get("new_section.field") == "value"

    def test_merge_config_replace_non_dict(self, temp_dir):
        """
        Given: Config file that replaces non-dict values
        When: Merging configurations
        Then: Should replace entire non-dict values
        """
        replacement_config = {
            "reddit": {
                "tickers": ["NVDA", "AMD"]  # Replace entire list
            }
        }
        
        config_file = temp_dir / "replacement_config.json"
        config_file.write_text(json.dumps(replacement_config))
        
        config = Config(str(config_file))
        
        assert config.get("reddit.tickers") == ["NVDA", "AMD"]
        assert config.get("reddit.max_days") == 3  # Other values preserved

    def test_get_reddit_config(self):
        """
        Given: Config instance
        When: Getting Reddit-specific configuration
        Then: Should return reddit section as dict
        """
        config = Config()
        reddit_config = config.get_reddit_config()
        
        assert isinstance(reddit_config, dict)
        assert reddit_config["max_days"] == 3
        assert reddit_config["min_days"] == 1
        assert reddit_config["subreddits"] == ["WallStreetBets"]
        assert reddit_config["tickers"] == ["AAPL", "TSLA", "GOOG"]

    def test_get_database_path(self):
        """
        Given: Config instance
        When: Getting database path
        Then: Should return configured database path
        """
        config = Config()
        assert config.get_database_path() == "advisor.db"

    def test_get_database_path_custom(self, test_config_file):
        """
        Given: Config with custom database path
        When: Getting database path
        Then: Should return custom database path
        """
        config = Config(str(test_config_file))
        assert config.get_database_path() == "test.db"

    def test_get_stock_symbols(self):
        """
        Given: Config instance
        When: Getting stock symbols to track
        Then: Should return list of ticker symbols
        """
        config = Config()
        symbols = config.get_stock_symbols()
        
        assert isinstance(symbols, list)
        assert symbols == ["AAPL", "TSLA", "GOOG"]

    def test_get_stock_symbols_empty_when_missing(self, temp_dir):
        """
        Given: Config with explicit empty tickers list
        When: Getting stock symbols
        Then: Should return empty list
        """
        empty_config = {
            "database": {"path": "test.db"},
            "reddit": {"tickers": []}  # Explicitly empty tickers
        }
        config_file = temp_dir / "empty_config.json"
        config_file.write_text(json.dumps(empty_config))
        
        config = Config(str(config_file))
        symbols = config.get_stock_symbols()
        
        assert symbols == []

    @patch.dict(os.environ, {
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret", 
        "USER_AGENT": "test_user_agent"
    })
    def test_get_reddit_credentials_from_env(self):
        """
        Given: Environment variables set for Reddit credentials
        When: Getting Reddit credentials
        Then: Should return credentials from environment
        """
        config = Config()
        creds = config.get_reddit_credentials()
        
        assert creds["client_id"] == "test_client_id"
        assert creds["client_secret"] == "test_client_secret"
        assert creds["user_agent"] == "test_user_agent"

    @patch('advisor.core.config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_reddit_credentials_missing_env(self, mock_load_dotenv):
        """
        Given: No environment variables set
        When: Getting Reddit credentials
        Then: Should return None values
        """
        config = Config()
        creds = config.get_reddit_credentials()
        
        assert creds["client_id"] is None
        assert creds["client_secret"] is None
        assert creds["user_agent"] is None

    @patch.dict(os.environ, {
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "test_client_secret",
        "USER_AGENT": "test_user_agent"
    })
    def test_validate_reddit_credentials_valid(self):
        """
        Given: All required environment variables set
        When: Validating Reddit credentials
        Then: Should return True
        """
        config = Config()
        assert config.validate_reddit_credentials() is True

    @patch.dict(os.environ, {
        "CLIENT_ID": "test_client_id",
        "CLIENT_SECRET": "",  # Empty string
        "USER_AGENT": "test_user_agent"
    })
    def test_validate_reddit_credentials_empty_value(self):
        """
        Given: One environment variable is empty
        When: Validating Reddit credentials
        Then: Should return False
        """
        config = Config()
        assert config.validate_reddit_credentials() is False

    @patch('advisor.core.config.load_dotenv')
    @patch.dict(os.environ, {
        "CLIENT_ID": "test_client_id"
        # Missing CLIENT_SECRET and USER_AGENT
    }, clear=True)
    def test_validate_reddit_credentials_missing_vars(self, mock_load_dotenv):
        """
        Given: Some environment variables missing
        When: Validating Reddit credentials
        Then: Should return False
        """
        config = Config()
        assert config.validate_reddit_credentials() is False

    @patch('advisor.core.config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_reddit_credentials_no_env_vars(self, mock_load_dotenv):
        """
        Given: No environment variables set
        When: Validating Reddit credentials
        Then: Should return False
        """
        config = Config()
        assert config.validate_reddit_credentials() is False


class TestGlobalConfigFunctions:
    """Test suite for global config functions."""
    
    def test_get_config_creates_instance(self):
        """
        Given: No global config instance exists
        When: Calling get_config()
        Then: Should create and return config instance
        """
        # Reset global instance
        import advisor.core.config
        advisor.core.config._config_instance = None
        
        config = get_config()
        assert isinstance(config, Config)
        assert config.get("database.path") == "advisor.db"

    def test_get_config_returns_same_instance(self):
        """
        Given: Global config instance exists
        When: Calling get_config() multiple times
        Then: Should return same instance
        """
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_init_config_with_file(self, test_config_file):
        """
        Given: Config file path provided
        When: Calling init_config() with file path
        Then: Should initialize global config with file
        """
        config = init_config(str(test_config_file))
        
        assert isinstance(config, Config)
        assert config.get("database.path") == "test.db"
        assert config.get("reddit.client_id") == "test_client_id"
        
        # Subsequent calls to get_config should return same instance
        same_config = get_config()
        assert same_config is config

    def test_init_config_without_file(self):
        """
        Given: No config file path provided
        When: Calling init_config()
        Then: Should initialize global config with defaults
        """
        config = init_config()
        
        assert isinstance(config, Config)
        assert config.get("database.path") == "advisor.db"
        assert config.get("reddit.tickers") == ["AAPL", "TSLA", "GOOG"]

    def test_init_config_replaces_existing_instance(self, test_config_file):
        """
        Given: Global config instance already exists
        When: Calling init_config() with different config
        Then: Should replace existing instance
        """
        # Create initial instance
        config1 = init_config()
        assert config1.get("database.path") == "advisor.db"
        
        # Replace with file-based config
        config2 = init_config(str(test_config_file))
        assert config2.get("database.path") == "test.db"
        
        # get_config should return new instance
        config3 = get_config()
        assert config3 is config2
        assert config3 is not config1