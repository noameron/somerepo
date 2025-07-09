-- Database schema for the Advisor system

-- Create stocks table
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create mentions table
CREATE TABLE IF NOT EXISTS mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    external_id TEXT,
    metadata TEXT,
    FOREIGN KEY (stock_id) REFERENCES stocks (id),
    UNIQUE(source, external_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_mentions_stock_id ON mentions(stock_id);
CREATE INDEX IF NOT EXISTS idx_mentions_source ON mentions(source);
CREATE INDEX IF NOT EXISTS idx_mentions_collected_at ON mentions(collected_at);