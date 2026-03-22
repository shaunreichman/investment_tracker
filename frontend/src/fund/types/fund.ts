/**
 * Fund Domain Type Definitions
 * 
 * TypeScript interfaces matching backend fund model exactly.
 * Source: src/fund/models/fund.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import {
  FundStatus,
  FundTrackingType,
  FundInvestmentType,
  FundTaxStatementFinancialYearType,
  SortFieldFund,
} from './fundEnums';
import { Country, Currency, SortOrder } from '@/shared/types';
import type { FundEvent } from './fundEvent';
import type { FundEventCashFlow } from './fundEventCashFlow';
import type { FundTaxStatement } from './fundTaxStatement';

// ============================================================================
// FUND MODEL
// ============================================================================

/**
 * Fund - Represents an investment fund
 * 
 * Backend source: src/fund/models/fund.py
 */
export interface Fund {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string; // ISO 8601 datetime string
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string; // ISO 8601 datetime string
  
  // Relationship fields
  /** Foreign key to company (RELATIONSHIP) */
  company_id: number;
  
  /** Foreign key to entity (RELATIONSHIP) */
  entity_id: number;
  
  // Basic fund information (MANUAL)
  /** Fund name (MANUAL) */
  name: string;
  
  /** Type of fund investment (MANUAL) */
  fund_investment_type: FundInvestmentType;
  
  /** Tracking type (NAV_BASED or COST_BASED) (MANUAL) */
  tracking_type: FundTrackingType;
  
  /** Fund description (MANUAL) */
  description: string | null;
  
  /** Currency code for the fund (MANUAL) */
  currency: Currency;
  
  /** Tax jurisdiction for the fund (MANUAL) */
  tax_jurisdiction: Country;
  
  /** Financial year type (CALCULATED) */
  tax_statement_financial_year_type: FundTaxStatementFinancialYearType;
  
  // Expected information (MANUAL)
  /** Expected IRR as percentage (MANUAL) */
  expected_irr: number | null;
  
  /** Expected fund duration in months (MANUAL) */
  expected_duration_months: number | null;
  
  // Investment tracking fields (common)
  /** Total amount committed to the fund (MANUAL) */
  commitment_amount: number | null;
  
  /** Current equity balance from capital movements (CALCULATED) */
  current_equity_balance: number;
  
  /** Time-weighted average equity balance (CALCULATED) */
  average_equity_balance: number;
  
  // IRR storage fields (CALCULATED)
  /** Completed gross IRR when realized/completed (CALCULATED) */
  completed_irr_gross: number | null;
  
  /** Completed after-tax IRR when completed (CALCULATED) */
  completed_irr_after_tax: number | null;
  
  /** Completed real IRR when completed (CALCULATED) */
  completed_irr_real: number | null;
  
  // Profitability storage fields (CALCULATED)
  /** PNL (CALCULATED) */
  pnl: number;
  
  /** Realized PNL (CALCULATED) */
  realized_pnl: number;
  
  /** Unrealized PNL (CALCULATED) */
  unrealized_pnl: number;
  
  /** Realized Capital Gain PNL (CALCULATED) */
  realized_pnl_capital_gain: number;
  
  /** Unrealized Capital Gain PNL (CALCULATED) */
  unrealized_pnl_capital_gain: number;
  
  /** Realized Dividend PNL (CALCULATED) */
  realized_pnl_dividend: number;
  
  /** Realized Interest PNL (CALCULATED) */
  realized_pnl_interest: number;
  
  /** Realized Distribution PNL (CALCULATED) */
  realized_pnl_distribution: number;
  
  // NAV-based fund specific fields (CALCULATED)
  /** Current number of units owned (CALCULATED) */
  current_units: number;
  
  /** Current unit price from latest NAV update (CALCULATED) */
  current_unit_price: number;
  
  /** Current NAV total (units * unit price) (CALCULATED) */
  current_nav_total: number;
  
  // Cost-based fund specific fields (CALCULATED)
  /** Total cost basis for cost-based funds (CALCULATED) */
  total_cost_basis: number;
  
  // Status and metadata
  /** Fund status (ACTIVE/SUSPENDED/REALIZED/COMPLETED) (CALCULATED) */
  status: FundStatus;
  
  /** Fund start date based on first capital call or unit purchase (CALCULATED) */
  start_date: string | null; // ISO 8601 date string
  
  /** Fund end date based on last equity/distribution event after equity balance reached zero (CALCULATED) */
  end_date: string | null; // ISO 8601 date string
  
  /** Current fund duration in months based on status (CALCULATED) */
  current_duration: number | null;
}

// ============================================================================
// REQUEST DTOs
// ============================================================================

/**
 * Create Fund Request
 * 
 * Backend validation:
 * - name: required, 2-255 characters
 * - entity_id: required, min 1
 * - company_id: required, min 1
 * - tracking_type: required, valid FundTrackingType enum
 * - tax_jurisdiction: required, valid Country enum
 * - currency: required, valid Currency enum
 * - fund_investment_type: optional, valid FundInvestmentType enum
 * - description: optional, max 1000 characters
 * - expected_irr: optional, 0.0-100.0 (non-negative)
 * - expected_duration_months: optional, 0-1200 (non-negative)
 * - commitment_amount: optional, must be positive (>0), max 9,999,999,999
 */
export interface CreateFundRequest {
  /** Fund name (required, 2-255 characters) */
  name: string;
  
  /** Associated entity ID (required) */
  entity_id: number;
  
  /** Associated company ID (required) */
  company_id: number;
  
  /** Tracking type (required) */
  tracking_type: FundTrackingType;
  
  /** Tax jurisdiction (required) */
  tax_jurisdiction: Country;
  
  /** Currency (required) */
  currency: Currency;
  
  /** Fund investment type (optional) */
  fund_investment_type?: FundInvestmentType;
  
  /** Fund description (optional, max 1000 characters) */
  description?: string;
  
  /** Expected IRR (optional, 0.0-100.0, non-negative) */
  expected_irr?: number;
  
  /** Expected duration months (optional, 0-1200, non-negative) */
  expected_duration_months?: number;
  
  /** Commitment amount (optional, must be positive if provided, max 9,999,999,999) */
  commitment_amount?: number;
}

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Get Funds Response - List of funds
 */
export interface GetFundsResponse {
  /** List of funds */
  funds: Fund[];
  
  /** Total count */
  count: number;
}

/**
 * Get Fund Response - Single fund
 */
export type GetFundResponse = Fund;

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

/**
 * Query parameters for GET /api/funds
 * 
 * All parameters are optional. Supports filtering and sorting.
 */
export interface GetFundsQueryParams {
  /** Filter by company ID */
  company_id?: number;
  
  /** Filter by company IDs (array) */
  company_ids?: number[];
  
  /** Filter by entity ID */
  entity_id?: number;
  
  /** Filter by entity IDs (array) */
  entity_ids?: number[];
  
  /** Filter by fund status */
  fund_status?: FundStatus;
  
  /** Filter by fund statuses (array) */
  fund_statuses?: FundStatus[];
  
  /** Filter by fund tracking type */
  fund_tracking_type?: FundTrackingType;
  
  /** Filter by fund tracking types (array) */
  fund_tracking_types?: FundTrackingType[];
  
  /** Start of start date range */
  start_start_date?: string;
  
  /** End of start date range */
  end_start_date?: string;
  
  /** Start of end date range */
  start_end_date?: string;
  
  /** End of end date range */
  end_end_date?: string;
  
  /** Sort by field */
  sort_by?: SortFieldFund;
  
  /** Sort order */
  sort_order?: SortOrder;
  
  /** Include fund events in response */
  include_fund_events?: boolean;
  
  /** Include fund event cash flows in response */
  include_fund_event_cash_flows?: boolean;
  
  /** Include fund tax statements in response */
  include_fund_tax_statements?: boolean;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial fund for list views (minimal data)
 */
export type FundSummary = Pick<
  Fund,
  'id' | 'name' | 'tracking_type' | 'status' | 'currency' | 'current_equity_balance'
>;

/**
 * Fund with relationships (for detail views)
 */
export type FundWithRelationships = Fund & {
  /** Included fund events */
  fund_events?: FundEvent[];
  /** Included fund event cash flows */
  fund_event_cash_flows?: FundEventCashFlow[];
  /** Included fund tax statements */
  fund_tax_statements?: FundTaxStatement[];
};

// ============================================================================
// FINANCIAL YEAR SUPPORT TYPES
// ============================================================================

/**
 * Map of financial year label to its final calendar date (CALCULATED)
 * 
 * Matches the backend response for GET /api/funds/:id/financial-years.
 */
export type FundFinancialYearMap = Record<string, string>;

/**
 * Structured financial year representation for UI consumption (CALCULATED)
 */
export interface FundFinancialYear {
  /** Financial year label (CALCULATED) */
  financialYear: string;
  /** Final calendar date for the financial year (CALCULATED) */
  finalDate: string;
}
