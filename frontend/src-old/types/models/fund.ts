/**
 * Fund Domain Models
 * 
 * TypeScript interfaces matching backend fund domain models exactly.
 * Source: src/fund/models/*.py
 * 
 * DO NOT modify these types without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import {
  FundStatus,
  FundTrackingType,
  FundInvestmentType,
  FundTaxStatementFinancialYearType,
  SortFieldFund,
  EventType,
  DistributionType,
  TaxPaymentType,
  GroupType,
  SortFieldFundEvent,
  CashFlowDirection,
  SortFieldFundEventCashFlow,
  SortFieldFundTaxStatement,
} from '../enums/fund.enums';
import { Country, Currency, SortOrder } from '../enums/shared.enums';

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
// FUND EVENT MODEL
// ============================================================================

/**
 * FundEvent - Represents a fund event (capital call, distribution, NAV update, etc.)
 * 
 * Backend source: src/fund/models/fund_event.py
 */
export interface FundEvent {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string; // ISO 8601 datetime string
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string; // ISO 8601 datetime string
  
  // Relationship fields
  /** Link to fund (RELATIONSHIP) */
  fund_id: number;
  
  // Event details
  /** Type of fund event (MANUAL) */
  event_type: EventType;
  
  /** Date when event occurred (MANUAL) */
  event_date: string; // ISO 8601 date string
  
  /** Event amount (MANUAL) */
  amount: number | null;
  
  /** Description of the event (MANUAL) */
  description: string | null;
  
  /** External reference number (MANUAL) */
  reference_number: string | null;
  
  // NAV-specific fields (for NAV_BASED funds)
  /** NAV per share for NAV_UPDATE events (MANUAL) */
  nav_per_share: number | null;
  
  /** Previous NAV per share for NAV_UPDATE events (CALCULATED) */
  previous_nav_per_share: number | null;
  
  /** Absolute change in NAV for NAV_UPDATE events (CALCULATED) */
  nav_change_absolute: number | null;
  
  /** Percentage change in NAV for NAV_UPDATE events (CALCULATED) */
  nav_change_percentage: number | null;
  
  // Distribution-specific fields
  /** Type of distribution if applicable (MANUAL) */
  distribution_type: DistributionType | null;
  
  /** Tax withholding amount if applicable (MANUAL) */
  tax_withholding: number | null;
  
  /** Flag for distributions with associated withholding tax (MANUAL) */
  has_withholding_tax: boolean;
  
  // Tax-specific fields
  /** Type of tax payment (MANUAL) */
  tax_payment_type: TaxPaymentType | null;
  
  /** Foreign key to tax statement for TAX_PAYMENT events (CALCULATED) */
  tax_statement_id: number | null;
  
  // Unit transaction fields
  /** Units purchased in this event (MANUAL) */
  units_purchased: number | null;
  
  /** Units sold in this event (MANUAL) */
  units_sold: number | null;
  
  /** Unit price for this transaction (MANUAL) */
  unit_price: number | null;
  
  /** Brokerage fee for unit transactions (MANUAL) */
  brokerage_fee: number | null;
  
  /** Cumulative units owned after this event (CALCULATED) */
  units_owned: number | null;
  
  // Calculated fields
  /** For NAV-based funds: FIFO cost base after this event. For cost-based funds: net capital after this event (CALCULATED) */
  current_equity_balance: number | null;
  
  // Debt cost fields
  /** Current equity balance used for this daily debt cost event (CALCULATED) */
  dc_current_equity_balance: number | null;
  
  /** Risk free rate used for this daily debt cost event (CALCULATED) */
  dc_risk_free_rate: number | null;
  
  // Cash flow fields
  /** Auto-managed flag set by reconciliation logic (SYSTEM) */
  is_cash_flow_complete: boolean;
  
  /** Balance of cash flows for this event (CALCULATED) */
  cash_flow_balance_amount: number;
  
  // Grouping fields (CALCULATED)
  /** Whether this event is part of a group (CALCULATED) */
  is_grouped: boolean;
  
  /** Unique identifier for the group (CALCULATED) */
  group_id: number | null;
  
  /** Type of grouping (CALCULATED) */
  group_type: GroupType | null;
  
  /** Position within group for ordering (CALCULATED) */
  group_position: number | null;
}

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
// FUND EVENT CASH FLOW MODEL
// ============================================================================

/**
 * FundEventCashFlow - Represents actual cash transfers linked to fund events
 * 
 * Backend source: src/fund/models/fund_event_cash_flow.py
 */
export interface FundEventCashFlow {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string; // ISO 8601 datetime string
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string; // ISO 8601 datetime string
  
  // Relationship fields
  /** Link to parent event (RELATIONSHIP) */
  fund_event_id: number;
  
  /** Account where the transfer occurred (RELATIONSHIP) */
  bank_account_id: number;
  
  // Cash flow details
  /** Inflow/outflow from investor perspective (MANUAL) */
  direction: CashFlowDirection;
  
  /** ISO-4217 currency code; must equal BankAccount.currency (MANUAL) */
  currency: string;
  
  /** Date of transaction on bank statement (MANUAL) */
  transfer_date: string; // ISO 8601 date string
  
  /** Date of the fund event (CALCULATED) */
  fund_event_date: string; // ISO 8601 date string
  
  /** Whether the transfer date is in a different month to the fund event date (CALCULATED) */
  different_month: boolean;
  
  /** Optional link to bank account balance after adjustment (RELATIONSHIP) */
  adjusted_bank_account_balance_id: number | null;
  
  /** Transfer amount in currency (MANUAL) */
  amount: number;
  
  /** Free-text bank reference (MANUAL) */
  reference: string | null;
  
  /** Additional notes/description (MANUAL) */
  description: string | null;
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

/**
 * Create Capital Call Request
 */
export interface CreateCapitalCallRequest {
  /** Event date in YYYY-MM-DD format (required) */
  event_date: string;
  
  /** Event amount (required) */
  amount: number;
  
  /** Event description (optional) */
  description?: string;
  
  /** Event reference number (optional) */
  reference_number?: string;
}

/**
 * Create Return of Capital Request
 */
export interface CreateReturnOfCapitalRequest {
  /** Event date in YYYY-MM-DD format (required) */
  event_date: string;
  
  /** Event amount (required) */
  amount: number;
  
  /** Event description (optional) */
  description?: string;
  
  /** Event reference number (optional) */
  reference_number?: string;
}

/**
 * Create Unit Purchase Request
 */
export interface CreateUnitPurchaseRequest {
  /** Event date in YYYY-MM-DD format (required) */
  event_date: string;
  
  /** Units purchased (required) */
  units_purchased: number;
  
  /** Unit price (required) */
  unit_price: number;
  
  /** Brokerage fee (optional) */
  brokerage_fee?: number;
  
  /** Event description (optional) */
  description?: string;
  
  /** Event reference number (optional) */
  reference_number?: string;
}

/**
 * Create Unit Sale Request
 */
export interface CreateUnitSaleRequest {
  /** Event date in YYYY-MM-DD format (required) */
  event_date: string;
  
  /** Units sold (required) */
  units_sold: number;
  
  /** Unit price (required) */
  unit_price: number;
  
  /** Brokerage fee (optional) */
  brokerage_fee?: number;
  
  /** Event description (optional) */
  description?: string;
  
  /** Event reference number (optional) */
  reference_number?: string;
}

/**
 * Create NAV Update Request
 */
export interface CreateNavUpdateRequest {
  /** Event date in YYYY-MM-DD format (required) */
  event_date: string;
  
  /** NAV per share (required) */
  nav_per_share: number;
  
  /** Event description (optional) */
  description?: string;
  
  /** Event reference number (optional) */
  reference_number?: string;
}

/**
 * Create Distribution Request
 */
export interface CreateDistributionRequest {
  /** Event date in YYYY-MM-DD format (required) */
  event_date: string;
  
  /** Type of distribution (required) */
  distribution_type: DistributionType;
  
  /** Distribution amount (optional if has_withholding_tax) */
  amount?: number;
  
  /** Whether the distribution has withholding tax (optional) */
  has_withholding_tax?: boolean;
  
  /** Gross amount (optional, required if has_withholding_tax) */
  gross_amount?: number;
  
  /** Net amount (optional, required if has_withholding_tax) */
  net_amount?: number;
  
  /** Withholding tax amount (optional, required if has_withholding_tax) */
  withholding_tax_amount?: number;
  
  /** Withholding tax rate (optional, required if has_withholding_tax) */
  withholding_tax_rate?: number;
  
  /** Event description (optional) */
  description?: string;
  
  /** Event reference number (optional) */
  reference_number?: string;
}

/**
 * Create Fund Event Cash Flow Request
 */
export interface CreateFundEventCashFlowRequest {
  /** ID of the bank account (required) */
  bank_account_id: number;
  
  /** Direction of the cash flow (required) */
  direction: CashFlowDirection;
  
  /** Transfer date in YYYY-MM-DD format (required) */
  transfer_date: string;
  
  /** Currency of the cash flow (required) */
  currency: Currency;
  
  /** Amount of the cash flow (required) */
  amount: number;
  
  /** Reference of the cash flow (optional) */
  reference?: string;
  
  /** Description of the cash flow (optional) */
  description?: string;
}

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
 * Get Funds Response - List of funds
 */
export type GetFundsResponse = Fund[];

/**
 * Get Fund Response - Single fund
 */
export type GetFundResponse = Fund;

/**
 * Get Fund Events Response - List of fund events
 */
export type GetFundEventsResponse = FundEvent[];

/**
 * Get Fund Event Response - Single fund event
 */
export type GetFundEventResponse = FundEvent;

/**
 * Get Fund Event Cash Flows Response - List of fund event cash flows
 */
export type GetFundEventCashFlowsResponse = FundEventCashFlow[];

/**
 * Get Fund Event Cash Flow Response - Single fund event cash flow
 */
export type GetFundEventCashFlowResponse = FundEventCashFlow;

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

/**
 * Query parameters for GET /api/fund-events
 * 
 * All parameters are optional. Supports filtering and sorting.
 */
export interface GetFundEventsQueryParams {
  /** Filter by fund ID */
  fund_id?: number;
  
  /** Filter by fund IDs (array) */
  fund_ids?: number[];
  
  /** Filter by event type */
  event_type?: EventType;
  
  /** Filter by event types (array) */
  event_types?: EventType[];
  
  /** Filter by distribution type */
  distribution_type?: DistributionType;
  
  /** Filter by distribution types (array) */
  distribution_types?: DistributionType[];
  
  /** Filter by tax payment type */
  tax_payment_type?: TaxPaymentType;
  
  /** Filter by tax payment types (array) */
  tax_payment_types?: TaxPaymentType[];
  
  /** Filter by group ID */
  group_id?: number;
  
  /** Filter by group IDs (array) */
  group_ids?: number[];
  
  /** Filter by group type */
  group_type?: GroupType;
  
  /** Filter by group types (array) */
  group_types?: GroupType[];
  
  /** Filter by cash flow complete status */
  is_cash_flow_complete?: boolean;
  
  /** Start of event date range */
  start_event_date?: string;
  
  /** End of event date range */
  end_event_date?: string;
  
  /** Sort by field */
  sort_by?: SortFieldFundEvent;
  
  /** Sort order */
  sort_order?: SortOrder;
  
  /** Include fund event cash flows in response */
  include_fund_event_cash_flows?: boolean;
}

/**
 * Query parameters for GET /api/fund-event-cash-flows
 * 
 * All parameters are optional. Supports filtering and sorting.
 */
export interface GetFundEventCashFlowsQueryParams {
  /** Filter by fund ID */
  fund_id?: number;
  
  /** Filter by fund IDs (array) */
  fund_ids?: number[];
  
  /** Filter by fund event ID */
  fund_event_id?: number;
  
  /** Filter by fund event IDs (array) */
  fund_event_ids?: number[];
  
  /** Filter by bank account ID */
  bank_account_id?: number;
  
  /** Filter by bank account IDs (array) */
  bank_account_ids?: number[];
  
  /** Filter by different month flag */
  different_month?: boolean;
  
  /** Filter by adjusted bank account balance ID */
  adjusted_bank_account_balance_id?: number;
  
  /** Filter by adjusted bank account balance IDs (array) */
  adjusted_bank_account_balance_ids?: number[];
  
  /** Filter by currency */
  currency?: Currency;
  
  /** Filter by currencies (array) */
  currencies?: Currency[];
  
  /** Start of transfer date range */
  start_transfer_date?: string;
  
  /** End of transfer date range */
  end_transfer_date?: string;
  
  /** Start of fund event date range */
  start_fund_event_date?: string;
  
  /** End of fund event date range */
  end_fund_event_date?: string;
  
  /** Sort by field */
  sort_by?: SortFieldFundEventCashFlow;
  
  /** Sort order */
  sort_order?: SortOrder;
}

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

/**
 * Fund event summary for list views
 */
export type FundEventSummary = Pick<
  FundEvent,
  'id' | 'fund_id' | 'event_type' | 'event_date' | 'amount' | 'description'
>;

/**
 * Fund event with cash flows
 */
export type FundEventWithCashFlows = FundEvent & {
  /** Included fund event cash flows */
  fund_event_cash_flows?: FundEventCashFlow[];
};

/**
 * Fund event cash flow summary for list views
 */
export type FundEventCashFlowSummary = Pick<
  FundEventCashFlow,
  'id' | 'fund_event_id' | 'bank_account_id' | 'direction' | 'transfer_date' | 'amount'
>;

/**
 * Fund tax statement summary for list views
 */
export type FundTaxStatementSummary = Pick<
  FundTaxStatement,
  'id' | 'fund_id' | 'entity_id' | 'financial_year' | 'tax_payment_date'
>;
