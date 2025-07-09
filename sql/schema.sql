-- Database schema for the Advisor system

-- Create stocks table
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create data_points table
CREATE TABLE IF NOT EXISTS data_points (
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
CREATE INDEX IF NOT EXISTS idx_data_points_stock_id ON data_points(stock_id);
CREATE INDEX IF NOT EXISTS idx_data_points_source ON data_points(source);
CREATE INDEX IF NOT EXISTS idx_data_points_collected_at ON data_points(collected_at);