/**
 * Fund Event Cash Flow Domain Type Definitions
 * 
 * TypeScript interfaces matching backend fund event cash flow model exactly.
 * Source: src/fund/models/fund_event_cash_flow.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import {
  CashFlowDirection,
  SortFieldFundEventCashFlow,
} from './fundEnums';
import { Currency, SortOrder } from '@/shared/types';

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

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Get Fund Event Cash Flows Response - List of fund event cash flows
 */
export type GetFundEventCashFlowsResponse = FundEventCashFlow[];

/**
 * Get Fund Event Cash Flow Response - Single fund event cash flow
 */
export type GetFundEventCashFlowResponse = FundEventCashFlow;

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

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

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Fund event cash flow summary for list views
 */
export type FundEventCashFlowSummary = Pick<
  FundEventCashFlow,
  'id' | 'fund_event_id' | 'bank_account_id' | 'direction' | 'transfer_date' | 'amount'
>;

