-- Stock mentions queries

-- Insert mention
INSERT INTO mentions (stock_id, source, content, url, external_id, metadata)
VALUES (?, ?, ?, ?, ?, ?);

-- Get mentions with filtering
SELECT * FROM mentions 
WHERE 1=1
  AND ($stock_id IS NULL OR stock_id = $stock_id)
  AND ($source IS NULL OR source = $source)
  AND ($since IS NULL OR collected_at >= $since)
ORDER BY collected_at DESC;

-- Check if mention exists
SELECT 1 FROM mentions 
WHERE source = ? AND external_id = ?;