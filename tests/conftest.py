"""Pytest configuration and shared fixtures."""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from advisor.core.database import Database
from advisor.core.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_db_path(temp_dir):
    """Provide a temporary database path."""
    return temp_dir / "test.db"


@pytest.fixture
def test_database(test_db_path):
    """Create a test database instance."""
    db = Database(str(test_db_path))
    yield db


@pytest.fixture
def test_config_file(temp_dir):
    """Create a test configuration file."""
    config_content = """
{
    "database": {
        "path": "test.db"
    },
    "reddit": {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "user_agent": "test_user_agent",
        "subreddits": ["stocks", "investing"],
        "days_back": 7
    },
    "analysis": {
        "sentiment": {
            "positive_threshold": 0.1,
            "negative_threshold": -0.1
        }
    }
}
"""
    config_file = temp_dir / "test_config.json"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def test_config(test_config_file):
    """Create a test configuration instance."""
    return Config(str(test_config_file))


@pytest.fixture
def sample_reddit_submissions():
    """Sample Reddit submission data for testing."""
    return [
        {
            "id": "test1",
            "title": "AAPL is going to the moon! 🚀",
            "selftext": "Apple stock looks amazing, buying more shares",
            "created_utc": 1640995200,  # 2022-01-01
            "score": 100,
            "num_comments": 50,
            "url": "https://reddit.com/r/stocks/test1"
        },
        {
            "id": "test2", 
            "title": "TSLA bearish outlook",
            "selftext": "Tesla might drop due to competition concerns",
            "created_utc": 1640995200,
            "score": 75,
            "num_comments": 30,
            "url": "https://reddit.com/r/stocks/test2"
        }
    ]


@pytest.fixture
def sample_reddit_comments():
    """Sample Reddit comment data for testing."""
    return [
        {
            "id": "comment1",
            "body": "MSFT is looking strong this quarter",
            "created_utc": 1640995200,
            "score": 25,
            "submission": {"id": "test1", "title": "Tech stocks discussion"}
        },
        {
            "id": "comment2",
            "body": "NVDA might be overvalued right now",
            "created_utc": 1640995200,
            "score": 15,
            "submission": {"id": "test2", "title": "GPU stocks analysis"}
        }
    ]


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "REDDIT_CLIENT_ID": "env_client_id",
        "REDDIT_CLIENT_SECRET": "env_client_secret",
        "REDDIT_USER_AGENT": "env_user_agent"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars