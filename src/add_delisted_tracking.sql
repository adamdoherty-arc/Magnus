-- Add delisted symbol tracking to database schema
-- This migration adds support for tracking delisted or problematic symbols

-- Add is_delisted column to stocks table if it doesn't exist
ALTER TABLE stocks
ADD COLUMN IF NOT EXISTS is_delisted BOOLEAN DEFAULT FALSE;

-- Add delisted_date column to track when symbol was marked as delisted
ALTER TABLE stocks
ADD COLUMN IF NOT EXISTS delisted_date TIMESTAMP;

-- Add delisted_reason column to track why symbol was marked as delisted
ALTER TABLE stocks
ADD COLUMN IF NOT EXISTS delisted_reason VARCHAR(255);

-- Create index for faster queries on delisted symbols
CREATE INDEX IF NOT EXISTS idx_stocks_is_delisted ON stocks(is_delisted);

-- Add comment to table
COMMENT ON COLUMN stocks.is_delisted IS 'Flag indicating if the stock symbol is delisted or unavailable';
COMMENT ON COLUMN stocks.delisted_date IS 'Date when the symbol was marked as delisted';
COMMENT ON COLUMN stocks.delisted_reason IS 'Reason why the symbol was marked as delisted (e.g., "No data from yfinance", "Expecting value error")';

-- Optional: Mark known delisted symbols
UPDATE stocks
SET is_delisted = TRUE,
    delisted_date = NOW(),
    delisted_reason = 'Known delisted symbol - yfinance data unavailable'
WHERE symbol IN ('BMNR', 'PLUG', 'BBAI')
  AND is_delisted = FALSE;
