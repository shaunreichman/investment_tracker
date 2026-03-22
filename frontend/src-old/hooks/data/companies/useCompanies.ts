/**
 * Company Hooks - CRUD operations for companies
 * 
 * Maps 1:1 to company.api.ts methods and backend /api/companies endpoints
 * 
 * @module hooks/data/companies/useCompanies
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  Company,
  GetCompaniesResponse,
  GetCompaniesQueryParams,
  CreateCompanyRequest,
} from '@/types/models/company';

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
  const queryFn = useCallback(() => api.Companies.getCompanies(params), [params]);
  
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
    () => api.Companies.getCompany(companyId, params),
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
    (data) => api.Companies.createCompany(data)
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
    () => api.Companies.deleteCompany(companyId)
  );
}

