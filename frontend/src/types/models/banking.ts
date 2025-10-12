/**
 * Banking Domain Type Definitions
 * 
 * TypeScript interfaces matching backend banking models exactly.
 * Source: src/banking/models/
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { 
  BankType, 
  BankStatus, 
  BankAccountType, 
  BankAccountStatus 
} from '../enums/banking.enums';
import { Country, Currency } from '../enums/shared.enums';

// ============================================================================
// BANK MODEL
// ============================================================================

/**
 * Bank - Represents a banking institution.
 * 
 * Source: src/banking/models/bank.py
 */
export interface Bank {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Manual fields
  /** Bank name (MANUAL) */
  name: string;
  
  /** ISO 3166-1 alpha-2 country code (MANUAL) */
  country: Country;
  
  /** Bank type (MANUAL) */
  bank_type?: BankType | null;
  
  /** Optional SWIFT/BIC identifier (MANUAL) */
  swift_bic?: string | null;
  
  // Calculated fields
  /** Bank status (CALCULATED) */
  status?: BankStatus | null;
  
  /** Total number of bank accounts (CALCULATED) */
  current_number_of_bank_accounts?: number;
  
  /** Total balance of all bank accounts (CALCULATED) */
  current_balance_in_bank_accounts?: number;
  
  // Relationships (optional - included based on API query params)
  /** Bank accounts (if include_bank_accounts=true) */
  bank_accounts?: BankAccount[];
}

// ============================================================================
// BANK ACCOUNT MODEL
// ============================================================================

/**
 * BankAccount - Represents an investor-owned bank account.
 * 
 * Source: src/banking/models/bank_account.py
 */
export interface BankAccount {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Relationship fields
  /** Owner entity ID (RELATIONSHIP) */
  entity_id: number;
  
  /** Linked bank ID (RELATIONSHIP) */
  bank_id: number;
  
  // Manual fields
  /** Human-readable account name/label (MANUAL) */
  account_name: string;
  
  /** Account number stored as provided (MANUAL) */
  account_number: string;
  
  /** ISO-4217 currency code (MANUAL) */
  currency: Currency;
  
  /** Account type (MANUAL) */
  account_type?: BankAccountType | null;
  
  // Calculated fields
  /** Account status (CALCULATED) */
  status?: BankAccountStatus | null;
  
  /** Current balance of the account in the currency of the account (CALCULATED) */
  current_balance?: number;
  
  // Relationships (optional - included based on API query params)
  /** Bank details (if included) */
  bank?: Bank;
  
  /** Entity details (if included) */
  entity?: {
    id: number;
    name: string;
    entity_type?: string;
  };
  
  /** Bank account balances (if include_bank_account_balances=true) */
  bank_account_balances?: BankAccountBalance[];
}

// ============================================================================
// BANK ACCOUNT BALANCE MODEL
// ============================================================================

/**
 * BankAccountBalance - Represents the balance of a bank account at a specific date.
 * 
 * Source: src/banking/models/bank_account_balance.py
 */
export interface BankAccountBalance {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Relationship fields
  /** Linked bank account ID (RELATIONSHIP) */
  bank_account_id: number;
  
  // Manual fields
  /** ISO-4217 currency code (MANUAL) */
  currency: Currency;
  
  /** Date of the balance - must be the last day of the month (MANUAL) */
  date: string; // ISO 8601 date string (YYYY-MM-DD)
  
  /** Balance of the bank account from the statement (MANUAL) */
  balance_statement: number;
  
  // Calculated fields
  /** Balance adjustment based on fund event cash flows different to the fund event date (CALCULATED) */
  balance_adjustment: number;
  
  /** Balance of the bank account after the adjustment (CALCULATED) */
  balance_final: number;
  
  // Relationships (optional)
  /** Bank account details (if included) */
  bank_account?: BankAccount;
}

// ============================================================================
// REQUEST DTOs
// ============================================================================

/**
 * Data required to create a new bank.
 */
export interface CreateBankRequest {
  /** Bank name (required) */
  name: string;
  
  /** ISO 3166-1 alpha-2 country code (required) */
  country: Country;
  
  /** Bank type (optional) */
  bank_type?: BankType;
  
  /** Optional SWIFT/BIC identifier (optional) */
  swift_bic?: string;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/banks/<id>, add UpdateBankRequest here

/**
 * Data required to create a new bank account.
 * 
 * Note: bank_id is provided via URL path parameter (/api/banks/:bank_id/bank-accounts), not in request body
 */
export interface CreateBankAccountRequest {
  /** Owner entity ID (required) */
  entity_id: number;
  
  /** Human-readable account name/label (required) */
  account_name: string;
  
  /** Account number (required) */
  account_number: string;
  
  /** ISO-4217 currency code (required) */
  currency: Currency;
  
  /** Account type (optional) */
  account_type?: BankAccountType;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/bank-accounts/<id>, add UpdateBankAccountRequest here

/**
 * Data required to create a new bank account balance.
 * 
 * Note: bank_id and bank_account_id are provided via URL path parameters
 * (/api/banks/:bank_id/bank-accounts/:bank_account_id/bank-account-balances), not in request body
 */
export interface CreateBankAccountBalanceRequest {
  /** ISO-4217 currency code (required) */
  currency: Currency;
  
  /** Date of the balance - must be the last day of the month (required) */
  date: string; // ISO 8601 date string (YYYY-MM-DD)
  
  /** Balance of the bank account from the statement (required) */
  balance_statement: number;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/bank-account-balances/<id>, add UpdateBankAccountBalanceRequest here

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Response from GET /api/banks
 */
export interface GetBanksResponse {
  /** List of banks */
  banks: Bank[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/banks/:id
 */
export interface GetBankResponse {
  /** Bank details */
  bank: Bank;
}

/**
 * Response from GET /api/bank-accounts
 */
export interface GetBankAccountsResponse {
  /** List of bank accounts */
  bank_accounts: BankAccount[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/bank-accounts/:id
 */
export interface GetBankAccountResponse {
  /** Bank account details */
  bank_account: BankAccount;
}

/**
 * Response from GET /api/bank-account-balances
 */
export interface GetBankAccountBalancesResponse {
  /** List of bank account balances */
  bank_account_balances: BankAccountBalance[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/bank-account-balances/:id
 */
export interface GetBankAccountBalanceResponse {
  /** Bank account balance details */
  bank_account_balance: BankAccountBalance;
}

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

/**
 * Query parameters for GET /api/banks
 */
export interface GetBanksQueryParams {
  /** Filter by bank name */
  name?: string;
  
  /** Filter by bank names (array) */
  names?: string[];
  
  /** Filter by country code */
  country?: Country;
  
  /** Filter by country codes (array) */
  countries?: Country[];
  
  /** Filter by bank type */
  bank_type?: BankType;
  
  /** Filter by bank types (array) */
  bank_types?: BankType[];
  
  /** Sort by field */
  sort_by?: string;
  
  /** Sort order */
  sort_order?: 'ASC' | 'DESC';
  
  /** Include bank accounts in response */
  include_bank_accounts?: boolean;
  
  /** Include bank account balances in response */
  include_bank_account_balances?: boolean;
}

/**
 * Query parameters for GET /api/bank-accounts
 */
export interface GetBankAccountsQueryParams {
  /** Filter by entity ID */
  entity_id?: number;
  
  /** Filter by entity IDs (array) */
  entity_ids?: number[];
  
  /** Filter by bank ID */
  bank_id?: number;
  
  /** Filter by bank IDs (array) */
  bank_ids?: number[];
  
  /** Filter by account name */
  account_name?: string;
  
  /** Filter by account names (array) */
  account_names?: string[];
  
  /** Filter by currency */
  currency?: Currency;
  
  /** Filter by currencies (array) */
  currencies?: Currency[];
  
  /** Filter by account type */
  account_type?: BankAccountType;
  
  /** Filter by account types (array) */
  account_types?: BankAccountType[];
  
  /** Filter by account status */
  status?: BankAccountStatus;
  
  /** Filter by account statuses (array) */
  statuses?: BankAccountStatus[];
  
  /** Sort by field */
  sort_by?: string;
  
  /** Sort order */
  sort_order?: 'ASC' | 'DESC';
  
  /** Include bank details in response */
  include_bank?: boolean;
  
  /** Include entity details in response */
  include_entity?: boolean;
  
  /** Include bank account balances in response */
  include_bank_account_balances?: boolean;
}

/**
 * Query parameters for GET /api/bank-account-balances
 */
export interface GetBankAccountBalancesQueryParams {
  /** Filter by bank account ID */
  bank_account_id?: number;
  
  /** Filter by bank account IDs (array) */
  bank_account_ids?: number[];
  
  /** Filter by currency */
  currency?: Currency;
  
  /** Filter by currencies (array) */
  currencies?: Currency[];
  
  /** Filter by start date */
  start_date?: string;
  
  /** Filter by end date */
  end_date?: string;
  
  /** Sort by field */
  sort_by?: string;
  
  /** Sort order */
  sort_order?: 'ASC' | 'DESC';
  
  /** Include bank account details in response */
  include_bank_account?: boolean;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial bank for list views (minimal data)
 */
export type BankSummary = Pick<Bank, 'id' | 'name' | 'country' | 'bank_type' | 'status'>;

/**
 * Partial bank account for list views (minimal data)
 */
export type BankAccountSummary = Pick<BankAccount, 'id' | 'account_name' | 'account_number' | 'currency' | 'status' | 'current_balance'>;

/**
 * Bank with accounts (for detail views)
 */
export type BankWithAccounts = Bank & Required<Pick<Bank, 'bank_accounts'>>;

/**
 * Bank account with balances (for detail views)
 */
export type BankAccountWithBalances = BankAccount & Required<Pick<BankAccount, 'bank_account_balances'>>;
