/**
 * Bank Account Balance Hooks - CRUD operations for bank account balances
 * 
 * Maps 1:1 to banking.api.ts balance methods and backend balance endpoints
 * 
 * @module bank/hooks/useBankAccountBalances
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { bankingApi } from '../api';
import type {
  BankAccountBalance,
  GetBankAccountBalancesResponse,
  GetBankAccountBalanceResponse,
  GetBankAccountBalancesQueryParams,
  CreateBankAccountBalanceRequest,
} from '../types';

// ============================================================================
// BANK ACCOUNT BALANCE QUERIES
// ============================================================================

/**
 * Get all bank account balances with optional filters
 * Maps to: GET /api/bank-account-balances
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with balances and count
 * 
 * @example
 * ```typescript
 * const { data, loading } = useBankAccountBalances({ 
 *   bank_account_id: 5,
 *   start_balance_date: '2024-01-01'
 * });
 * ```
 */
export function useBankAccountBalances(
  params?: GetBankAccountBalancesQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => bankingApi.getBankAccountBalances(params),
    [params]
  );
  
  return useQuery<GetBankAccountBalancesResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get all balances for a specific bank account
 * Maps to: GET /api/banks/:id/bank-accounts/:id/bank-account-balances
 * 
 * @param bankId - Bank ID
 * @param bankAccountId - Bank Account ID
 * @param options - Hook options
 * @returns Query result with balances
 * 
 * @example
 * ```typescript
 * const { data: balances, loading } = useBankAccountBalancesByAccount(
 *   bankId, 
 *   accountId
 * );
 * ```
 */
export function useBankAccountBalancesByAccount(
  bankId: number,
  bankAccountId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => bankingApi.getBankAccountBalancesByBankAccount(bankId, bankAccountId),
    [bankId, bankAccountId]
  );
  
  return useQuery<GetBankAccountBalancesResponse>(queryFn, {
    enabled: bankId > 0 && bankAccountId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a specific bank account balance by ID
 * Maps to: GET /api/banks/:id/bank-accounts/:id/bank-account-balances/:id
 * 
 * @param bankId - Bank ID
 * @param bankAccountId - Bank Account ID
 * @param balanceId - Balance ID
 * @param options - Hook options
 * @returns Query result with balance data
 * 
 * @example
 * ```typescript
 * const { data: balance, loading } = useBankAccountBalance(
 *   bankId, 
 *   accountId, 
 *   balanceId
 * );
 * ```
 */
export function useBankAccountBalance(
  bankId: number,
  bankAccountId: number,
  balanceId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => bankingApi.getBankAccountBalance(bankId, bankAccountId, balanceId),
    [bankId, bankAccountId, balanceId]
  );
  
  return useQuery<GetBankAccountBalanceResponse>(queryFn, {
    enabled: bankId > 0 && bankAccountId > 0 && balanceId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// BANK ACCOUNT BALANCE MUTATIONS
// ============================================================================

/**
 * Create a new bank account balance
 * Maps to: POST /api/banks/:id/bank-accounts/:id/bank-account-balances
 * 
 * @param bankId - Bank ID
 * @param bankAccountId - Bank Account ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createBalance, loading } = useCreateBankAccountBalance(
 *   bankId, 
 *   accountId
 * );
 * 
 * createBalance({
 *   balance_date: '2024-01-31',
 *   balance_amount: 125000.50,
 *   is_final: true
 * });
 * ```
 */
export function useCreateBankAccountBalance(
  bankId: number,
  bankAccountId: number
) {
  return useMutation<BankAccountBalance, CreateBankAccountBalanceRequest>(
    (data) => bankingApi.createBankAccountBalance(bankId, bankAccountId, data)
  );
}

/**
 * Delete a bank account balance
 * Maps to: DELETE /api/banks/:id/bank-accounts/:id/bank-account-balances/:id
 * 
 * @param bankId - Bank ID
 * @param bankAccountId - Bank Account ID
 * @param balanceId - Balance ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteBalance, loading } = useDeleteBankAccountBalance(
 *   bankId, 
 *   accountId, 
 *   balanceId
 * );
 * 
 * deleteBalance(undefined, {
 *   onSuccess: () => refetchBalances()
 * });
 * ```
 */
export function useDeleteBankAccountBalance(
  bankId: number,
  bankAccountId: number,
  balanceId: number
) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => bankingApi.deleteBankAccountBalance(bankId, bankAccountId, balanceId)
  );
}

