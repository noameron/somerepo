#!/usr/bin/env python3
"""Database migration script to rename data_points to mentions."""

import sqlite3
from pathlib import Path

def migrate_database():
    """Migrate the database from data_points to mentions table."""
    db_path = Path("advisor/data/sentinel.db")
    
    if not db_path.exists():
        print("No database found to migrate.")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if data_points table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='data_points'
        """)
        
        if not cursor.fetchone():
            print("data_points table not found. Migration not needed.")
            return
        
        # Check if mentions table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='mentions'
        """)
        
        if cursor.fetchone():
            print("mentions table already exists. Copying data...")
            # Copy data from data_points to mentions
            cursor.execute("""
                INSERT OR IGNORE INTO mentions 
                SELECT * FROM data_points
            """)
        else:
            print("Renaming data_points table to mentions...")
            # Rename table
            cursor.execute("ALTER TABLE data_points RENAME TO mentions")
            
            # Update indexes
            cursor.execute("DROP INDEX IF EXISTS idx_data_points_stock_id")
            cursor.execute("DROP INDEX IF EXISTS idx_data_points_source")
            cursor.execute("DROP INDEX IF EXISTS idx_data_points_collected_at")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_stock_id ON mentions(stock_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_source ON mentions(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_collected_at ON mentions(collected_at)")
        
        conn.commit()
        print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()