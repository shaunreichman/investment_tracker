/**
 * Models Barrel Export
 * 
 * Centralized export of all domain model types.
 * 
 * Usage:
 *   import { Bank, BankAccount, Fund } from '@/types/models';
 */

// ============================================================================
// BANKING DOMAIN
// ============================================================================
export type {
  // Core models
  Bank,
  BankAccount,
  BankAccountBalance,
  
  // Request DTOs
  CreateBankRequest,
  CreateBankAccountRequest,
  CreateBankAccountBalanceRequest,
  
  // Response DTOs
  GetBanksResponse,
  GetBankResponse,
  GetBankAccountsResponse,
  GetBankAccountResponse,
  GetBankAccountBalancesResponse,
  GetBankAccountBalanceResponse,
  
  // Query parameters
  GetBanksQueryParams,
  GetBankAccountsQueryParams,
  GetBankAccountBalancesQueryParams,
  
  // Utility types
  BankSummary,
  BankAccountSummary,
  BankWithAccounts,
  BankAccountWithBalances
} from './banking';

// ============================================================================
// RATES DOMAIN
// ============================================================================
export type {
  // Core models
  RiskFreeRate,
  FxRate,
  
  // Request DTOs
  CreateRiskFreeRateRequest,
  CreateFxRateRequest,
  
  // Response DTOs
  GetRiskFreeRatesResponse,
  GetRiskFreeRateResponse,
  GetFxRatesResponse,
  GetFxRateResponse,
  
  // Query parameters
  GetRiskFreeRatesQueryParams,
  GetFxRatesQueryParams,
  
  // Utility types
  RiskFreeRateSummary,
  FxRateSummary
} from './rates';

// ============================================================================
// ENTITY DOMAIN
// ============================================================================
export type {
  // Core model
  Entity,
  
  // Request DTOs
  CreateEntityRequest,
  
  // Response DTOs
  GetEntitiesResponse,
  GetEntityResponse,
  
  // Query parameters
  GetEntitiesQueryParams,
  
  // Utility types
  EntitySummary,
  EntityWithRelationships
} from './entity';

// ============================================================================
// COMPANY DOMAIN
// ============================================================================
export type {
  // Core models
  Company,
  Contact,
  
  // Request DTOs
  CreateCompanyRequest,
  CreateContactRequest,
  // Note: Update DTOs not yet implemented in backend
  
  // Response DTOs
  GetCompaniesResponse,
  GetCompanyResponse,
  GetContactsResponse,
  GetContactResponse,
  
  // Query parameters
  GetCompaniesQueryParams,
  GetContactsQueryParams,
  
  // Utility types
  CompanySummary,
  ContactSummary,
  CompanyWithContacts,
  CompanyWithFunds,
  ContactWithCompany
} from './company';

// ============================================================================
// FUND DOMAIN
// ============================================================================
export type {
  // Core models
  Fund,
  FundEvent,
  FundEventCashFlow,
  FundTaxStatement,
  
  // Request DTOs
  CreateFundRequest,
  CreateCapitalCallRequest,
  CreateReturnOfCapitalRequest,
  CreateUnitPurchaseRequest,
  CreateUnitSaleRequest,
  CreateNavUpdateRequest,
  CreateDistributionRequest,
  CreateFundEventCashFlowRequest,
  CreateFundTaxStatementRequest,
  
  // Response DTOs
  GetFundsResponse,
  GetFundResponse,
  GetFundEventsResponse,
  GetFundEventResponse,
  GetFundEventCashFlowsResponse,
  GetFundEventCashFlowResponse,
  GetFundTaxStatementsResponse,
  GetFundTaxStatementResponse,
  
  // Query parameters
  GetFundsQueryParams,
  GetFundEventsQueryParams,
  GetFundEventCashFlowsQueryParams,
  GetFundTaxStatementsQueryParams,
  
  // Utility types
  FundSummary,
  FundWithRelationships,
  FundEventSummary,
  FundEventWithCashFlows,
  FundEventCashFlowSummary,
  FundTaxStatementSummary
} from './fund';
