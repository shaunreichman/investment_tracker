/**
 * Banking Domain Types Barrel Export
 * 
 * Centralized export of all banking domain types.
 * 
 * Usage:
 *   import { Bank, BankAccount, CreateBankRequest } from '@/bank/types';
 */

// Bank types
export type {
  // Core models
  Bank,
  
  // Request DTOs
  CreateBankRequest,
  
  // Response DTOs
  GetBanksResponse,
  GetBankResponse,
  
  // Query parameters
  GetBanksQueryParams,
  
  // Utility types
  BankSummary,
  BankWithAccounts
} from './bank';

// Bank account types
export type {
  // Core models
  BankAccount,
  
  // Request DTOs
  CreateBankAccountRequest,
  
  // Response DTOs
  GetBankAccountsResponse,
  GetBankAccountResponse,
  
  // Query parameters
  GetBankAccountsQueryParams,
  
  // Utility types
  BankAccountSummary,
  BankAccountWithBalances
} from './bankAccount';

// Bank account balance types
export type {
  // Core models
  BankAccountBalance,
  
  // Request DTOs
  CreateBankAccountBalanceRequest,
  
  // Response DTOs
  GetBankAccountBalancesResponse,
  GetBankAccountBalanceResponse,
  
  // Query parameters
  GetBankAccountBalancesQueryParams
} from './bankAccountBalance';

// Re-export enums from enums.ts
export {
  // Bank enums
  BankType,
  BankStatus,
  SortFieldBank,
  
  // Bank account enums
  BankAccountType,
  BankAccountStatus,
  SortFieldBankAccount,
  
  // Bank account balance enums
  SortFieldBankAccountBalance,
} from './bankEnums';

