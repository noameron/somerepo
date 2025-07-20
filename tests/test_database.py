"""Tests for advisor.core.database module."""
import sqlite3
import pytest
from pathlib import Path

from advisor.core.database import Database


class TestDatabase:
    """Test suite for Database class."""
    
    def test_database_initialization(self, test_db_path):
        """
        Given: Database path provided
        When: Creating Database instance
        Then: Should create database file and tables
        """
        db = Database(str(test_db_path))
        
        assert test_db_path.exists()
        assert db.connection is not None
        assert db.db_path == test_db_path
        
        # Verify tables exist
        cursor = db.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [row[0] for row in cursor.fetchall()]
        assert "stocks" in table_names
        assert "mentions" in table_names

    def test_database_default_path(self, temp_dir, monkeypatch):
        """
        Given: No database path provided
        When: Creating Database instance
        Then: Should use default path
        """
        monkeypatch.chdir(temp_dir)
        db = Database()
        
        # Database uses relative path "advisor.db"
        assert db.db_path.name == "advisor.db"
        assert db.db_path.exists()

    def test_stocks_table_schema(self, test_database):
        """
        Given: Initialized database
        When: Checking stocks table schema
        Then: Should have correct columns and constraints
        """
        cursor = test_database.connection.execute("PRAGMA table_info(stocks)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert "id" in columns
        assert "symbol" in columns
        assert "created_at" in columns
        assert columns["symbol"] == "TEXT"

    def test_mentions_table_schema(self, test_database):
        """
        Given: Initialized database
        When: Checking mentions table schema
        Then: Should have correct columns and foreign key
        """
        cursor = test_database.connection.execute("PRAGMA table_info(mentions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert "id" in columns
        assert "stock_id" in columns
        assert "content" in columns
        assert "url" in columns
        assert "external_id" in columns
        assert "metadata" in columns
        assert "sentiment_score" in columns
        assert "created_at" in columns

    def test_add_stock_new_symbol(self, test_database):
        """
        Given: Empty database
        When: Adding new stock symbol
        Then: Should insert stock and return ID
        """
        stock_id = test_database.add_stock("AAPL")
        
        assert isinstance(stock_id, int)
        assert stock_id > 0
        
        # Verify stock was added
        result = test_database.connection.execute(
            "SELECT symbol FROM stocks WHERE id = ?", (stock_id,)
        ).fetchone()
        assert result["symbol"] == "AAPL"

    def test_add_stock_duplicate_symbol(self, test_database):
        """
        Given: Stock symbol already exists
        When: Adding same stock symbol again
        Then: Should return existing ID without error
        """
        # Add stock first time
        stock_id1 = test_database.add_stock("TSLA")
        
        # Add same stock second time
        stock_id2 = test_database.add_stock("TSLA")
        
        assert stock_id1 == stock_id2
        
        # Verify only one record exists
        count = test_database.connection.execute(
            "SELECT COUNT(*) FROM stocks WHERE symbol = ?", ("TSLA",)
        ).fetchone()[0]
        assert count == 1

    def test_get_stock_id_existing(self, test_database):
        """
        Given: Stock exists in database
        When: Getting stock ID by symbol
        Then: Should return correct ID
        """
        # Add stock first
        expected_id = test_database.add_stock("GOOG")
        
        # Get stock ID
        stock_id = test_database.get_stock_id("GOOG")
        
        assert stock_id == expected_id

    def test_get_stock_id_nonexistent(self, test_database):
        """
        Given: Stock does not exist in database
        When: Getting stock ID by symbol
        Then: Should return None
        """
        stock_id = test_database.get_stock_id("NONEXISTENT")
        assert stock_id is None

    def test_add_mention_basic(self, test_database):
        """
        Given: Stock exists in database
        When: Adding mention with basic parameters
        Then: Should insert mention successfully
        """
        stock_id = test_database.add_stock("AAPL")
        
        success = test_database.add_mention(
            stock_id=stock_id,
            content="AAPL is looking strong!",
            url="https://example.com/post1",
            external_id="post_1"
        )
        
        assert success is True
        
        # Verify mention was added
        result = test_database.connection.execute(
            "SELECT content, url, external_id FROM mentions WHERE stock_id = ?",
            (stock_id,)
        ).fetchone()
        
        assert result["content"] == "AAPL is looking strong!"
        assert result["url"] == "https://example.com/post1"
        assert result["external_id"] == "post_1"

    def test_add_mention_with_metadata(self, test_database):
        """
        Given: Stock exists in database
        When: Adding mention with metadata
        Then: Should store metadata correctly
        """
        stock_id = test_database.add_stock("TSLA")
        
        success = test_database.add_mention(
            stock_id=stock_id,
            content="Tesla earnings look promising",
            external_id="post_2",
            metadata='{"score": 100, "comments": 50}'
        )
        
        assert success is True
        
        # Verify metadata was stored
        result = test_database.connection.execute(
            "SELECT metadata FROM mentions WHERE external_id = ?",
            ("post_2",)
        ).fetchone()
        
        assert result["metadata"] == '{"score": 100, "comments": 50}'

    def test_add_mention_minimal_params(self, test_database):
        """
        Given: Stock exists in database
        When: Adding mention with minimal parameters
        Then: Should insert mention with NULL optional fields
        """
        stock_id = test_database.add_stock("NVDA")
        
        success = test_database.add_mention(
            stock_id=stock_id,
            content="NVDA discussion"
        )
        
        assert success is True
        
        # Verify mention was added with NULL optional fields
        result = test_database.connection.execute(
            "SELECT url, external_id, metadata FROM mentions WHERE stock_id = ?",
            (stock_id,)
        ).fetchone()
        
        assert result["url"] is None
        assert result["external_id"] is None
        assert result["metadata"] is None

    def test_add_mention_duplicate_external_id(self, test_database):
        """
        Given: Mention with external_id already exists
        When: Adding mention with same external_id
        Then: Should return False due to unique constraint
        """
        stock_id = test_database.add_stock("AMD")
        
        # Add first mention
        success1 = test_database.add_mention(
            stock_id=stock_id,
            content="AMD first mention",
            external_id="duplicate_id"
        )
        assert success1 is True
        
        # Add second mention with same external_id
        success2 = test_database.add_mention(
            stock_id=stock_id,
            content="AMD second mention",
            external_id="duplicate_id"
        )
        assert success2 is False

    def test_is_duplicate_exists(self, test_database):
        """
        Given: Mention with external_id exists
        When: Checking if external_id is duplicate
        Then: Should return True
        """
        stock_id = test_database.add_stock("INTC")
        test_database.add_mention(
            stock_id=stock_id,
            content="Intel mention",
            external_id="existing_id"
        )
        
        assert test_database.is_duplicate("existing_id") is True

    def test_is_duplicate_not_exists(self, test_database):
        """
        Given: External_id does not exist
        When: Checking if external_id is duplicate
        Then: Should return False
        """
        assert test_database.is_duplicate("nonexistent_id") is False

    def test_get_mentions_for_stock(self, test_database):
        """
        Given: Stock with multiple mentions
        When: Getting mentions for stock
        Then: Should return all mentions ordered by creation date
        """
        stock_id = test_database.add_stock("MSFT")
        
        # Add multiple mentions
        test_database.add_mention(
            stock_id=stock_id,
            content="First mention",
            url="https://example.com/1",
            external_id="mention_1"
        )
        test_database.add_mention(
            stock_id=stock_id,
            content="Second mention",
            url="https://example.com/2",
            external_id="mention_2"
        )
        
        mentions = test_database.get_mentions_for_stock("MSFT")
        
        assert len(mentions) == 2
        # Check that both mentions are present (order may vary due to same timestamps)
        mention_contents = {mention["content"] for mention in mentions}
        assert mention_contents == {"First mention", "Second mention"}
        assert all("created_at" in mention for mention in mentions)

    def test_get_mentions_for_stock_with_limit(self, test_database):
        """
        Given: Stock with multiple mentions
        When: Getting mentions with limit
        Then: Should return limited number of mentions
        """
        stock_id = test_database.add_stock("AMZN")
        
        # Add three mentions
        for i in range(3):
            test_database.add_mention(
                stock_id=stock_id,
                content=f"Mention {i+1}",
                external_id=f"mention_{i+1}"
            )
        
        mentions = test_database.get_mentions_for_stock("AMZN", limit=2)
        
        assert len(mentions) == 2
        # Check that we get exactly 2 mentions (order may vary due to same timestamps)
        mention_contents = {mention["content"] for mention in mentions}
        expected_contents = {"Mention 1", "Mention 2", "Mention 3"}
        assert mention_contents.issubset(expected_contents)

    def test_get_mentions_for_nonexistent_stock(self, test_database):
        """
        Given: Stock does not exist
        When: Getting mentions for stock
        Then: Should return empty list
        """
        mentions = test_database.get_mentions_for_stock("NONEXISTENT")
        assert mentions == []

    def test_update_sentiment_score_success(self, test_database):
        """
        Given: Mention exists with external_id
        When: Updating sentiment score
        Then: Should update score and return True
        """
        stock_id = test_database.add_stock("CRM")
        test_database.add_mention(
            stock_id=stock_id,
            content="CRM sentiment test",
            external_id="sentiment_test"
        )
        
        success = test_database.update_sentiment_score("sentiment_test", 0.75)
        assert success is True
        
        # Verify sentiment score was updated
        result = test_database.connection.execute(
            "SELECT sentiment_score FROM mentions WHERE external_id = ?",
            ("sentiment_test",)
        ).fetchone()
        
        assert result["sentiment_score"] == 0.75

    def test_update_sentiment_score_nonexistent(self, test_database):
        """
        Given: External_id does not exist
        When: Updating sentiment score
        Then: Should return False
        """
        success = test_database.update_sentiment_score("nonexistent", 0.5)
        assert success is False

    def test_get_all_stocks_empty(self, test_database):
        """
        Given: Empty database
        When: Getting all stocks
        Then: Should return empty list
        """
        stocks = test_database.get_all_stocks()
        assert stocks == []

    def test_get_all_stocks_with_data(self, test_database):
        """
        Given: Database with multiple stocks
        When: Getting all stocks
        Then: Should return all stock symbols
        """
        symbols = ["AAPL", "TSLA", "GOOG", "MSFT"]
        
        for symbol in symbols:
            test_database.add_stock(symbol)
        
        result = test_database.get_all_stocks()
        
        assert len(result) == 4
        assert set(result) == set(symbols)

    def test_close_connection(self, test_database):
        """
        Given: Database with active connection
        When: Closing database
        Then: Should close connection and set to None
        """
        assert test_database.connection is not None
        
        test_database.close()
        
        assert test_database.connection is None

    def test_close_already_closed(self, test_database):
        """
        Given: Database connection already closed
        When: Closing database again
        Then: Should not raise error
        """
        test_database.close()
        test_database.close()  # Should not raise error
        
        assert test_database.connection is None

    def test_operations_after_close_raise_error(self, test_database):
        """
        Given: Database connection is closed
        When: Attempting database operations
        Then: Should raise RuntimeError
        """
        test_database.close()
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.add_stock("TEST")
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.get_stock_id("TEST")
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.add_mention(1, "test content")
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.is_duplicate("test_id")
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.get_mentions_for_stock("TEST")
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.update_sentiment_score("test_id", 0.5)
        
        with pytest.raises(RuntimeError, match="Database connection not initialized"):
            test_database.get_all_stocks()

    def test_row_factory_dict_access(self, test_database):
        """
        Given: Database with row_factory set
        When: Querying data
        Then: Should allow dict-style access to results
        """
        stock_id = test_database.add_stock("TEST")
        
        result = test_database.connection.execute(
            "SELECT id, symbol FROM stocks WHERE id = ?", (stock_id,)
        ).fetchone()
        
        # Should work with both dict-style and index access
        assert result["id"] == stock_id
        assert result["symbol"] == "TEST"
        assert result[0] == stock_id
        assert result[1] == "TEST"

    def test_foreign_key_constraint(self, test_database):
        """
        Given: Database with foreign key constraints
        When: Adding mention with invalid stock_id
        Then: Should accept invalid stock_id (SQLite default behavior)
        """
        # SQLite doesn't enforce foreign keys by default
        success = test_database.add_mention(
            stock_id=99999,  # Non-existent stock_id
            content="Test content"
        )
        assert success is True