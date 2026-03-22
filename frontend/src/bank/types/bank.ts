/**
 * Bank Domain Type Definitions
 * 
 * TypeScript interfaces matching backend banking models exactly.
 * Source: src/banking/models/bank.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { 
  BankType, 
  BankStatus
} from './bankEnums';
import { Country } from '@/shared/types';
import type { BankAccount } from './bankAccount';

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
export type GetBankResponse = Bank;

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

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial bank for list views (minimal data)
 */
export type BankSummary = Pick<Bank, 'id' | 'name' | 'country' | 'bank_type' | 'status'>;

/**
 * Bank with accounts (for detail views)
 */
export type BankWithAccounts = Bank & Required<Pick<Bank, 'bank_accounts'>>;

