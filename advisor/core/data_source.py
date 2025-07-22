"""Base data source class for all scrapers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .database import Database
from .config import get_config


class DataSource(ABC):
    """Abstract base class for all data sources."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize data source with configuration."""
        self.config = config
        self.db = Database(get_config().get_database_path())
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate data source specific configuration."""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this data source."""
        pass
    
    @abstractmethod
    def scrape(self) -> Dict[str, int]:
        """Scrape data from the source."""
        pass
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with optional default."""
        return self.config.get(key, default)
    
    def ensure_stocks_exist(self, tickers: List[str]) -> None:
        """Ensure all ticker symbols exist in the database."""
        for ticker in tickers:
            self.db.add_stock(ticker.upper())
    
    def get_stock_id(self, symbol: str) -> Optional[int]:
        """Get stock ID for a symbol."""
        return self.db.get_stock_id(symbol.upper())
    
    def store_mention(self, stock_id: int, content: str, url: str = "",
                     external_id: str = "", metadata: str = "") -> bool:
        """Store a mention in the database."""
        return self.db.add_mention(stock_id, content, url, external_id, metadata)
    
    def is_duplicate(self, external_id: str) -> bool:
        """Check if external_id already exists in database."""
        return self.db.is_duplicate(external_id)