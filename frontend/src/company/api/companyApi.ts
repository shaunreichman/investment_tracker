/**
 * Company API
 * 
 * All company-related API methods including:
 * - Companies (CRUD operations)
 * - Contacts (CRUD operations)
 * 
 * Companies manage funds and have associated contacts.
 */

import { ApiClient } from '@/shared/api';
import {
  Company,
  Contact,
  CreateCompanyRequest,
  CreateContactRequest,
  GetCompaniesResponse,
  GetCompanyResponse,
  GetContactsResponse,
  GetContactResponse,
  GetCompaniesQueryParams,
  GetContactsQueryParams
} from '@/company/types';

export class CompanyApi {
  constructor(private client: ApiClient) {}

  // ============================================================================
  // COMPANIES
  // ============================================================================

  /**
   * Get all companies with optional filters.
   * 
   * Supports filtering by:
   * - name (single) or names (multiple)
   * - company_type (single) or company_types (multiple)
   * - status (single) or statuses (multiple)
   * 
   * Supports sorting by: NAME, STATUS, START_DATE, CREATED_AT, UPDATED_AT
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Response with companies and count
   * 
   * @example
   * ```typescript
   * // Get all companies
   * const response = await api.companies.getCompanies();
   * 
   * // Get all PRIVATE_EQUITY companies
   * const peCompanies = await api.companies.getCompanies({
   *   company_type: CompanyType.PRIVATE_EQUITY
   * });
   * 
   * // Get companies sorted by name
   * const sortedCompanies = await api.companies.getCompanies({
   *   sort_by: SortFieldCompany.NAME,
   *   sort_order: SortOrder.ASC
   * });
   * ```
   */
  async getCompanies(params: GetCompaniesQueryParams = {}): Promise<GetCompaniesResponse> {
    return this.client.get<GetCompaniesResponse>('/api/companies', params);
  }

  /**
   * Get a single company by ID with comprehensive data.
   * 
   * This endpoint returns all company data including:
   * - Basic info (name, type, address, website)
   * - Fund statistics (total_funds, active, completed, realized)
   * - Financial metrics (equity balances, IRR, PNL)
   * - Status and timeline (status, start_date, end_date, duration)
   * - Optionally: contacts
   * 
   * @param companyId The ID of the company to retrieve
   * @param params Optional parameters to include related entities
   * @returns Company object with all calculated fields
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if company doesn't exist
   * 
   * @example
   * ```typescript
   * // Get company with all data
   * const response = await api.Companies.getCompany(1);
   * const company = response.company;
   * 
   * // Get company with contacts included
   * const withContacts = await api.Companies.getCompany(1, {
   *   include_contacts: true
   * });
   * ```
   */
  async getCompany(
    companyId: number,
    params: {
      include_contacts?: boolean;
    } = {}
  ): Promise<Company> {
    // Backend returns { success: true, data: company } which gets unwrapped to just company
    return this.client.get<Company>(`/api/companies/${companyId}`, params);
  }

  /**
   * Create a new company.
   * 
   * Required fields:
   * - name: Company name (unique)
   * 
   * Optional fields:
   * - description: Company description
   * - company_type: Type of company
   * - business_address: Business address
   * - website: Company website URL
   * 
   * @param data Company creation data
   * @returns Created company object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with BUSINESS_LOGIC_ERROR if company name already exists
   * 
   * @example
   * ```typescript
   * const newCompany = await api.companies.createCompany({
   *   name: 'Acme Capital Partners',
   *   company_type: CompanyType.PRIVATE_EQUITY,
   *   description: 'Leading PE firm focused on tech investments',
   *   website: 'https://acmecapital.com'
   * });
   * ```
   */
  async createCompany(data: CreateCompanyRequest): Promise<Company> {
    return this.client.post<Company>('/api/companies', data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/companies/<id>, add updateCompany() method here

  /**
   * Delete an company.
   * 
   * Warning: This will cascade delete all related data:
   * - Funds managed by this company
   * - Contacts for this company
   * - All fund-related data (events, cash flows, tax statements, etc.)
   * 
   * @param companyId The ID of the company to delete
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if company doesn't exist
   * @throws ApiError with BUSINESS_LOGIC_ERROR if company has dependencies that prevent deletion
   * 
   * @example
   * ```typescript
   * await api.companies.deleteCompany(1);
   * console.log('Company deleted successfully');
   * ```
   */
  async deleteCompany(companyId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/companies/${companyId}`);
  }

  // ============================================================================
  // CONTACTS
  // ============================================================================

  /**
   * Get all contacts with optional filters.
   * 
   * Supports filtering by:
   * - company_id (single) or company_ids (multiple)
   * - name (single) or names (multiple)
   * 
   * Supports sorting by: NAME, CREATED_AT, UPDATED_AT
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Response with contacts and count
   * 
   * @example
   * ```typescript
   * // Get all contacts for a specific company
   * const contacts = await api.companies.getContacts({
   *   company_id: 1
   * });
   * 
   * // Get all contacts with company details
   * const contactsWithCompany = await api.companies.getContacts({
   *   include_company: true
   * });
   * ```
   */
  async getContacts(params: GetContactsQueryParams = {}): Promise<GetContactsResponse> {
    return this.client.get<GetContactsResponse>('/api/contacts', params);
  }

  /**
   * Get all contacts for a specific company (nested endpoint).
   * 
   * @param companyId The ID of the company
   * @returns Response with contacts for the company
   * 
   * @example
   * ```typescript
   * const contacts = await api.companies.getContactsByCompanyId(1);
   * ```
   */
  async getContactsByCompanyId(companyId: number): Promise<GetContactsResponse> {
    return this.client.get<GetContactsResponse>(`/api/companies/${companyId}/contacts`);
  }

  /**
   * Get a single contact by ID (nested endpoint).
   * 
   * @param companyId The ID of the company
   * @param contactId The ID of the contact to retrieve
   * @returns Single contact object
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if contact doesn't exist
   * 
   * @example
   * ```typescript
   * const contact = await api.companies.getContact(1, 5);
   * ```
   */
  async getContact(
    companyId: number,
    contactId: number
  ): Promise<GetContactResponse> {
    return this.client.get<GetContactResponse>(`/api/companies/${companyId}/contacts/${contactId}`);
  }

  /**
   * Create a new contact for a specific company.
   * 
   * Required fields:
   * - name: Contact person's name
   * 
   * Optional fields:
   * - title: Job title
   * - phone: Phone number
   * - email: Email address
   * 
   * @param companyId The ID of the company
   * @param data Contact creation data (company_id not needed, taken from URL)
   * @returns Created contact object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with RESOURCE_NOT_FOUND if company doesn't exist
   * 
   * @example
   * ```typescript
   * const newContact = await api.companies.createContact(1, {
   *   name: 'John Smith',
   *   title: 'Managing Partner',
   *   direct_email: 'john.smith@acmecapital.com',
   *   direct_number: '+1-555-0123'
   * });
   * ```
   */
  async createContact(companyId: number, data: CreateContactRequest): Promise<Contact> {
    return this.client.post<Contact>(`/api/companies/${companyId}/contacts`, data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/companies/<company_id>/contacts/<id>, add updateContact() method here

  /**
   * Delete a contact.
   * 
   * @param companyId The ID of the company
   * @param contactId The ID of the contact to delete
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if contact doesn't exist
   * 
   * @example
   * ```typescript
   * await api.companies.deleteContact(1, 5);
   * console.log('Contact deleted successfully');
   * ```
   */
  async deleteContact(companyId: number, contactId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/companies/${companyId}/contacts/${contactId}`);
  }
}
