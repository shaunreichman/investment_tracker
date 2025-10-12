/**
 * Banking Domain Enums
 * 
 * TypeScript enums matching backend banking domain enums exactly.
 * Source: src/banking/enums/
 * 
 * DO NOT modify these enums without updating the corresponding Python enums.
 * These must remain in sync with the backend for API communication.
 */

// ============================================================================
// BANK ENUMS (src/banking/enums/bank_enums.py)
// ============================================================================

/**
 * Banking institution classification.
 * 
 * Defines the type of banking institution for regulatory and operational purposes.
 */
export enum BankType {
  /** Commercial bank (retail and business banking) */
  COMMERCIAL = 'COMMERCIAL',
  /** Investment bank (securities and advisory) */
  INVESTMENT = 'INVESTMENT',
  /** Central bank (monetary policy and regulation) */
  CENTRAL = 'CENTRAL',
  /** Cooperative bank (member-owned) */
  COOPERATIVE = 'COOPERATIVE',
  /** Digital-only bank (online banking) */
  DIGITAL = 'DIGITAL'
}

/**
 * Bank status enum.
 */
export enum BankStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  CLOSED = 'CLOSED'
}

/**
 * Sort field enum for banks.
 */
export enum SortFieldBank {
  NAME = 'NAME',
  COUNTRY = 'COUNTRY',
  CURRENCY = 'CURRENCY',
  TYPE = 'TYPE',
  STATUS = 'STATUS',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT'
}

// ============================================================================
// BANK ACCOUNT ENUMS (src/banking/enums/bank_account_enums.py)
// ============================================================================

/**
 * Bank account classification types.
 * 
 * Defines the type of bank account for regulatory and operational purposes.
 */
export enum BankAccountType {
  /** Checking/current account (daily transactions) */
  CHECKING = 'CHECKING',
  /** Savings account (interest-bearing) */
  SAVINGS = 'SAVINGS',
  /** Investment account (securities trading) */
  INVESTMENT = 'INVESTMENT',
  /** Business account (commercial operations) */
  BUSINESS = 'BUSINESS',
  /** Trust account (fiduciary operations) */
  TRUST = 'TRUST',
  /** Joint account (multiple owners) */
  JOINT = 'JOINT'
}

/**
 * Bank account status enum.
 */
export enum BankAccountStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  CLOSED = 'CLOSED',
  SUSPENDED = 'SUSPENDED',
  OVERDRAFT = 'OVERDRAFT'
}

/**
 * Sort field enum for bank accounts.
 */
export enum SortFieldBankAccount {
  NAME = 'NAME',
  ACCOUNT_NUMBER = 'ACCOUNT_NUMBER',
  CURRENCY = 'CURRENCY',
  STATUS = 'STATUS',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT'
}

// ============================================================================
// BANK ACCOUNT BALANCE ENUMS (src/banking/enums/bank_account_balance_enums.py)
// ============================================================================

/**
 * Sort field enum for bank account balances.
 */
export enum SortFieldBankAccountBalance {
  DATE = 'DATE'
}
