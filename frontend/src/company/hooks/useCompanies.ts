/**
 * Company Hooks - CRUD operations for companies
 * 
 * Maps 1:1 to companyApi.ts methods and backend /api/companies endpoints
 * 
 * @module company/hooks/useCompanies
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { companyApi } from '../api';
import type {
  Company,
  GetCompaniesResponse,
  GetCompaniesQueryParams,
  CreateCompanyRequest,
  CompanyOverviewResponse,
  CompanyDetailsResponse,
} from '../types';

// ============================================================================
// COMPANY QUERIES
// ============================================================================

/**
 * Get all companies with optional filters
 * Maps to: GET /api/companies
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with companies and count
 * 
 * @example
 * ```typescript
 * // Get all companies
 * const { data, loading } = useCompanies();
 * 
 * // Get filtered companies
 * const { data, loading } = useCompanies({ 
 *   company_type: CompanyType.PRIVATE_EQUITY,
 *   sort_by: SortFieldCompany.NAME
 * });
 * ```
 */
export function useCompanies(
  params?: GetCompaniesQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => companyApi.getCompanies(params), [params]);
  
  return useQuery<GetCompaniesResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a single company by ID with all calculated fields
 * Maps to: GET /api/companies/:id
 * 
 * @param companyId - Company ID
 * @param params - Query parameters for including relationships
 * @param options - Hook options
 * @returns Query result with company data
 * 
 * @example
 * ```typescript
 * // Get company with contacts
 * const { data: company, loading } = useCompany(companyId, { 
 *   include_contacts: true 
 * });
 * ```
 */
export function useCompany(
  companyId: number,
  params?: { include_contacts?: boolean },
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => companyApi.getCompany(companyId, params),
    [companyId, params]
  );
  
  return useQuery<Company>(queryFn, {
    enabled: companyId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// COMPANY MUTATIONS
// ============================================================================

/**
 * Create a new company
 * Maps to: POST /api/companies
 * 
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createCompany, loading } = useCreateCompany();
 * 
 * createCompany({
 *   name: 'Acme Capital Partners',
 *   company_type: CompanyType.PRIVATE_EQUITY,
 *   description: 'Leading PE firm',
 *   website: 'https://acmecapital.com'
 * });
 * ```
 */
export function useCreateCompany() {
  return useMutation<Company, CreateCompanyRequest>(
    (data) => companyApi.createCompany(data)
  );
}

/**
 * Delete a company
 * Maps to: DELETE /api/companies/:id
 * 
 * @param companyId - Company ID to delete
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteCompany, loading } = useDeleteCompany(companyId);
 * 
 * deleteCompany(undefined, {
 *   onSuccess: () => navigate('/companies')
 * });
 * ```
 */
export function useDeleteCompany(companyId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => companyApi.deleteCompany(companyId)
  );
}

// ============================================================================
// COMPANY UI HOOKS (Transformed Responses)
// ============================================================================

/**
 * Transform flat Company object to CompanyOverviewResponse structure
 * Maps calculated fields from backend to expected frontend format
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

/**
 * Hook to get company overview data for the Overview tab
 * 
 * Uses the standard GET /api/companies/:id endpoint which returns
 * all calculated fields, then transforms to expected CompanyOverviewResponse format.
 * 
 * @param companyId - Company ID
 * @param options - Hook options
 * @returns Query result with transformed overview data
 * 
 * @example
 * ```typescript
 * const { data: overviewData, loading } = useCompanyOverview(companyId);
 * ```
 */
export function useCompanyOverview(
  companyId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(async () => {
    const company = await companyApi.getCompany(companyId, { include_contacts: true });
    return transformToOverviewResponse(company);
  }, [companyId]);
  
  return useQuery<CompanyOverviewResponse>(queryFn, {
    enabled: companyId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Hook to get company details for the Company Details tab
 * 
 * Uses the standard GET /api/companies/:id endpoint which returns
 * all calculated fields, then transforms to expected CompanyDetailsResponse format.
 * 
 * @param companyId - Company ID
 * @param options - Hook options
 * @returns Query result with transformed details data
 * 
 * @example
 * ```typescript
 * const { data: detailsData, loading } = useCompanyDetails(companyId);
 * ```
 */
export function useCompanyDetails(
  companyId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(async () => {
    const company = await companyApi.getCompany(companyId, { include_contacts: true });
    return transformToDetailsResponse(company);
  }, [companyId]);
  
  return useQuery<CompanyDetailsResponse>(queryFn, {
    enabled: companyId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

