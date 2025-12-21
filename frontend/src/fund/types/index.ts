/**
 * Fund Types Barrel Export
 * 
 * Centralized export of all fund domain types.
 * 
 * Usage:
 *   import { Fund, FundEvent, CreateFundRequest, GetFundsResponse } from '@/fund/types';
 */

// Fund types
export type {
  // Core models
  Fund,
  
  // Request DTOs
  CreateFundRequest,
  
  // Response DTOs
  GetFundsResponse,
  GetFundResponse,
  
  // Query parameters
  GetFundsQueryParams,
  
  // Utility types
  FundSummary,
  FundWithRelationships,
  FundFinancialYearMap,
  FundFinancialYear,
} from './fund';

// Fund event types
export type {
  // Core models
  FundEvent,
  
  // Request DTOs
  CreateCapitalCallRequest,
  CreateReturnOfCapitalRequest,
  CreateUnitPurchaseRequest,
  CreateUnitSaleRequest,
  CreateNavUpdateRequest,
  CreateDistributionRequest,
  
  // Response DTOs
  GetFundEventsResponse,
  GetFundEventResponse,
  
  // Query parameters
  GetFundEventsQueryParams,
  
  // Utility types
  FundEventSummary,
  FundEventWithCashFlows,
} from './fundEvent';

// Fund event cash flow types
export type {
  // Core models
  FundEventCashFlow,
  
  // Request DTOs
  CreateFundEventCashFlowRequest,
  
  // Response DTOs
  GetFundEventCashFlowsResponse,
  GetFundEventCashFlowResponse,
  
  // Query parameters
  GetFundEventCashFlowsQueryParams,
  
  // Utility types
  FundEventCashFlowSummary,
} from './fundEventCashFlow';

// Fund tax statement types
export type {
  // Core models
  FundTaxStatement,
  
  // Request DTOs
  CreateFundTaxStatementRequest,
  
  // Response DTOs
  GetFundTaxStatementsResponse,
  GetFundTaxStatementResponse,
  
  // Query parameters
  GetFundTaxStatementsQueryParams,
  
  // Utility types
  FundTaxStatementSummary,
} from './fundTaxStatement';

// Re-export enums from fundEnums.ts
export {
  // Fund enums
  FundStatus,
  FundTrackingType,
  FundInvestmentType,
  FundTaxStatementFinancialYearType,
  SortFieldFund,
  
  // Fund event enums
  EventType,
  DistributionType,
  TaxPaymentType,
  GroupType,
  SortFieldFundEvent,
  
  // Fund event cash flow enums
  CashFlowDirection,
  SortFieldFundEventCashFlow,
  
  // Fund tax statement enums
  SortFieldFundTaxStatement,
  
  // Helper functions
  isEquityEvent,
  isDistributionEvent,
  isSystemEvent,
  isEquityCallEvent,
  isEquityReturnEvent,
  isTaxStatementEvent,
  isTaxableDistribution,
  hasFrankingCredits,
  isWithholdingTax,
  isDividendTax,
  isIncomingCashFlow,
  isOutgoingCashFlow,
} from './fundEnums';
