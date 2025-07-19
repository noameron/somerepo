"""Database operations for the advisor system."""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any


class Database:
    """SQLite database manager for advisor system."""
    
    def __init__(self, db_path: str = "advisor.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create database and tables if they don't exist."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        # Create stocks table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create mentions table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                url TEXT,
                external_id TEXT UNIQUE,
                metadata TEXT,
                sentiment_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_id) REFERENCES stocks (id)
            )
        """)
        
        self.connection.commit()
    
    def add_stock(self, symbol: str) -> int:
        """Add a stock symbol to the database."""
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO stocks (symbol) VALUES (?)",
            (symbol,)
        )
        self.connection.commit()
        
        # Get the stock ID
        result = self.connection.execute(
            "SELECT id FROM stocks WHERE symbol = ?",
            (symbol,)
        ).fetchone()
        
        return result['id']
    
    def get_stock_id(self, symbol: str) -> Optional[int]:
        """Get stock ID by symbol."""
        result = self.connection.execute(
            "SELECT id FROM stocks WHERE symbol = ?",
            (symbol,)
        ).fetchone()
        
        return result['id'] if result else None
    
    def add_mention(self, stock_id: int, content: str, url: str = None, 
                   external_id: str = None, metadata: str = None) -> bool:
        """Add a mention to the database."""
        try:
            self.connection.execute("""
                INSERT INTO mentions (stock_id, content, url, external_id, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (stock_id, content, url, external_id, metadata))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def is_duplicate(self, external_id: str) -> bool:
        """Check if a mention with this external_id already exists."""
        result = self.connection.execute(
            "SELECT 1 FROM mentions WHERE external_id = ?",
            (external_id,)
        ).fetchone()
        
        return result is not None
    
    def get_mentions_for_stock(self, symbol: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get all mentions for a specific stock."""
        query = """
            SELECT m.content, m.url, m.metadata, m.sentiment_score, m.created_at
            FROM mentions m
            JOIN stocks s ON m.stock_id = s.id
            WHERE s.symbol = ?
            ORDER BY m.created_at DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        results = self.connection.execute(query, (symbol,)).fetchall()
        return [dict(row) for row in results]
    
    def update_sentiment_score(self, external_id: str, sentiment_score: float) -> bool:
        """Update sentiment score for a mention."""
        cursor = self.connection.execute(
            "UPDATE mentions SET sentiment_score = ? WHERE external_id = ?",
            (sentiment_score, external_id)
        )
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_all_stocks(self) -> List[str]:
        """Get all stock symbols in the database."""
        results = self.connection.execute("SELECT symbol FROM stocks").fetchall()
        return [row['symbol'] for row in results]
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None