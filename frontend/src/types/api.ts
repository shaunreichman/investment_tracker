// API Response and Request TypeScript Interfaces
// This file defines all TypeScript interfaces for API communication

// ============================================================================
// ENUM TYPES
// ============================================================================

export enum FundType {
  NAV_BASED = 'nav_based',
  COST_BASED = 'cost_based'
}

export enum EventType {
  CAPITAL_CALL = 'CAPITAL_CALL',
  RETURN_OF_CAPITAL = 'RETURN_OF_CAPITAL',
  UNIT_PURCHASE = 'UNIT_PURCHASE',
  UNIT_SALE = 'UNIT_SALE',
  NAV_UPDATE = 'NAV_UPDATE',
  DISTRIBUTION = 'DISTRIBUTION',
  TAX_PAYMENT = 'TAX_PAYMENT'
}

export enum DistributionType {
  INTEREST = 'INTEREST',
  DIVIDEND = 'DIVIDEND',
  OTHER = 'OTHER'
}

export enum TaxPaymentType {
  INTEREST_TAX = 'INTEREST_TAX',
  DIVIDEND_TAX = 'DIVIDEND_TAX',
  CAPITAL_GAINS_TAX = 'CAPITAL_GAINS_TAX'
}

// ============================================================================
// CORE ENTITY INTERFACES
// ============================================================================

export interface InvestmentCompany {
  id: number;
  name: string;
  description?: string;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
  fund_count?: number;
  active_funds?: number;
  total_commitments?: number;
  total_equity_balance?: number;
  created_at: string;
  updated_at: string;
  funds_count?: number;
}

export interface Entity {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Fund {
  id: number;
  name: string;
  fund_type?: string;
  tracking_type: FundType;
  description?: string;
  currency: string;
  commitment_amount?: number;
  expected_irr?: number;
  expected_duration_months?: number;
  investment_company_id: number;
  entity_id: number;
  current_equity_balance: number;
  average_equity_balance: number;
  is_active: boolean;
  final_tax_statement_received: boolean;
  current_units?: number;
  current_unit_price?: number;
  total_cost_basis?: number;
  created_at: string;
  updated_at: string;
  // Related data
  investment_company?: InvestmentCompany;
  entity?: Entity;
  events?: FundEvent[];
  tax_statements?: TaxStatement[];
  statistics?: FundStatistics;
}

export interface FundEvent {
  id: number;
  fund_id: number;
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
  units_owned?: number;
  cost_of_units?: number;
  created_at: string;
  updated_at: string;
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
  total_units_owned?: number;
  current_unit_price?: number;
  total_cost_basis?: number;
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

export interface UpdateFundEventData extends CreateFundEventData {
  // Same as CreateFundEventData for now
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
// EXPORTS
// ============================================================================

// All interfaces and types are already exported above
// This section is for documentation purposes only 