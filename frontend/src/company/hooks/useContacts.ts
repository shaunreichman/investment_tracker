/**
 * Contact Hooks - CRUD operations for company contacts
 * 
 * Maps 1:1 to companyApi.ts contact methods and backend contact endpoints
 * 
 * @module company/hooks/useContacts
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { companyApi } from '../api';
import type {
  Contact,
  GetContactsResponse,
  GetContactResponse,
  GetContactsQueryParams,
  CreateContactRequest,
} from '../types';

// ============================================================================
// CONTACT QUERIES
// ============================================================================

/**
 * Get all contacts with optional filters
 * Maps to: GET /api/contacts
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with contacts and count
 * 
 * @example
 * ```typescript
 * // Get all contacts
 * const { data, loading } = useContacts();
 * 
 * // Get contacts for a specific company
 * const { data, loading } = useContacts({ 
 *   company_id: 1,
 *   include_company: true
 * });
 * ```
 */
export function useContacts(
  params?: GetContactsQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => companyApi.getContacts(params), [params]);
  
  return useQuery<GetContactsResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get all contacts for a specific company
 * Maps to: GET /api/companies/:id/contacts
 * 
 * @param companyId - Company ID
 * @param options - Hook options
 * @returns Query result with contacts for the company
 * 
 * @example
 * ```typescript
 * const { data: contacts, loading } = useContactsByCompanyId(companyId);
 * ```
 */
export function useContactsByCompanyId(
  companyId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => companyApi.getContactsByCompanyId(companyId),
    [companyId]
  );
  
  return useQuery<GetContactsResponse>(queryFn, {
    enabled: companyId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a specific contact by ID
 * Maps to: GET /api/companies/:id/contacts/:id
 * 
 * @param companyId - Company ID
 * @param contactId - Contact ID
 * @param options - Hook options
 * @returns Query result with contact data
 * 
 * @example
 * ```typescript
 * const { data: contact, loading } = useContact(companyId, contactId);
 * ```
 */
export function useContact(
  companyId: number,
  contactId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => companyApi.getContact(companyId, contactId),
    [companyId, contactId]
  );
  
  return useQuery<GetContactResponse>(queryFn, {
    enabled: companyId > 0 && contactId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// CONTACT MUTATIONS
// ============================================================================

/**
 * Create a new contact for a company
 * Maps to: POST /api/companies/:id/contacts
 * 
 * @param companyId - Company ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createContact, loading } = useCreateContact(companyId);
 * 
 * createContact({
 *   name: 'John Smith',
 *   title: 'Managing Partner',
 *   direct_email: 'john.smith@acmecapital.com'
 * });
 * ```
 */
export function useCreateContact(companyId: number) {
  return useMutation<Contact, CreateContactRequest>(
    (data) => companyApi.createContact(companyId, data)
  );
}

/**
 * Delete a contact
 * Maps to: DELETE /api/companies/:id/contacts/:id
 * 
 * @param companyId - Company ID
 * @param contactId - Contact ID
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteContact, loading } = useDeleteContact(companyId, contactId);
 * 
 * deleteContact(undefined, {
 *   onSuccess: () => refetchContacts()
 * });
 * ```
 */
export function useDeleteContact(companyId: number, contactId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => companyApi.deleteContact(companyId, contactId)
  );
}

