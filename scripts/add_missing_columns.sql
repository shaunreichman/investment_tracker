-- Add missing columns to fund_events table
-- These columns are expected by the Python model but missing from the database

-- Add previous_nav_per_share column
ALTER TABLE fund_events ADD COLUMN previous_nav_per_share FLOAT;

-- Add nav_change_absolute column  
ALTER TABLE fund_events ADD COLUMN nav_change_absolute FLOAT;

-- Add nav_change_percentage column
ALTER TABLE fund_events ADD COLUMN nav_change_percentage FLOAT;

-- Add current_equity_balance column
ALTER TABLE fund_events ADD COLUMN current_equity_balance FLOAT;

-- Verify the columns were added
PRAGMA table_info(fund_events); 