/**
 * Fund Event Domain Type Definitions
 * 
 * TypeScript interfaces matching backend fund event model exactly.
 * Source: src/fund/models/fund_event.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import {
  EventType,
  DistributionType,
  TaxPaymentType,
  GroupType,
  SortFieldFundEvent,
} from './fundEnums';
import { SortOrder } from '@/shared/types';

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
// REQUEST DTOs
// ============================================================================

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

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Get Fund Events Response - Object containing events array and count
 */
export interface GetFundEventsResponse {
  events: FundEvent[];
  count: number;
}

/**
 * Get Fund Event Response - Single fund event
 */
export type GetFundEventResponse = FundEvent;

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

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

// ============================================================================
// UTILITY TYPES
// ============================================================================

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
  fund_event_cash_flows?: import('./fundEventCashFlow').FundEventCashFlow[];
};

