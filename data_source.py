"""Abstract base class for data sources in the Advisor system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from database import Database


class DataSource(ABC):
    """Abstract base class for all data sources (Reddit, SEC, News, etc.)."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize data source with configuration."""
        self.config = config
        self.db = Database()
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the configuration for this data source."""
        pass
    
    @abstractmethod
    def scrape(self) -> Dict[str, int]:
        """Scrape data from the source and store in database.
        
        Returns:
            Dictionary with 'stored' and 'skipped' counts
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this data source (e.g., 'reddit', 'sec', 'news')."""
        pass
    
    def ensure_stocks_exist(self, ticker_symbols: List[str]) -> None:
        """Ensure all ticker symbols exist in the database."""
        for ticker in ticker_symbols:
            self.db.add_stock(ticker)
    
    def is_duplicate(self, external_id: str) -> bool:
        """Check if content already exists in database."""
        return self.db.data_point_exists(self.get_source_name(), external_id)
    
    def store_data_point(self, stock_id: int, content: str, url: str, 
                        external_id: str, metadata: str) -> bool:
        """Store a data point in the database."""
        try:
            self.db.add_data_point(
                stock_id=stock_id,
                source=self.get_source_name(),
                content=content,
                url=url,
                external_id=external_id,
                metadata=metadata
            )
            return True
        except Exception as e:
            print(f"✗ Error storing data point: {e}")
            return False
    
    def get_stock_id(self, symbol: str) -> Optional[int]:
        """Get stock ID by symbol."""
        return self.db.get_stock_id(symbol)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default."""
        return self.config.get(key, default)