/**
 * Shared Domain Enums
 * 
 * TypeScript enums matching backend shared domain enums exactly.
 * Source: src/shared/enums/
 * 
 * DO NOT modify these enums without updating the corresponding Python enums.
 * These must remain in sync with the backend for API communication.
 */

// ============================================================================
// SHARED ENUMS (src/shared/enums/shared_enums.py)
// ============================================================================

/**
 * Sort order enum.
 * 
 * Defines the order for sorting operations in APIs and queries.
 */
export enum SortOrder {
  /** Ascending order (A-Z, 1-9, oldest to newest) */
  ASC = 'ASC',
  /** Descending order (Z-A, 9-1, newest to oldest) */
  DESC = 'DESC'
}

/**
 * Event operation enum.
 * 
 * Defines all possible operations that can occur on an event.
 */
export enum EventOperation {
  /** Event creation operation */
  CREATE = 'CREATE',
  /** Event update operation */
  UPDATE = 'UPDATE',
  /** Event deletion operation */
  DELETE = 'DELETE'
}

/**
 * ISO 3166-1 alpha-2 country codes for banking operations.
 * 
 * Represents countries where banking operations can occur.
 */
export enum Country {
  /** Australia (with specific banking regulations) */
  AU = 'AU',
  /** United States (with SWIFT/BIC requirements) */
  US = 'US',
  /** United Kingdom (with SWIFT/BIC requirements) */
  UK = 'UK',
  /** Canada (with SWIFT/BIC requirements) */
  CA = 'CA',
  /** New Zealand (with specific banking regulations) */
  NZ = 'NZ',
  /** Singapore (with specific banking regulations) */
  SG = 'SG',
  /** Hong Kong (with specific banking regulations) */
  HK = 'HK',
  /** Japan (with specific banking regulations) */
  JP = 'JP',
  /** Germany (with SWIFT/BIC requirements) */
  DE = 'DE',
  /** France (with SWIFT/BIC requirements) */
  FR = 'FR',
  /** China (with SWIFT/BIC requirements) */
  CN = 'CN',
  /** Korea (with SWIFT/BIC requirements) */
  KR = 'KR'
}

/**
 * ISO 4217 currency codes for banking operations.
 * 
 * Defines supported currencies for banking operations.
 */
export enum Currency {
  /** Australian Dollar (primary currency) */
  AUD = 'AUD',
  /** US Dollar (major world currency) */
  USD = 'USD',
  /** Euro (major world currency) */
  EUR = 'EUR',
  /** British Pound (major world currency) */
  GBP = 'GBP',
  /** Canadian Dollar */
  CAD = 'CAD',
  /** New Zealand Dollar */
  NZD = 'NZD',
  /** Singapore Dollar */
  SGD = 'SGD',
  /** Hong Kong Dollar */
  HKD = 'HKD',
  /** Japanese Yen (major world currency) */
  JPY = 'JPY',
  /** Swiss Franc (major world currency) */
  CHF = 'CHF',
  /** Chinese Yuan (major world currency) */
  CNY = 'CNY',
  /** Korean Won (major world currency) */
  KRW = 'KRW'
}

// ============================================================================
// DOMAIN UPDATE EVENT ENUMS (src/shared/enums/domain_update_event_enums.py)
// ============================================================================

/**
 * Domain object type enum.
 */
export enum DomainObjectType {
  // Banking
  BANK = 'BANK',
  BANK_ACCOUNT = 'BANK_ACCOUNT',
  BANK_ACCOUNT_BALANCE = 'BANK_ACCOUNT_BALANCE',
  
  // Entity
  ENTITY = 'ENTITY',
  
  // Fund
  FUND = 'FUND',
  FUND_EVENT = 'FUND_EVENT',
  FUND_EVENT_CASH_FLOW = 'FUND_EVENT_CASH_FLOW',
  FUND_TAX_STATEMENT = 'FUND_TAX_STATEMENT',
  
  // Company
  COMPANY = 'COMPANY',
  CONTACT = 'CONTACT',
  
  // Rates
  FX_RATE = 'FX_RATE',
  RISK_FREE_RATE = 'RISK_FREE_RATE'
}

/**
 * Sort field enum for domain update events.
 */
export enum SortFieldDomainUpdateEvent {
  TIMESTAMP = 'TIMESTAMP',
  DOMAIN_OBJECT_TYPE = 'DOMAIN_OBJECT_TYPE',
  DOMAIN_OBJECT_ID = 'DOMAIN_OBJECT_ID',
  EVENT_OPERATION = 'EVENT_OPERATION',
  FUND_EVENT_TYPE = 'FUND_EVENT_TYPE'
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if sort order is reverse/descending.
 */
export function isReverseSortOrder(order: SortOrder): boolean {
  return order === SortOrder.DESC;
}

/**
 * Get the number of decimal places for a currency.
 */
export function getCurrencyDecimalPlaces(currency: Currency): number {
  // Japanese Yen uses 0 decimal places
  if (currency === Currency.JPY) {
    return 0;
  }
  // Most currencies use 2 decimal places
  return 2;
}
