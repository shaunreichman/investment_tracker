/**
 * Bank Account Hooks - CRUD operations for bank accounts
 * 
 * Maps 1:1 to banking.api.ts bank account methods and backend bank account endpoints
 * 
 * @module bank/hooks/useBankAccounts
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { bankingApi } from '../api';
import type {
  BankAccount,
  GetBankAccountsResponse,
  GetBankAccountResponse,
  GetBankAccountsQueryParams,
  CreateBankAccountRequest,
} from '../types';

// ============================================================================
// BANK ACCOUNT QUERIES
// ============================================================================

/**
 * Get all bank accounts with optional filters
 * Maps to: GET /api/bank-accounts
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with bank accounts and count
 * 
 * @example
 * ```typescript
 * const { data, loading } = useBankAccounts({ 
 *   entity_id: 1,
 *   currency: Currency.AUD
 * });
 * ```
 */
export function useBankAccounts(
  params?: GetBankAccountsQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => bankingApi.getBankAccounts(params), [params]);
  
  return useQuery<GetBankAccountsResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get all bank accounts for a specific bank
 * Maps to: GET /api/banks/:id/bank-accounts
 * 
 * @param bankId - Bank ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with bank accounts
 * 
 * @example
 * ```typescript
 * const { data: accounts, loading } = useBankAccountsByBankId(bankId);
 * ```
 */
export function useBankAccountsByBankId(
  bankId: number,
  params?: { include_bank_account_balances?: boolean },
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => bankingApi.getBankAccountsByBankId(bankId, params),
    [bankId, params]
  );
  
  return useQuery<GetBankAccountsResponse>(queryFn, {
    enabled: bankId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a specific bank account by ID
 * Maps to: GET /api/banks/:id/bank-accounts/:id
 * 
 * @param bankId - Bank ID
 * @param bankAccountId - Bank Account ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with bank account data
 * 
 * @example
 * ```typescript
 * const { data: account, loading } = useBankAccount(bankId, accountId, {
 *   include_bank_account_balances: true
 * });
 * ```
 */
export function useBankAccount(
  bankId: number,
  bankAccountId: number,
  params?: { include_bank_account_balances?: boolean },
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => bankingApi.getBankAccount(bankId, bankAccountId, params),
    [bankId, bankAccountId, params]
  );
  
  return useQuery<GetBankAccountResponse>(queryFn, {
    enabled: bankId > 0 && bankAccountId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// BANK ACCOUNT MUTATIONS
// ============================================================================

/**
 * Create a new bank account for a bank
 * Maps to: POST /api/banks/:id/bank-accounts
 * 
 * @param bankId - Bank ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createAccount, loading } = useCreateBankAccount(bankId);
 * 
 * createAccount({
 *   entity_id: 1,
 *   account_name: 'Savings Account',
 *   account_number: '12345678',
 *   currency: Currency.AUD
 * });
 * ```
 */
export function useCreateBankAccount(bankId: number) {
  return useMutation<BankAccount, CreateBankAccountRequest>(
    (data) => bankingApi.createBankAccount(bankId, data)
  );
}

/**
 * Delete a bank account
 * Maps to: DELETE /api/banks/:id/bank-accounts/:id
 * 
 * @param bankId - Bank ID
 * @param bankAccountId - Bank Account ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteAccount, loading } = useDeleteBankAccount(bankId, accountId);
 * 
 * deleteAccount(undefined, {
 *   onSuccess: () => refetchAccounts()
 * });
 * ```
 */
export function useDeleteBankAccount(bankId: number, bankAccountId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => bankingApi.deleteBankAccount(bankId, bankAccountId)
  );
}

