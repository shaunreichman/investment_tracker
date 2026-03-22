/**
 * Bank Account Domain Type Definitions
 * 
 * TypeScript interfaces matching backend banking models exactly.
 * Source: src/banking/models/bank_account.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { 
  BankAccountType, 
  BankAccountStatus 
} from './bankEnums';
import { Currency } from '@/shared/types';
import type { Bank } from './bank';
import type { BankAccountBalance } from './bankAccountBalance';

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
// REQUEST DTOs
// ============================================================================

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

// ============================================================================
// RESPONSE DTOs
// ============================================================================

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

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

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

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial bank account for list views (minimal data)
 */
export type BankAccountSummary = Pick<BankAccount, 'id' | 'account_name' | 'account_number' | 'currency' | 'status' | 'current_balance'>;

/**
 * Bank account with balances (for detail views)
 */
export type BankAccountWithBalances = BankAccount & Required<Pick<BankAccount, 'bank_account_balances'>>;

