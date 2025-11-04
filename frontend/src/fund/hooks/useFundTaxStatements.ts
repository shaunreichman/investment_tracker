/**
 * Fund Tax Statement Hooks - CRUD operations for fund tax statements
 * 
 * Maps 1:1 to fundApi tax statement methods and backend tax statement endpoints
 * 
 * @module fund/hooks/useFundTaxStatements
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { fundApi } from '../api';
import type {
  FundTaxStatement,
  GetFundTaxStatementsResponse,
  GetFundTaxStatementResponse,
  GetFundTaxStatementsQueryParams,
  CreateFundTaxStatementRequest,
} from '../types';

// ============================================================================
// TAX STATEMENT QUERIES
// ============================================================================

/**
 * Get all fund tax statements with optional filters
 * Maps to: GET /api/fund-tax-statements
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with array of tax statements
 * 
 * @example
 * ```typescript
 * // Get all tax statements for FY 2024
 * const { data, loading } = useFundTaxStatements({ 
 *   financial_year: '2024' 
 * });
 * ```
 */
export function useFundTaxStatements(
  params?: GetFundTaxStatementsQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => fundApi.getFundTaxStatements(params),
    [params]
  );
  
  return useQuery<GetFundTaxStatementsResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get all tax statements for a specific fund
 * Maps to: GET /api/funds/:id/fund-tax-statements
 * 
 * @param fundId - Fund ID
 * @param options - Hook options
 * @returns Query result with array of tax statements
 * 
 * @example
 * ```typescript
 * const { data: statements, loading } = useFundTaxStatementsByFundId(fundId);
 * ```
 */
export function useFundTaxStatementsByFundId(
  fundId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => fundApi.getFundTaxStatementsByFundId(fundId),
    [fundId]
  );
  
  return useQuery<GetFundTaxStatementsResponse>(queryFn, {
    enabled: fundId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a specific fund tax statement
 * Maps to: GET /api/funds/:id/fund-tax-statements/:id
 * 
 * @param fundId - Fund ID
 * @param fundTaxStatementId - Tax Statement ID
 * @param options - Hook options
 * @returns Query result with tax statement
 * 
 * @example
 * ```typescript
 * const { data: statement, loading } = useFundTaxStatement(fundId, statementId);
 * ```
 */
export function useFundTaxStatement(
  fundId: number,
  fundTaxStatementId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => fundApi.getFundTaxStatement(fundId, fundTaxStatementId),
    [fundId, fundTaxStatementId]
  );
  
  return useQuery<GetFundTaxStatementResponse>(queryFn, {
    enabled: fundId > 0 && fundTaxStatementId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// TAX STATEMENT MUTATIONS
// ============================================================================

/**
 * Create a new fund tax statement
 * Maps to: POST /api/funds/:id/fund-tax-statements
 * 
 * @param fundId - Fund ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createTaxStatement } = useCreateFundTaxStatement(fundId);
 * 
 * createTaxStatement({
 *   entity_id: 2,
 *   financial_year: '2024',
 *   tax_payment_date: '2024-10-31',
 *   interest_income_tax_rate: 30.0,
 *   interest_received_in_cash: 15000,
 *   accountant: 'Smith & Co'
 * });
 * ```
 */
export function useCreateFundTaxStatement(fundId: number) {
  return useMutation<FundTaxStatement, CreateFundTaxStatementRequest>(
    (data) => fundApi.createFundTaxStatement(fundId, data)
  );
}

/**
 * Delete a fund tax statement
 * Maps to: DELETE /api/funds/:id/fund-tax-statements/:id
 * 
 * @param fundId - Fund ID
 * @param fundTaxStatementId - Tax Statement ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteStatement } = useDeleteFundTaxStatement(fundId, statementId);
 * 
 * deleteStatement(undefined, {
 *   onSuccess: () => refetchStatements()
 * });
 * ```
 */
export function useDeleteFundTaxStatement(
  fundId: number,
  fundTaxStatementId: number
) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => fundApi.deleteFundTaxStatement(fundId, fundTaxStatementId)
  );
}

