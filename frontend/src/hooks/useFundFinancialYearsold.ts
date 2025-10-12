import { useState, useEffect } from 'react';
import { useErrorHandler } from './useErrorHandlerold';
import { getApiBaseUrl } from '../config/environment';

/**
 * Custom hook to fetch financial years for a specific fund.
 * 
 * This hook provides enterprise-grade financial year management by:
 * - Fetching financial years from fund start date to current date
 * - Handling loading states and error conditions
 * - Providing real-time data from the backend
 * - Supporting proper error handling and user feedback
 * 
 * @param fundId - The ID of the fund to get financial years for
 * @returns Object containing financial years, loading state, and error handling
 */
export const useFundFinancialYears = (fundId: number | null) => {
  const [financialYears, setFinancialYears] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { setError } = useErrorHandler();

  useEffect(() => {
    if (!fundId) {
      setFinancialYears([]);
      return;
    }

    const fetchFinancialYears = async () => {
      setIsLoading(true);
      try {
        const url = `${getApiBaseUrl()}/api/funds/${fundId}/financial-years`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
          if (response.status === 404) {
            // Fund not found - this is a valid business case
            setFinancialYears([]);
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setFinancialYears(data.financial_years || []);
      } catch (error) {
        console.error('Error fetching financial years:', error);
        setError('Failed to fetch financial years');
        // Fallback to empty array on error
        setFinancialYears([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFinancialYears();
  }, [fundId, setError]);

  return {
    financialYears,
    isLoading,
    // Helper method to check if we have financial years
    hasFinancialYears: financialYears.length > 0,
    // Helper method to get the most recent financial year
    mostRecentFinancialYear: financialYears[0] || null
  };
};
