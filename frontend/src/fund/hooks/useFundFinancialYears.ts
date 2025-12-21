/**
 * Fund Financial Years Query Hook
 *
 * Maps 1:1 to fundApi method and backend /api/funds/:id/financial-years endpoint
 *
 * @module fund/hooks/useFundFinancialYears
 */

import { useCallback, useMemo } from 'react';
import { useQuery, type UseQueryResult } from '@/shared/hooks/core';
import { fundApi } from '../api';
import type { FundFinancialYearMap, FundFinancialYear } from '../types';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Result returned from useFundFinancialYears hook
 */
export interface UseFundFinancialYearsResult extends UseQueryResult<FundFinancialYearMap> {
  /** Financial year data as map (defaults to empty object when not loaded) */
  financialYearMap: FundFinancialYearMap;
  /** Financial year data as sorted array for UI consumption */
  financialYears: FundFinancialYear[];
  /** Convenience list of financial year labels */
  financialYearLabels: string[];
  /** Whether at least one financial year exists */
  hasFinancialYears: boolean;
  /** Most recent financial year entry or null if none available */
  mostRecentFinancialYear: FundFinancialYear | null;
}

// ============================================================================
// FUND FINANCIAL YEARS QUERY
// ============================================================================

/**
 * Get financial years for a specific fund
 * Maps to: GET /api/funds/:id/financial-years
 *
 * Returns a mapping of financial year labels to their final calendar dates.
 * Provides derived structures for UI consumption (array, labels, latest year).
 *
 * @param fundId - Fund ID
 * @param options - Hook options
 * @returns Query result with financial year map and derived helpers
 *
 * @example
 * ```typescript
 * const {
 *   financialYears,
 *   financialYearLabels,
 *   mostRecentFinancialYear,
 * } = useFundFinancialYears(fundId);
 *
 * // In a select dropdown
 * {financialYears.map(({ financialYear }) => (
 *   <option key={financialYear} value={financialYear}>
 *     {financialYear}
 *   </option>
 * ))}
 * ```
 */
export function useFundFinancialYears(
  fundId: number,
  options?: { refetchOnWindowFocus?: boolean }
): UseFundFinancialYearsResult {
  const queryFn = useCallback(
    () => fundApi.getFundFinancialYears(fundId),
    [fundId]
  );

  const queryResult = useQuery<FundFinancialYearMap>(queryFn, {
    enabled: fundId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });

  const financialYears = useMemo<FundFinancialYear[]>(() => {
    if (!queryResult.data) {
      return [];
    }

    return Object.entries(queryResult.data)
      .map(([financialYear, finalDate]) => ({
        financialYear,
        finalDate,
      }))
      .sort((a, b) => Number(b.financialYear) - Number(a.financialYear));
  }, [queryResult.data]);

  const financialYearMap = queryResult.data ?? {};
  const financialYearLabels = useMemo(
    () => financialYears.map((entry) => entry.financialYear),
    [financialYears]
  );
  const hasFinancialYears = financialYears.length > 0;
  const mostRecentFinancialYear = hasFinancialYears ? financialYears[0]! : null;

  return {
    ...queryResult,
    data: queryResult.data ?? null,
    financialYearMap,
    financialYears,
    financialYearLabels,
    hasFinancialYears,
    mostRecentFinancialYear,
  };
}