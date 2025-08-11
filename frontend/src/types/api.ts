// API Response and Request TypeScript Interfaces
// This file defines all TypeScript interfaces for API communication

// ============================================================================
// ENUM TYPES
// ============================================================================

export enum FundType {
  NAV_BASED = 'nav_based',
  COST_BASED = 'cost_based'
}

export enum FundStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  REALIZED = 'realized',
  COMPLETED = 'completed'
}

export enum EventType {
  CAPITAL_CALL = 'CAPITAL_CALL',
  RETURN_OF_CAPITAL = 'RETURN_OF_CAPITAL',
  UNIT_PURCHASE = 'UNIT_PURCHASE',
  UNIT_SALE = 'UNIT_SALE',
  NAV_UPDATE = 'NAV_UPDATE',
  DISTRIBUTION = 'DISTRIBUTION',
  TAX_PAYMENT = 'TAX_PAYMENT',
  EOFY_DEBT_COST = 'EOFY_DEBT_COST',
  DAILY_RISK_FREE_INTEREST_CHARGE = 'DAILY_RISK_FREE_INTEREST_CHARGE',
  MANAGEMENT_FEE = 'MANAGEMENT_FEE',
  CARRIED_INTEREST = 'CARRIED_INTEREST',
  OTHER = 'OTHER'
}

export enum DistributionType {
  INTEREST = 'INTEREST',
  DIVIDEND = 'DIVIDEND',
  OTHER = 'OTHER'
}

export enum TaxPaymentType {
  INTEREST_TAX = 'INTEREST_TAX',
  DIVIDEND_TAX = 'DIVIDEND_TAX',
  CAPITAL_GAINS_TAX = 'CAPITAL_GAINS_TAX',
  NON_RESIDENT_INTEREST_WITHHOLDING = 'NON_RESIDENT_INTEREST_WITHHOLDING',
  EOFY_INTEREST_TAX = 'EOFY_INTEREST_TAX',
  DIVIDENDS_FRANKED_TAX = 'DIVIDENDS_FRANKED_TAX',
  DIVIDENDS_UNFRANKED_TAX = 'DIVIDENDS_UNFRANKED_TAX'
}

export enum GroupType {
  INTEREST_WITHHOLDING = 'interest_withholding',
  TAX_STATEMENT = 'tax_statement'
}

// ============================================================================
// CORE ENTITY INTERFACES
// ============================================================================

export interface InvestmentCompany {
  id: number;
  name: string;
  description?: string | undefined;
  website?: string | undefined;
  contact_email?: string | undefined;
  contact_phone?: string | undefined;
  fund_count?: number | undefined;
  active_funds?: number | undefined;
  total_commitments?: number | undefined;
  total_equity_balance?: number | undefined;
  created_at: string;
  updated_at: string;
  funds_count?: number | undefined;
}

export interface Entity {
  id: number;
  name: string;
  description?: string | undefined;
  created_at: string;
  updated_at: string;
}

export interface Fund {
  id: number;
  name: string;
  fund_type?: string | undefined;
  tracking_type: FundType;
  description?: string | undefined;
  currency: string;
  commitment_amount?: number | undefined;
  expected_irr?: number | undefined;
  expected_duration_months?: number | undefined;
  investment_company_id: number;
  entity_id: number;
  current_equity_balance: number;
  average_equity_balance: number;
  status: FundStatus;
  final_tax_statement_received: boolean;
  current_units?: number | undefined;
  current_unit_price?: number | undefined;
  current_nav_total?: number | undefined;
  total_cost_basis?: number | undefined;
  created_at: string;
  updated_at: string;
  // Related data
  investment_company?: InvestmentCompany | undefined;
  entity?: Entity | undefined;
  events?: FundEvent[] | undefined;
  tax_statements?: TaxStatement[] | undefined;
  statistics?: FundStatistics | undefined;
}

export interface FundEvent {
  id: number;
  fund_id: number;
  event_type: EventType;
  event_date: string;
  amount?: number | undefined;
  description?: string | undefined;
  reference_number?: string | undefined;
  distribution_type?: DistributionType | undefined;
  units_purchased?: number | undefined;
  units_sold?: number | undefined;
  unit_price?: number | undefined;
  nav_per_share?: number | undefined;
  brokerage_fee?: number | undefined;
  tax_payment_type?: TaxPaymentType | undefined;
  units_owned?: number | undefined;
  cost_of_units?: number | undefined;
  created_at: string;
  updated_at: string;
  
  // CALCULATED: Grouping flags set by backend when creating events
  is_grouped?: boolean | undefined;  // (CALCULATED) whether this event is part of a group
  group_id?: number | undefined;     // (CALCULATED) unique identifier for the group (auto-generated)
  group_type?: GroupType | undefined; // (CALCULATED) type of grouping (INTEREST_WITHHOLDING, TAX_STATEMENT, etc.)
  group_position?: number | undefined; // (CALCULATED) position within group for ordering (0=first, 1=second, etc.)
}

export interface TaxStatement {
  id: number;
  fund_id: number;
  entity_id: number;
  financial_year: string;
  tax_payment_date: string;
  statement_date: string;
  interest_received_in_cash: number;
  interest_receivable_this_fy: number;
  interest_receivable_prev_fy: number;
  interest_non_resident_withholding_tax_from_statement: number;
  interest_income_tax_rate: number;
  interest_income_amount: number;
  interest_tax_amount: number;
  interest_non_resident_withholding_tax_already_withheld: number;
  dividend_franked_income_amount: number;
  dividend_unfranked_income_amount: number;
  dividend_franked_income_tax_rate: number;
  dividend_unfranked_income_tax_rate: number;
  capital_gain_income_amount: number;
  capital_gain_income_tax_rate: number;
  eofy_debt_interest_deduction_rate: number;
  fy_debt_interest_deduction_sum_of_daily_interest: number;
  fy_debt_interest_deduction_total_deduction: number;
  foreign_income: number;
  capital_gains: number;
  other_income: number;
  foreign_tax_credits: number;
  non_resident: boolean;
  accountant?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// DASHBOARD AND SUMMARY INTERFACES
// ============================================================================

export interface PortfolioSummary {
  total_funds: number;
  active_funds: number;
  total_equity_balance: number;
  total_average_equity_balance: number;
  recent_events_count: number;
  total_tax_statements: number;
  last_updated: string;
}

export interface FundStatistics {
  total_events: number;
  total_tax_statements: number;
  recent_events_count: number;
  current_equity_balance: number;
  average_equity_balance: number;
  total_units_owned?: number | undefined;
  current_unit_price?: number | undefined;
  total_cost_basis?: number | undefined;
}

export interface DashboardData {
  portfolio_summary: PortfolioSummary;
  funds: Fund[];
  recent_events: FundEvent[];
  performance: any; // TODO: Define specific performance interface
}

// ============================================================================
// API REQUEST INTERFACES
// ============================================================================

export interface CreateInvestmentCompanyData {
  name: string;
  description?: string;
}

export interface CreateEntityData {
  name: string;
  description?: string;
}

export interface CreateFundData {
  name: string;
  fund_type?: string;
  tracking_type: FundType;
  description?: string;
  currency?: string;
  commitment_amount?: number;
  expected_irr?: number;
  expected_duration_months?: number;
  investment_company_id: number;
  entity_id: number;
}

export interface CreateFundEventData {
  event_type: EventType;
  event_date: string;
  amount?: number;
  description?: string;
  reference_number?: string;
  distribution_type?: DistributionType;
  units_purchased?: number;
  units_sold?: number;
  unit_price?: number;
  nav_per_share?: number;
  brokerage_fee?: number;
  tax_payment_type?: TaxPaymentType;
}



export interface CreateTaxStatementData {
  entity_id: number;
  financial_year: string;
  statement_date: string;
  eofy_debt_interest_deduction_rate: number;
  interest_received_in_cash?: number;
  interest_receivable_this_fy?: number;
  interest_receivable_prev_fy?: number;
  interest_non_resident_withholding_tax_from_statement?: number;
  interest_income_tax_rate?: number;
  dividend_franked_income_amount?: number;
  dividend_unfranked_income_amount?: number;
  dividend_franked_income_tax_rate?: number;
  dividend_unfranked_income_tax_rate?: number;
  capital_gain_income_amount?: number;
  capital_gain_income_tax_rate?: number;
  accountant?: string;
  notes?: string;
  non_resident?: boolean;
}

// ============================================================================
// API RESPONSE INTERFACES
// ============================================================================

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// ============================================================================
// ERROR INTERFACES
// ============================================================================

export interface ApiError {
  error: string;
  message?: string;
  status?: number;
  details?: any;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type FundListResponse = Fund[];
export type FundEventListResponse = FundEvent[];
export type TaxStatementListResponse = TaxStatement[];
export type InvestmentCompanyListResponse = InvestmentCompany[];
export type EntityListResponse = Entity[];

// ============================================================================
// EXTENDED INTERFACES FOR COMPONENT-SPECIFIC FIELDS
// ============================================================================

/**
 * Extended FundEvent interface for FundDetail component
 * Includes tax statement fields and withholding tax context
 */
export interface ExtendedFundEvent extends Omit<FundEvent, 'amount'> {
  // Override amount to be nullable instead of optional
  amount: number | null;
  
  // NAV-specific fields
  previous_nav_per_share?: number | null;
  nav_change_absolute?: number | null;
  nav_change_percentage?: number | null;
  
  // Tax statement fields for TAX_PAYMENT events
  interest_income_amount?: number | null;
  interest_income_tax_rate?: number | null;
  dividend_franked_income_amount?: number | null;
  dividend_franked_income_tax_rate?: number | null;
  dividend_unfranked_income_amount?: number | null;
  dividend_unfranked_income_tax_rate?: number | null;
  capital_gain_income_amount?: number | null;
  capital_gain_income_tax_rate?: number | null;
  
  // Tax statement fields for EOFY_DEBT_COST events
  eofy_debt_interest_deduction_sum_of_daily_interest?: number | null;
  eofy_debt_interest_deduction_rate?: number | null;
  eofy_debt_interest_deduction_total_deduction?: number | null;
  
  // Withholding tax context (added by handleEditEvent)
  has_withholding_tax?: boolean;
  withholding_amount?: number | null;
  withholding_rate?: number | null;
  net_interest?: number | null;
  
  // CALCULATED: Grouping flags set by backend when creating events
  is_grouped?: boolean;  // (CALCULATED) whether this event is part of a group
  group_id?: number;     // (CALCULATED) unique identifier for the group (auto-generated)
  group_type?: GroupType; // (CALCULATED) type of grouping (INTEREST_WITHHOLDING, TAX_STATEMENT, etc.)
  group_position?: number; // (CALCULATED) position within group for ordering (0=first, 1=second, etc.)
  
  // Tax statement relationship for grouped events
  tax_statement?: TaxStatement | null;
}

/**
 * Extended FundStatistics interface for FundDetail component
 * Includes detailed event counts and date ranges
 */
export interface ExtendedFundStatistics extends FundStatistics {
  capital_calls: number;
  distributions: number;
  nav_updates: number;
  unit_purchases: number;
  unit_sales: number;
  total_capital_called: number;
  total_capital_returned: number;
  total_distributions: number;
  first_event_date: string | null;
  last_event_date: string | null;
}

/**
 * Extended Fund interface for FundDetail component
 * Includes display-specific fields and new calculated fields for fund detail redesign
 */
export interface ExtendedFund extends Omit<Fund, 'investment_company' | 'entity'> {
  // Display-specific fields (strings instead of objects)
  investment_company: string;  // Company name as string
  entity: string;              // Entity name as string
  
  // New calculated fields for fund detail redesign
  current_nav_fund_value?: number | null;        // NAV fund value calculation
  total_tax_payments?: number | null;            // Sum of tax payment events
  total_daily_interest_charges?: number | null;  // Sum of daily charge events
  total_unit_purchases?: number | null;          // Total unit purchases (NAV-based funds)
  total_unit_sales?: number | null;              // Total unit sales (NAV-based funds)
  total_capital_calls?: number | null;           // Total capital calls (cost-based funds)
  total_capital_returns?: number | null;         // Total capital returns (cost-based funds)
  total_distributions?: number | null;           // Total distributions
  actual_duration_months?: number | null;        // Calculated fund duration
  completed_irr?: number | null;                 // IRR for completed funds
  completed_after_tax_irr?: number | null;      // After-tax IRR for completed funds
  completed_real_irr?: number | null;            // Real IRR for completed funds
  start_date?: string | null;                    // First event date
  end_date?: string | null;                      // Last event date (if completed)
}

/**
 * FundDetailData interface for the complete fund detail response
 */
export interface FundDetailData {
  fund: ExtendedFund;
  events: ExtendedFundEvent[];
  statistics: ExtendedFundStatistics;
}

// ============================================================================
// COMPANIES UI ENHANCED API INTERFACES
// ============================================================================

export interface CompanyOverviewResponse {
  company: {
    id: number;
    name: string;
    company_type: string | null;
    business_address: string | null;
    website: string | null;
    contacts: Array<{
      id: number;
      name: string;
      title: string | null;
      direct_number: string | null;
      direct_email: string | null;
      notes: string | null;
    }>;
  };
  portfolio_summary: {
    total_committed_capital: number;
    total_current_value: number;
    total_invested_capital: number;
    active_funds_count: number;
    completed_funds_count: number;
    fund_status_breakdown: {
      active_funds_count: number;
      completed_funds_count: number;
      suspended_funds_count: number;
      realized_funds_count: number;
    };
  };
  performance_summary: {
    average_completed_irr: number | null;
    total_realized_gains: number | null;
    total_realized_losses: number | null;
  };
  last_activity: {
    last_activity_date: string | null;
    days_since_last_activity: number | null;
  };
}

export interface EnhancedFund {
  id: number;
  name: string;
  description: string | null;
  currency: string;
  fund_type: string;
  status: string;
  tracking_type: string;
  
  fund_details: {
    start_date: string;
    end_date: string | null;
    actual_duration_days: number | null;
    days_since_last_activity: number;
  };
  
  equity: {
    commitment: number;
    invested_capital: number;
    current_value: number;
    current_equity_balance: number;
  };
  
  estimated_return: {
    expected_irr: number | null;
    duration_months: number | null;
  };
  
  distributions: {
    distribution_count: number;
    total_distribution_amount: number;
    last_distribution_date: string | null;
    distribution_frequency_months: number | null;
  };
  
  returns: {
    completed_irr: number | null;
    performance_vs_expected: number | null;
  };
  
  performance: {
    unrealized_gains_losses: number;
    realized_gains_losses: number;
    total_profit_loss: number;
  };
}

export interface EnhancedFundsResponse {
  funds: EnhancedFund[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_funds: number;
    per_page: number;
  };
  filters: {
    applied_status_filter: string;
    applied_search: string | null;
  };
}

export interface CompanyDetailsResponse {
  company: {
    id: number;
    name: string;
    company_type: string | null;
    business_address: string | null;
    website: string | null;
    contacts: Array<{
      id: number;
      name: string;
      title: string | null;
      direct_number: string | null;
      direct_email: string | null;
      notes: string | null;
    }>;
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

// All interfaces and types are already exported above
// This section is for documentation purposes only 