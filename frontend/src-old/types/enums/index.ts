/**
 * Enums Barrel Export
 * 
 * Centralized export of all domain enums for easy importing throughout the application.
 * 
 * Usage:
 *   import { FundStatus, EntityType, BankType } from '@/types/enums';
 * 
 * Organization:
 *   - Fund Domain: All fund-related enums
 *   - Entity Domain: Entity-related enums
 *   - Banking Domain: Banking-related enums
 *   - Company Domain: Company enums
 *   - Rates Domain: FX and risk-free rate enums
 *   - Shared Domain: Cross-domain shared enums
 */

// ============================================================================
// FUND DOMAIN ENUMS
// ============================================================================
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
  isOutgoingCashFlow
} from './fund.enums';

// ============================================================================
// ENTITY DOMAIN ENUMS
// ============================================================================
export {
  EntityType,
  SortFieldEntity
} from './entity.enums';

// ============================================================================
// BANKING DOMAIN ENUMS
// ============================================================================
export {
  BankType,
  BankStatus,
  SortFieldBank,
  BankAccountType,
  BankAccountStatus,
  SortFieldBankAccount,
  SortFieldBankAccountBalance
} from './banking.enums';

// ============================================================================
// COMPANY DOMAIN ENUMS
// ============================================================================
export {
  CompanyType,
  CompanyStatus,
  SortFieldCompany,
  SortFieldContact
} from './company.enums';

// ============================================================================
// RATES DOMAIN ENUMS
// ============================================================================
export {
  SortFieldFxRate,
  RiskFreeRateType,
  SortFieldRiskFreeRate
} from './rates.enums';

// ============================================================================
// SHARED DOMAIN ENUMS
// ============================================================================
export {
  SortOrder,
  EventOperation,
  Country,
  Currency,
  DomainObjectType,
  SortFieldDomainUpdateEvent,
  isReverseSortOrder,
  getCurrencyDecimalPlaces
} from './shared.enums';
