/**
 * Contact Domain Type Definitions
 * 
 * TypeScript interfaces matching backend company contact models exactly.
 * Source: src/company/models/contact.py
 * 
 * DO NOT modify these interfaces without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import type { Company } from './company';

// ============================================================================
// CONTACT MODEL
// ============================================================================

/**
 * Contact - Represents a contact person at a company.
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
 * Partial contact for list views (minimal data)
 */
export type ContactSummary = Pick<Contact, 'id' | 'name' | 'title' | 'direct_email' | 'direct_number'>;

/**
 * Contact with company (for detail views)
 */
export type ContactWithCompany = Contact & Required<Pick<Contact, 'company'>>;

