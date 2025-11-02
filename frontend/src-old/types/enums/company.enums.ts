/**
 * Company Domain Enums
 * 
 * TypeScript enums matching backend company domain enums exactly.
 * Source: src/company/enums/
 * 
 * DO NOT modify these enums without updating the corresponding Python enums.
 * These must remain in sync with the backend for API communication.
 */

// ============================================================================
// COMPANY ENUMS (src/company/enums/company_enums.py)
// ============================================================================

/**
 * Company type enum for database constraints.
 * 
 * Defines the valid types of companies that can be stored
 * in the database.
 * 
 * NOTE: Uses human-readable strings (not UPPER_CASE like other enums)
 */
export enum CompanyType {
  /** Private equity investment firm */
  PRIVATE_EQUITY = 'Private Equity',
  /** Venture capital investment firm */
  VENTURE_CAPITAL = 'Venture Capital',
  /** Real estate investment firm */
  REAL_ESTATE = 'Real Estate',
  /** Infrastructure investment firm */
  INFRASTRUCTURE = 'Infrastructure',
  /** Credit/debt investment firm */
  CREDIT = 'Credit',
  /** Hedge fund management firm */
  HEDGE_FUND = 'Hedge Fund',
  /** Family office investment firm */
  FAMILY_OFFICE = 'Family Office',
  /** Investment banking firm */
  INVESTMENT_BANK = 'Investment Bank',
  /** Asset management firm */
  ASSET_MANAGEMENT = 'Asset Management',
  /** Investment group */
  INVESTMENT_GROUP = 'Investment Group',
  /** Other type of investment firm */
  OTHER = 'Other'
}

/**
 * Company status enum for database constraints.
 * 
 * Defines the possible statuses for companies.
 */
export enum CompanyStatus {
  /** Company is active and operational */
  ACTIVE = 'ACTIVE',
  /** Company is inactive */
  INACTIVE = 'INACTIVE',
  /** Company operations are completed */
  COMPLETED = 'COMPLETED',
  /** Company operations are suspended */
  SUSPENDED = 'SUSPENDED',
  /** Company has closed operations */
  CLOSED = 'CLOSED'
}

/**
 * Sort field enum for companies.
 */
export enum SortFieldCompany {
  NAME = 'NAME',
  STATUS = 'STATUS',
  START_DATE = 'START_DATE',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT'
}

// ============================================================================
// COMPANY CONTACT ENUMS (src/company/enums/company_contact_enums.py)
// ============================================================================

/**
 * Sort field enum for contacts.
 */
export enum SortFieldContact {
  NAME = 'NAME',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT'
}
