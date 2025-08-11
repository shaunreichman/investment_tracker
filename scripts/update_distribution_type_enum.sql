-- Update distribution_type enum to include dividend_franked and dividend_unfranked
-- This script adds the missing enum values to the existing enum type

-- First, let's check what values currently exist
SELECT DISTINCT distribution_type FROM fund_events;

-- For PostgreSQL, we can use ALTER TYPE to add new enum values
-- This is the preferred approach for PostgreSQL enum modifications

-- Step 1: Create new table with updated enum
CREATE TABLE fund_events_new (
    id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_date DATE NOT NULL,
    amount FLOAT,
    distribution_type VARCHAR(50) CHECK (distribution_type IN ('INCOME', 'DIVIDEND', 'dividend_franked', 'dividend_unfranked', 'INTEREST', 'CAPITAL_GAIN', 'RETURN_OF_CAPITAL', 'OTHER')),
    units_purchased FLOAT,
    units_sold FLOAT,
    unit_price FLOAT,
    nav_per_share FLOAT,
    brokerage_fee FLOAT DEFAULT 0.0,
    tax_payment_type VARCHAR(50),
    description TEXT,
    reference_number VARCHAR(100),
    units_owned FLOAT,
    cost_of_units FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES funds (id)
);

-- Step 2: Copy all data from old table to new table
INSERT INTO fund_events_new 
SELECT * FROM fund_events;

-- Step 3: Drop the old table
DROP TABLE fund_events;

-- Step 4: Rename new table to original name
ALTER TABLE fund_events_new RENAME TO fund_events;

-- Step 5: Verify the update worked
SELECT DISTINCT distribution_type FROM fund_events; 