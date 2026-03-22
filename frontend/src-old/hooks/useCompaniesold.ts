// Company-specific Custom Hooks
// This file provides hooks for company-related API operations

import { api } from '../services/api/index';
import { useApiCall, useMutation, useApiCallWithDeps } from './useApiCallold';
import { Company } from '../types/models/company';
import { CreateCompanyRequest } from '../types/models/company';
import { CompanyOverviewResponse, CompanyDetailsResponse, EnhancedFundsResponse } from '../types/api';
import { useCallback } from 'react';

// ============================================================================
// TRANSFORMER FUNCTIONS
// ============================================================================

/**
 * Transform Fund to EnhancedFund format
 * Maps refactored Fund model to legacy EnhancedFund interface
 */
function transformToEnhancedFund(fund: any): any {
  return {
    id: fund.id,
    name: fund.name,
    description: fund.description,
    currency: fund.currency,
    fund_type: fund.fund_investment_type, // Map fund_investment_type to fund_type
    status: fund.status,
    tracking_type: fund.tracking_type,
    
    // Dates
    start_date: fund.start_date,
    end_date: fund.end_date,
    current_duration: fund.current_duration,
    created_at: fund.created_at,
    updated_at: fund.updated_at,
    
    // Investment details
    company_id: fund.company_id,
    entity_id: fund.entity_id,
    commitment_amount: fund.commitment_amount,
    expected_irr: fund.expected_irr,
    expected_duration_months: fund.expected_duration_months,
    
    // Equity and performance
    current_equity_balance: fund.current_equity_balance,
    average_equity_balance: fund.average_equity_balance,
    total_cost_basis: fund.total_cost_basis,
    current_units: fund.current_units,
    current_unit_price: fund.current_unit_price,
    current_nav_total: fund.current_nav_total,
  };
}

/**
 * Transform flat Company object to CompanyOverviewResponse structure
 * Maps calculated fields from refactored backend to expected frontend format
 */
function transformToOverviewResponse(company: Company): CompanyOverviewResponse {
  return {
    company: {
      id: company.id,
      name: company.name,
      company_type: company.company_type || null,
      business_address: company.business_address || null,
      website: company.website || null,
      contacts: (company.contacts || []).map(contact => ({
        id: contact.id,
        name: contact.name,
        title: contact.title ?? null,
        direct_number: contact.direct_number ?? null,
        direct_email: contact.direct_email ?? null,
        notes: contact.notes ?? null,
      })),
    },
    portfolio_summary: {
      total_committed_capital: company.total_commitment_amount || 0,
      total_current_value: company.current_equity_balance || 0,
      total_invested_capital: company.current_equity_balance || 0, // Same as current value for now
      active_funds_count: company.total_funds_active || 0,
      completed_funds_count: company.total_funds_completed || 0,
      fund_status_breakdown: {
        active_funds_count: company.total_funds_active || 0,
        completed_funds_count: company.total_funds_completed || 0,
        suspended_funds_count: 0, // Not tracked in current model
        realized_funds_count: company.total_funds_realized || 0,
      },
    },
    performance_summary: {
      average_completed_irr: company.completed_irr_gross ?? null,
      total_realized_gains: company.realized_pnl && company.realized_pnl > 0 ? company.realized_pnl : null,
      total_realized_losses: company.realized_pnl && company.realized_pnl < 0 ? Math.abs(company.realized_pnl) : null,
    },
    last_activity: {
      last_activity_date: company.updated_at || null,
      days_since_last_activity: company.updated_at 
        ? Math.floor((Date.now() - new Date(company.updated_at).getTime()) / (1000 * 60 * 60 * 24))
        : null,
    },
  };
}

/**
 * Transform flat Company object to CompanyDetailsResponse structure
 */
function transformToDetailsResponse(company: Company): CompanyDetailsResponse {
  return {
    company: {
      id: company.id,
      name: company.name,
      company_type: company.company_type || null,
      business_address: company.business_address || null,
      website: company.website || null,
      contacts: (company.contacts || []).map(contact => ({
        id: contact.id,
        name: contact.name,
        title: contact.title ?? null,
        direct_number: contact.direct_number ?? null,
        direct_email: contact.direct_email ?? null,
        notes: contact.notes ?? null,
      })),
    },
  };
}

// ============================================================================
// COMPANIES HOOKS
// ============================================================================

/**
 * Hook to get all companies
 * 
 * Returns company list with summary data including calculated fields.
 * New API returns { companies: Company[], count: number } but we extract just the companies array.
 */
export function useCompanies(options?: { refetchOnWindowFocus?: boolean }) {
  const getCompanies = useCallback(async () => {
    const response = await api.Companies.getCompanies();
    // Extract companies array from response { companies: Company[], count: number }
    return response.companies;
  }, []);
  
  const result = useApiCall(
    getCompanies,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
  
  return result;
}

/**
 * Hook to create a new company
 */
export function useCreateCompany() {
  const result = useMutation<CreateCompanyRequest, Company>(
    (data) => {
      return api.Companies.createCompany(data);
    }
  );
  
  return result;
}

/**
 * Hook to get funds for a specific company
 * 
 * Uses the standard GET /api/funds endpoint with company_id filter.
 */
export function useCompanyFunds(companyId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    async (companyId: number) => {
      const funds = await api.funds.getFunds({ company_id: companyId });
      return { company: { id: companyId, name: '' }, funds };
    },
    [companyId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

// ============================================================================
// ENHANCED COMPANIES UI HOOKS
// ============================================================================

/**
 * Hook to get company overview data for the Overview tab
 * 
 * Uses the standard GET /api/companies/:id endpoint which now returns
 * all calculated fields, then transforms to expected CompanyOverviewResponse format.
 */
export function useCompanyOverview(companyId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    async (companyId: number) => {
      const company = await api.Companies.getCompany(companyId, { include_contacts: true });
      return transformToOverviewResponse(company);
    },
    [companyId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get enhanced funds data for the Funds tab
 * 
 * Uses the standard GET /api/funds endpoint with company_id filter
 * instead of the legacy /enhanced endpoint.
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
    async (companyId: number, params: any) => {
      // Map frontend params to backend API params
      const apiParams: any = {
        company_id: companyId,
      };
      
      // Map status filter
      if (params.status_filter && params.status_filter !== 'all') {
        apiParams.fund_status = params.status_filter.toUpperCase();
      }
      
      // Map sort parameters
      if (params.sort_by) {
        apiParams.sort_by = params.sort_by.toUpperCase();
      }
      if (params.sort_order) {
        apiParams.sort_order = params.sort_order.toUpperCase();
      }
      
      // Get funds using new API (returns Fund[] directly)
      const funds = await api.funds.getFunds(apiParams);
      
      // Transform to match expected EnhancedFundsResponse format
      return {
        funds: funds.map(transformToEnhancedFund),
        filters: {
          applied_status_filter: params.status_filter || 'all',
          applied_search: params.search || null,
        },
      };
    },
    [companyId, params],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get company details for the Company Details tab
 * 
 * Uses the standard GET /api/companies/:id endpoint which now returns
 * all calculated fields, then transforms to expected CompanyDetailsResponse format.
 */
export function useCompanyDetails(companyId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    async (companyId: number) => {
      const company = await api.Companies.getCompany(companyId, { include_contacts: true });
      return transformToDetailsResponse(company);
    },
    [companyId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
} 