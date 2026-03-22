/**
 * Bank Hooks - CRUD operations for banks
 * 
 * Maps 1:1 to bank.api.ts bank methods and backend /api/banks endpoints
 * 
 * @module bank/hooks/useBanks
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { bankingApi } from '../api';
import type {
  Bank,
  GetBanksResponse,
  GetBankResponse,
  GetBanksQueryParams,
  CreateBankRequest,
} from '../types';

// ============================================================================
// BANK QUERIES
// ============================================================================

/**
 * Get all banks with optional filters
 * Maps to: GET /api/banks
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with banks and count
 * 
 * @example
 * ```typescript
 * const { data, loading } = useBanks();
 * ```
 */
export function useBanks(
  params?: GetBanksQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => bankingApi.getBanks(params), [params]);
  
  return useQuery<GetBanksResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a single bank by ID
 * Maps to: GET /api/banks/:id
 * 
 * @param bankId - Bank ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with bank data
 * 
 * @example
 * ```typescript
 * const { data: bank, loading } = useBank(bankId, { 
 *   include_bank_accounts: true 
 * });
 * ```
 */
export function useBank(
  bankId: number,
  params?: {
    include_bank_accounts?: boolean;
    include_bank_account_balances?: boolean;
  },
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => bankingApi.getBank(bankId, params),
    [bankId, params]
  );
  
  return useQuery<Bank>(queryFn, {
    enabled: bankId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// BANK MUTATIONS
// ============================================================================

/**
 * Create a new bank
 * Maps to: POST /api/banks
 * 
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createBank, loading } = useCreateBank();
 * 
 * createBank({
 *   name: 'Commonwealth Bank',
 *   country: Country.AU,
 *   bank_type: BankType.COMMERCIAL
 * });
 * ```
 */
export function useCreateBank() {
  return useMutation<Bank, CreateBankRequest>(
    (data) => bankingApi.createBank(data)
  );
}

/**
 * Delete a bank
 * Maps to: DELETE /api/banks/:id
 * 
 * @param bankId - Bank ID to delete
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteBank, loading } = useDeleteBank(bankId);
 * 
 * deleteBank(undefined, {
 *   onSuccess: () => navigate('/banks')
 * });
 * ```
 */
export function useDeleteBank(bankId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => bankingApi.deleteBank(bankId)
  );
}

