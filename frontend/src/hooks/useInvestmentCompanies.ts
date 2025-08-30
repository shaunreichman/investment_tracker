// Investment Company-specific Custom Hooks
// This file provides hooks for investment company-related API operations

import { apiClient } from '../services/api';
import { useApiCall, useMutation, useApiCallWithDeps } from './useApiCall';
import { InvestmentCompany, CreateInvestmentCompanyData } from '../types/api';
import { useCallback } from 'react';
import React from 'react';

// ============================================================================
// INVESTMENT COMPANIES HOOKS
// ============================================================================

/**
 * Hook to get all investment companies
 */
export function useInvestmentCompanies(options?: { refetchOnWindowFocus?: boolean }) {
  console.log('🔍 useInvestmentCompanies hook called with options:', options);
  
  const getInvestmentCompanies = useCallback(() => {
    console.log('📡 useInvestmentCompanies: Making API call to getInvestmentCompanies');
    return apiClient.getInvestmentCompanies();
  }, []);
  
  const result = useApiCall(
    getInvestmentCompanies,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
  
  console.log('📊 useInvestmentCompanies hook result:', {
    data: result.data,
    loading: result.loading,
    error: result.error,
    refetch: typeof result.refetch
  });
  
  // Add effect to monitor refetch calls
  React.useEffect(() => {
    if (typeof result.refetch === 'function') {
      console.log('🔧 useInvestmentCompanies: refetch function is available');
    } else {
      console.warn('⚠️ useInvestmentCompanies: refetch function is undefined!');
    }
  }, [result.refetch]);
  
  return result;
}

/**
 * Hook to create a new investment company
 */
export function useCreateInvestmentCompany() {
  console.log('🔍 useCreateInvestmentCompany hook called');
  
  const result = useMutation<CreateInvestmentCompanyData, InvestmentCompany>(
    (data) => {
      console.log('📤 useCreateInvestmentCompany: Calling API with data:', data);
      return apiClient.createInvestmentCompany(data);
    }
  );
  
  console.log('📊 useCreateInvestmentCompany hook result:', {
    data: result.data,
    loading: result.loading,
    error: result.error,
    mutate: typeof result.mutate
  });
  
  return result;
}

/**
 * Hook to get funds for a specific company
 */
export function useCompanyFunds(companyId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (companyId: number) => apiClient.getCompanyFunds(companyId),
    [companyId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

// ============================================================================
// ENHANCED COMPANIES UI HOOKS
// ============================================================================

/**
 * Hook to get company overview data for the Overview tab
 */
export function useCompanyOverview(companyId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (companyId: number) => apiClient.getCompanyOverview(companyId),
    [companyId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get enhanced funds data for the Funds tab
 */
export function useEnhancedFunds(
  companyId: number,
  params: {
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    status_filter?: 'all' | 'active' | 'completed' | 'suspended';
    search?: string;
    page?: number;
    per_page?: number;
  } = {},
  options?: { refetchOnWindowFocus?: boolean }
) {
  return useApiCallWithDeps(
    (companyId: number, params: any) => apiClient.getEnhancedFunds(companyId, params),
    [companyId, params],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get company details for the Company Details tab
 */
export function useCompanyDetails(companyId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (companyId: number) => apiClient.getCompanyDetails(companyId),
    [companyId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
} 