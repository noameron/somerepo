import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "advisor/data/sentinel.db"):
        """Initialize database connection and create tables if they don't exist."""
        # Resolve database path relative to project root  
        project_root = Path(__file__).parent.parent.parent  # Go up from advisor/core/ to project root
        if not Path(db_path).is_absolute():
            self.db_path = project_root / db_path
        else:
            self.db_path = Path(db_path)
        
        self.sql_dir = project_root / "advisor" / "data" / "sql"
        self._init_database()
    
    def _load_sql(self, filename: str) -> str:
        """Load SQL query from file."""
        sql_file = self.sql_dir / filename
        return sql_file.read_text()
    
    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            schema_sql = self._load_sql("schema.sql")
            cursor.executescript(schema_sql)
            conn.commit()
    
    def add_stock(self, symbol: str) -> int:
        """Add a stock symbol to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO stocks (symbol) VALUES (?)", (symbol.upper(),))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Stock already exists, return its ID
                cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol.upper(),))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def get_stock_id(self, symbol: str) -> Optional[int]:
        """Get stock ID by symbol."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol.upper(),))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def add_mention(self, stock_id: int, source: str, content: str, 
                   url: Optional[str] = None, external_id: Optional[str] = None,
                   metadata: Optional[str] = None) -> int:
        """Add a stock mention to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mentions (stock_id, source, content, url, external_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (stock_id, source, content, url, external_id, metadata))
            return cursor.lastrowid
    
    def get_stocks(self) -> List[Dict[str, Any]]:
        """Get all stocks from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stocks ORDER BY symbol")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_mentions(self, stock_id: Optional[int] = None, 
                    source: Optional[str] = None,
                    since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get stock mentions with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM mentions WHERE 1=1"
            params = []
            
            if stock_id:
                query += " AND stock_id = ?"
                params.append(stock_id)
            
            if source:
                query += " AND source = ?"
                params.append(source)
            
            if since:
                query += " AND collected_at >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY collected_at DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def mention_exists(self, source: str, external_id: str) -> bool:
        """Check if a stock mention already exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM mentions 
                WHERE source = ? AND external_id = ?
            """, (source, external_id))
            return cursor.fetchone() is not None
    
    # Backward compatibility methods (deprecated)
    def add_data_point(self, stock_id: int, source: str, content: str, 
                      url: Optional[str] = None, external_id: Optional[str] = None,
                      metadata: Optional[str] = None) -> int:
        """Deprecated: Use add_mention() instead."""
        return self.add_mention(stock_id, source, content, url, external_id, metadata)
    
    def get_data_points(self, stock_id: Optional[int] = None, 
                       source: Optional[str] = None,
                       since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Deprecated: Use get_mentions() instead."""
        return self.get_mentions(stock_id, source, since)
    
    def data_point_exists(self, source: str, external_id: str) -> bool:
        """Deprecated: Use mention_exists() instead."""
        return self.mention_exists(source, external_id)