/**
 * Fund Financial Years Query Hook
 * 
 * @module hooks/data/funds
 */

import { useCallback } from 'react';
import { useQuery } from '@/hooks/core/api';
import { getApiBaseUrl } from '@/config/environment';

/**
 * Hook to fetch financial years for a specific fund
 * 
 * Fetches all financial years from the fund's start date to current date.
 * Used for tax statement forms and financial year filtering.
 * 
 * @param fundId - The ID of the fund
 * @returns Query result with financial years and helper properties
 * 
 * @example
 * ```typescript
 * const { data: years, loading, hasFinancialYears } = useFundFinancialYears(fundId);
 * 
 * // In a select dropdown
 * {years?.map(year => <option key={year} value={year}>{year}</option>)}
 * ```
 */
export function useFundFinancialYears(fundId: number | null) {
  const queryFn = useCallback(async () => {
    if (!fundId) return [];
    
    const url = `${getApiBaseUrl()}/api/funds/${fundId}/financial-years`;
    const response = await fetch(url);
    
    if (!response.ok) {
      if (response.status === 404) {
        // Fund not found - return empty array
        return [];
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.financial_years || [];
  }, [fundId]);

  const result = useQuery<string[]>(queryFn, {
    enabled: fundId !== null && fundId > 0,
  });

  return {
    financialYears: result.data || [],
    loading: result.loading,
    error: result.error,
    refetch: result.refetch,
    // Helper properties
    hasFinancialYears: (result.data?.length || 0) > 0,
    mostRecentFinancialYear: result.data?.[0] || null,
  };
}

