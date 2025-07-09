-- Stock-related queries

-- Insert stock
INSERT INTO stocks (symbol) VALUES (?);

-- Get stock ID by symbol
SELECT id FROM stocks WHERE symbol = ?;

-- Get all stocks
SELECT * FROM stocks ORDER BY symbol;