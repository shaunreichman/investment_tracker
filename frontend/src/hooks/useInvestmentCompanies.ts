// Investment Company-specific Custom Hooks
// This file provides hooks for investment company-related API operations

import { apiClient } from '../services/api';
import { useApiCall, useMutation, useApiCallWithDeps } from './useApiCall';
import {
  InvestmentCompany,
  InvestmentCompanyListResponse,
  CreateInvestmentCompanyData,
  FundListResponse,
} from '../types/api';
import { useCallback } from 'react';

// ============================================================================
// INVESTMENT COMPANIES HOOKS
// ============================================================================

/**
 * Hook to get all investment companies
 */
export function useInvestmentCompanies(options?: { refetchOnWindowFocus?: boolean }) {
  const getInvestmentCompanies = useCallback(() => apiClient.getInvestmentCompanies(), []);
  
  return useApiCall(
    getInvestmentCompanies,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to create a new investment company
 */
export function useCreateInvestmentCompany() {
  return useMutation<CreateInvestmentCompanyData, InvestmentCompany>(
    (data) => apiClient.createInvestmentCompany(data)
  );
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