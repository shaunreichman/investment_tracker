/**
 * Fund Financial Years Query Hook
 * 
 * Maps 1:1 to fundApi method and backend /api/funds/:id/financial-years endpoint
 * 
 * @module fund/hooks/useFundFinancialYears
 */

import { useCallback } from 'react';
import { useQuery } from '@/shared/hooks/core';
import { fundApi } from '../api';

// ============================================================================
// FUND FINANCIAL YEARS QUERY
// ============================================================================

/**
 * Get financial years for a specific fund
 * Maps to: GET /api/funds/:id/financial-years
 * 
 * Returns all financial years from the fund's start date to current date.
 * Used for tax statement forms and financial year filtering.
 * 
 * @param fundId - Fund ID
 * @param options - Hook options
 * @returns Query result with financial years array
 * 
 * @example
 * ```typescript
 * // Get financial years
 * const { data, loading } = useFundFinancialYears(fundId);
 * 
 * // In a select dropdown
 * {data?.map(year => <option key={year} value={year}>{year}</option>)}
 * ```
 */
export function useFundFinancialYears(
  fundId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => fundApi.getFundFinancialYears(fundId),
    [fundId]
  );
  
  return useQuery<string[]>(queryFn, {
    enabled: fundId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

