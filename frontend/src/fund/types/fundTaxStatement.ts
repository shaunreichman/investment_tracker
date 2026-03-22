/**
 * Fund Tax Statement Domain Type Definitions
 * 
 * TypeScript interfaces matching backend fund tax statement model exactly.
 * Source: src/fund/models/fund_tax_statement.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { SortFieldFundTaxStatement } from './fundEnums';
import { SortOrder } from '@/shared/types';

// ============================================================================
// FUND TAX STATEMENT MODEL
// ============================================================================

/**
 * FundTaxStatement - Represents tax statements from funds for specific financial years
 * 
 * Backend source: src/fund/models/fund_tax_statement.py
 */
export interface FundTaxStatement {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string; // ISO 8601 datetime string
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string; // ISO 8601 datetime string
  
  // Relationship fields
  /** Foreign key to fund (RELATIONSHIP) */
  fund_id: number;
  
  /** Foreign key to entity (RELATIONSHIP) */
  entity_id: number;
  
  // Basic fields
  /** Financial year (e.g., "2023-24") (MANUAL) */
  financial_year: string;
  
  /** Start date of the financial year (CALCULATED) */
  financial_year_start_date: string; // ISO 8601 date string
  
  /** End date of the financial year (CALCULATED) */
  financial_year_end_date: string; // ISO 8601 date string
  
  /** Date when additional tax is due (HYBRID) */
  tax_payment_date: string | null; // ISO 8601 date string
  
  /** Date the tax statement was issued (MANUAL) */
  statement_date: string | null; // ISO 8601 date string
  
  // Interest income fields
  /** Calculated from manual interest fields (CALCULATED) */
  interest_income_amount: number;
  
  /** Manually defined interest tax rate (%) (MANUAL) */
  interest_income_tax_rate: number;
  
  /** Calculated from interest income and rate (CALCULATED) */
  interest_tax_amount: number;
  
  /** Actual cash flow received this FY (MANUAL) */
  interest_received_in_cash: number;
  
  /** Accounting income for this FY, not yet received (MANUAL) */
  interest_receivable_this_fy: number;
  
  /** Accounting income from prev FY, received this FY (MANUAL) */
  interest_receivable_prev_fy: number;
  
  /** Withholding tax as reported (MANUAL) */
  interest_non_resident_withholding_tax_from_statement: number;
  
  /** Sum of TAX_PAYMENT events (CALCULATED) */
  interest_non_resident_withholding_tax_already_withheld: number;
  
  // Dividend income fields
  /** Manual or calculated franked dividends (HYBRID) */
  dividend_franked_income_amount: number;
  
  /** Manual or calculated unfranked dividends (HYBRID) */
  dividend_unfranked_income_amount: number;
  
  /** Manually defined franked dividend tax rate (%) (MANUAL) */
  dividend_franked_income_tax_rate: number;
  
  /** Manually defined unfranked dividend tax rate (%) (MANUAL) */
  dividend_unfranked_income_tax_rate: number;
  
  /** Calculated franked dividend tax amount (CALCULATED) */
  dividend_franked_tax_amount: number;
  
  /** Calculated unfranked dividend tax amount (CALCULATED) */
  dividend_unfranked_tax_amount: number;
  
  /** True if amount comes from tax statement (CALCULATED) */
  dividend_franked_income_amount_from_tax_statement_flag: boolean;
  
  /** True if amount comes from tax statement (CALCULATED) */
  dividend_unfranked_income_amount_from_tax_statement_flag: boolean;
  
  // Capital gain income fields
  /** Manual or calculated capital gains (HYBRID) */
  capital_gain_income_amount: number;
  
  /** Manually defined capital gain tax rate (%) (MANUAL) */
  capital_gain_income_tax_rate: number;
  
  /** Calculated capital gain tax amount (CALCULATED) */
  capital_gain_tax_amount: number;
  
  /** Calculated capital gain discount (50% for AU holdings > 12 months) (CALCULATED) */
  capital_gain_discount_amount: number;
  
  /** True if amount comes from tax statement (CALCULATED) */
  capital_gain_income_amount_from_tax_statement_flag: boolean;
  
  /** Set to false by user to disable discount (e.g., if non-resident and no discount available) (MANUAL) */
  capital_gain_discount_applicable_flag: boolean;
  
  // Debt cost tracking for real IRR calculations
  /** Total interest expense for the EOFY (CALCULATED) */
  eofy_debt_interest_deduction_sum_of_daily_interest: number;
  
  /** Tax deduction rate for interest (e.g., 30.0 for 30%) (MANUAL) */
  eofy_debt_interest_deduction_rate: number;
  
  /** Calculated tax benefit from interest deduction (CALCULATED) */
  eofy_debt_interest_deduction_total_deduction: number;
  
  // Additional fields
  /** Name of fund's accountant who prepared the tax statement (MANUAL) */
  accountant: string | null;
  
  /** Additional notes (MANUAL) */
  notes: string | null;
}

// ============================================================================
// REQUEST DTOs
// ============================================================================

/**
 * Create Fund Tax Statement Request
 */
export interface CreateFundTaxStatementRequest {
  /** ID of the entity (required) */
  entity_id: number;
  
  /** Financial year (required, 4 characters) */
  financial_year: string;
  
  /** Tax payment date (optional) */
  tax_payment_date?: string;
  
  /** Statement date (optional) */
  statement_date?: string;
  
  /** Interest income tax rate (optional) */
  interest_income_tax_rate?: number;
  
  /** Interest received in cash (optional) */
  interest_received_in_cash?: number;
  
  /** Interest receivable this FY (optional) */
  interest_receivable_this_fy?: number;
  
  /** Interest receivable previous FY (optional) */
  interest_receivable_prev_fy?: number;
  
  /** Interest non-resident withholding tax from statement (optional) */
  interest_non_resident_withholding_tax_from_statement?: number;
  
  /** Dividend franked income amount (optional) */
  dividend_franked_income_amount?: number;
  
  /** Dividend unfranked income amount (optional) */
  dividend_unfranked_income_amount?: number;
  
  /** Dividend franked income tax rate (optional) */
  dividend_franked_income_tax_rate?: number;
  
  /** Dividend unfranked income tax rate (optional) */
  dividend_unfranked_income_tax_rate?: number;
  
  /** Capital gain income amount (optional) */
  capital_gain_income_amount?: number;
  
  /** Capital gain income tax rate (optional) */
  capital_gain_income_tax_rate?: number;
  
  /** Capital gain discount applicable flag (optional) */
  capital_gain_discount_applicable_flag?: boolean;
  
  /** EOFY debt interest deduction rate (optional) */
  eofy_debt_interest_deduction_rate?: number;
  
  /** Accountant (optional) */
  accountant?: string;
  
  /** Notes (optional) */
  notes?: string;
}

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Get Fund Tax Statements Response - List of fund tax statements
 */
export type GetFundTaxStatementsResponse = FundTaxStatement[];

/**
 * Get Fund Tax Statement Response - Single fund tax statement
 */
export type GetFundTaxStatementResponse = FundTaxStatement;

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

/**
 * Query parameters for GET /api/fund-tax-statements
 * 
 * All parameters are optional. Supports filtering and sorting.
 */
export interface GetFundTaxStatementsQueryParams {
  /** Filter by fund ID */
  fund_id?: number;
  
  /** Filter by fund IDs (array) */
  fund_ids?: number[];
  
  /** Filter by entity ID */
  entity_id?: number;
  
  /** Filter by entity IDs (array) */
  entity_ids?: number[];
  
  /** Filter by financial year */
  financial_year?: string;
  
  /** Filter by financial years (array) */
  financial_years?: string[];
  
  /** Start of tax payment date range */
  start_tax_payment_date?: string;
  
  /** End of tax payment date range */
  end_tax_payment_date?: string;
  
  /** Sort by field */
  sort_by?: SortFieldFundTaxStatement;
  
  /** Sort order */
  sort_order?: SortOrder;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Fund tax statement summary for list views
 */
export type FundTaxStatementSummary = Pick<
  FundTaxStatement,
  'id' | 'fund_id' | 'entity_id' | 'financial_year' | 'tax_payment_date'
>;

