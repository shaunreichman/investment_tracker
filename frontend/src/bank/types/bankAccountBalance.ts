/**
 * Bank Account Balance Domain Type Definitions
 * 
 * TypeScript interfaces matching backend banking models exactly.
 * Source: src/banking/models/bank_account_balance.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { Currency } from '@/shared/types';
import type { BankAccount } from './bankAccount';

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

