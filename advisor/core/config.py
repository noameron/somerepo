"""Configuration management for the advisor system."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class Config:
    """Global configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        # Load environment variables
        load_dotenv()
        
        # Default config
        self._config = {
            "database": {
                "path": "advisor.db"
            },
            "reddit": {
                "max_days": 3,
                "min_days": 1,
                "subreddits": ["WallStreetBets"],
                "tickers": ["AAPL", "TSLA", "GOOG"]
            },
            "analysis": {
                "sentiment_threshold_buy": 0.7,
                "sentiment_threshold_sell": 0.3
            }
        }
        
        # Load additional config from file if provided
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing."""
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self._config:
                self._config[key].update(value)
            else:
                self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_reddit_config(self) -> Dict[str, Any]:
        """Get Reddit-specific configuration."""
        return self._config.get("reddit", {})
    
    def get_database_path(self) -> str:
        """Get database file path."""
        return self.get("database.path", "advisor.db")
    
    def get_stock_symbols(self) -> List[str]:
        """Get list of stock symbols to track."""
        return self.get("reddit.tickers", [])
    
    def get_reddit_credentials(self) -> Dict[str, str]:
        """Get Reddit API credentials from environment."""
        return {
            "client_id": os.getenv("CLIENT_ID") or "",
            "client_secret": os.getenv("CLIENT_SECRET") or "",
            "user_agent": os.getenv("USER_AGENT") or ""
        }
    
    def validate_reddit_credentials(self) -> bool:
        """Validate that all required Reddit credentials are present."""
        creds = self.get_reddit_credentials()
        return all(creds.values())


# Global configuration instance
_config_instance = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def init_config(config_path: Optional[str] = None) -> Config:
    """Initialize global configuration with optional config file."""
    global _config_instance
    _config_instance = Config(config_path)
    return _config_instance