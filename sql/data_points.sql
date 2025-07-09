-- Data points queries

-- Insert data point
INSERT INTO data_points (stock_id, source, content, url, external_id, metadata)
VALUES (?, ?, ?, ?, ?, ?);

-- Get data points with filtering
SELECT * FROM data_points 
WHERE 1=1
  AND ($stock_id IS NULL OR stock_id = $stock_id)
  AND ($source IS NULL OR source = $source)
  AND ($since IS NULL OR collected_at >= $since)
ORDER BY collected_at DESC;

-- Check if data point exists
SELECT 1 FROM data_points 
WHERE source = ? AND external_id = ?;