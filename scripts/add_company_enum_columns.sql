-- Migration Script: Add Company Enum Columns
-- This script adds the new company_type and status enum columns to the investment_companies table
-- Run this script to migrate existing data to use the new enum constraints

-- Step 1: Add new enum columns alongside existing string columns
ALTER TABLE investment_companies 
ADD COLUMN company_type_enum VARCHAR(100),
ADD COLUMN status_enum VARCHAR(50) DEFAULT 'ACTIVE' NOT NULL;

-- Step 2: Create the enum types in PostgreSQL
-- Note: This is PostgreSQL-specific syntax. For other databases, you may need to adjust.
DO $$
BEGIN
    -- Create CompanyType enum if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'company_type_enum') THEN
        CREATE TYPE company_type_enum AS ENUM (
            'Private Equity',
            'Venture Capital', 
            'Real Estate',
            'Infrastructure',
            'Credit',
            'Hedge Fund',
            'Family Office',
            'Investment Bank',
            'Asset Management',
            'Other'
        );
    END IF;
    
    -- Create CompanyStatus enum if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'company_status_enum') THEN
        CREATE TYPE company_status_enum AS ENUM (
            'ACTIVE',
            'INACTIVE',
            'SUSPENDED',
            'CLOSED'
        );
    END IF;
END$$;

-- Step 3: Migrate existing data to new enum columns
UPDATE investment_companies 
SET 
    company_type_enum = CASE 
        WHEN company_type = 'Private Equity' THEN 'Private Equity'
        WHEN company_type = 'Venture Capital' THEN 'Venture Capital'
        WHEN company_type = 'Real Estate' THEN 'Real Estate'
        WHEN company_type = 'Infrastructure' THEN 'Infrastructure'
        WHEN company_type = 'Credit' THEN 'Credit'
        WHEN company_type = 'Hedge Fund' THEN 'Hedge Fund'
        WHEN company_type = 'Family Office' THEN 'Family Office'
        WHEN company_type = 'Investment Bank' THEN 'Investment Bank'
        WHEN company_type = 'Asset Management' THEN 'Asset Management'
        WHEN company_type = 'Other' THEN 'Other'
        ELSE 'Other'
    END,
    status_enum = 'ACTIVE'  -- Default all existing companies to ACTIVE
WHERE company_type_enum IS NULL OR status_enum IS NULL;

-- Step 4: Drop old string columns and rename enum columns
ALTER TABLE investment_companies 
DROP COLUMN company_type,
DROP COLUMN status;

ALTER TABLE investment_companies 
RENAME COLUMN company_type_enum TO company_type;

ALTER TABLE investment_companies 
RENAME COLUMN status_enum TO status;

-- Step 5: Add constraints to ensure data integrity
ALTER TABLE investment_companies 
ALTER COLUMN company_type TYPE company_type_enum USING company_type::company_type_enum,
ALTER COLUMN status TYPE company_status_enum USING status::company_status_enum;

-- Step 6: Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_investment_companies_company_type ON investment_companies(company_type);
CREATE INDEX IF NOT EXISTS idx_investment_companies_status ON investment_companies(status);
CREATE INDEX IF NOT EXISTS idx_investment_companies_type_status ON investment_companies(company_type, status);
CREATE INDEX IF NOT EXISTS idx_investment_companies_name_status ON investment_companies(name, status);

-- Step 7: Verify migration
SELECT 
    'Migration completed successfully' as status,
    COUNT(*) as total_companies,
    COUNT(CASE WHEN company_type IS NOT NULL THEN 1 END) as companies_with_type,
    COUNT(CASE WHEN status IS NOT NULL THEN 1 END) as companies_with_status
FROM investment_companies;
