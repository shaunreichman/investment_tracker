/**
 * Company Domain Type Definitions
 * 
 * TypeScript interfaces matching backend company models exactly.
 * Source: src/company/models/
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { CompanyType, CompanyStatus } from '../enums/company.enums';

// ============================================================================
// COMPANY MODEL
// ============================================================================

/**
 * Company - Represents an company which manages funds.
 * 
 * Source: src/company/models/company.py
 */
export interface Company {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Manual fields
  /** Company name (MANUAL) */
  name: string;
  
  /** Company description (MANUAL) */
  description?: string | null;
  
  /** Type of company using CompanyType enum (MANUAL) */
  company_type?: CompanyType | null;
  
  /** Business address (MANUAL) */
  business_address?: string | null;
  
  /** Company website URL (MANUAL) */
  website?: string | null;
  
  // Fund Information (CALCULATED)
  /** Total number of funds (CALCULATED) */
  total_funds?: number;
  
  /** Total number of active funds (CALCULATED) */
  total_funds_active?: number;
  
  /** Total number of completed funds (CALCULATED) */
  total_funds_completed?: number;
  
  /** Total number of realized funds (CALCULATED) */
  total_funds_realized?: number;
  
  // Equity storage fields (CALCULATED)
  /** Total commitment amount from funds (CALCULATED) */
  total_commitment_amount?: number;
  
  /** Current equity balance from capital movements (CALCULATED) */
  current_equity_balance?: number;
  
  /** Time-weighted average equity balance (CALCULATED) */
  average_equity_balance?: number;
  
  // IRR storage fields (CALCULATED)
  /** Completed gross IRR only of realized/completed funds (CALCULATED) */
  completed_irr_gross?: number | null;
  
  /** Completed after-tax IRR only of realized/completed funds (CALCULATED) */
  completed_irr_after_tax?: number | null;
  
  /** Completed real IRR only of realized/completed funds (CALCULATED) */
  completed_irr_real?: number | null;
  
  // Profitability storage fields (CALCULATED)
  /** PNL (CALCULATED) */
  pnl?: number;
  
  /** Realized PNL (CALCULATED) */
  realized_pnl?: number;
  
  /** Unrealized PNL (CALCULATED) */
  unrealized_pnl?: number;
  
  /** Realized Capital Gain PNL (CALCULATED) */
  realized_pnl_capital_gain?: number;
  
  /** Unrealized Capital Gain PNL (CALCULATED) */
  unrealized_pnl_capital_gain?: number;
  
  /** Realized Dividend PNL (CALCULATED) */
  realized_pnl_dividend?: number;
  
  /** Realized Interest PNL (CALCULATED) */
  realized_pnl_interest?: number;
  
  /** Realized Distribution PNL (CALCULATED) */
  realized_pnl_distribution?: number;
  
  // Additional information (CALCULATED)
  /** Company status using CompanyStatus enum (CALCULATED) */
  status?: CompanyStatus | null;
  
  /** Company start date (CALCULATED) */
  start_date?: string | null; // ISO 8601 date string (YYYY-MM-DD)
  
  /** Company end date (CALCULATED) */
  end_date?: string | null; // ISO 8601 date string (YYYY-MM-DD)
  
  /** Current company duration in months based on status (CALCULATED) */
  current_duration?: number | null;
  
  // Relationships (optional - included based on API query params)
  /** Contacts (if include_contacts=true) */
  contacts?: Contact[];
  
  /** Funds (if include_funds=true) */
  funds?: any[]; // TODO: Replace with Fund[] when Fund type is available
}

// ============================================================================
// CONTACT MODEL
// ============================================================================

/**
 * Contact - Represents a contact person at an company.
 * 
 * Source: src/company/models/contact.py
 */
export interface Contact {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string;
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string;
  
  // Relationship fields
  /** Foreign key to company (RELATIONSHIP) */
  company_id: number;
  
  // Manual fields
  /** Contact person's name (MANUAL) */
  name: string;
  
  /** Contact person's job title (MANUAL) */
  title?: string | null;
  
  /** Direct phone number (MANUAL) */
  direct_number?: string | null;
  
  /** Direct email address (MANUAL) */
  direct_email?: string | null;
  
  /** Additional notes about the contact (MANUAL) */
  notes?: string | null;
  
  // Relationships (optional - included based on API query params)
  /** Company details (if included) */
  company?: Company;
}

// ============================================================================
// REQUEST DTOs
// ============================================================================

/**
 * Data required to create a new company.
 */
export interface CreateCompanyRequest {
  /** Company name (required) */
  name: string;
  
  /** Company description (optional) */
  description?: string;
  
  /** Type of company (optional) */
  company_type?: CompanyType;
  
  /** Business address (optional) */
  business_address?: string;
  
  /** Company website URL (optional) */
  website?: string;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/companies/<id>, add UpdateCompanyRequest here

/**
 * Data required to create a new contact.
 * 
 * Note: company_id is provided via URL path parameter (/api/companies/:company_id/contacts), not in request body
 * Aligned with backend model: src/company/models/contact.py
 */
export interface CreateContactRequest {
  /** Contact person's name (required) */
  name: string;
  
  /** Contact person's job title (optional) */
  title?: string;
  
  /** Direct email address (optional) */
  direct_email?: string;
  
  /** Direct phone number (optional) */
  direct_number?: string;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/contacts/<id>, add UpdateContactRequest here

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Response from GET /api/companies
 */
export interface GetCompaniesResponse {
  /** List of companies */
  companies: Company[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/companies/:id
 */
export interface GetCompanyResponse {
  /** Company details */
  company: Company;
}

/**
 * Response from GET /api/contacts
 */
export interface GetContactsResponse {
  /** List of contacts */
  contacts: Contact[];
  
  /** Total count */
  count: number;
}

/**
 * Response from GET /api/contacts/:id
 */
export interface GetContactResponse {
  /** Contact details */
  contact: Contact;
}

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

/**
 * Query parameters for GET /api/companies
 */
export interface GetCompaniesQueryParams {
  /** Filter by company name */
  name?: string;
  
  /** Filter by company names (array) */
  names?: string[];
  
  /** Filter by company type */
  company_type?: CompanyType;
  
  /** Filter by company types (array) */
  company_types?: CompanyType[];
  
  /** Filter by status */
  status?: CompanyStatus;
  
  /** Filter by statuses (array) */
  statuses?: CompanyStatus[];
  
  /** Sort by field */
  sort_by?: string;
  
  /** Sort order */
  sort_order?: 'ASC' | 'DESC';
  
  /** Include contacts in response */
  include_contacts?: boolean;
  
  /** Include funds in response */
  include_funds?: boolean;
}

/**
 * Query parameters for GET /api/contacts
 */
export interface GetContactsQueryParams {
  /** Filter by company ID */
  company_id?: number;
  
  /** Filter by company IDs (array) */
  company_ids?: number[];
  
  /** Filter by contact name */
  name?: string;
  
  /** Filter by contact names (array) */
  names?: string[];
  
  /** Sort by field */
  sort_by?: string;
  
  /** Sort order */
  sort_order?: 'ASC' | 'DESC';
  
  /** Include company details in response */
  include_company?: boolean;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial company for list views (minimal data)
 */
export type CompanySummary = Pick<Company, 'id' | 'name' | 'company_type' | 'status' | 'total_funds' | 'current_equity_balance'>;

/**
 * Partial contact for list views (minimal data)
 */
export type ContactSummary = Pick<Contact, 'id' | 'name' | 'title' | 'direct_email' | 'direct_number'>;

/**
 * Company with contacts (for detail views)
 */
export type CompanyWithContacts = Company & Required<Pick<Company, 'contacts'>>;

/**
 * Company with funds (for detail views)
 */
export type CompanyWithFunds = Company & Required<Pick<Company, 'funds'>>;

/**
 * Contact with company (for detail views)
 */
export type ContactWithCompany = Contact & Required<Pick<Contact, 'company'>>;
