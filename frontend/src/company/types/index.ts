/**
 * Company Domain Types Barrel Export
 * 
 * Centralized export of all company domain types.
 * 
 * Usage:
 *   import { Company, Contact, CreateCompanyRequest } from '@/company/types';
 */

// Company types
export type {
  // Core models
  Company,
  
  // Request DTOs
  CreateCompanyRequest,
  
  // Response DTOs
  GetCompaniesResponse,
  GetCompanyResponse,
  CompanyOverviewResponse,
  CompanyDetailsResponse,
  
  // Query parameters
  GetCompaniesQueryParams,
  
  // Utility types
  CompanySummary,
  CompanyWithContacts,
  CompanyWithFunds
} from './company';

// Contact types
export type {
  // Core models
  Contact,
  
  // Request DTOs
  CreateContactRequest,
  
  // Response DTOs
  GetContactsResponse,
  GetContactResponse,
  
  // Query parameters
  GetContactsQueryParams,
  
  // Utility types
  ContactSummary,
  ContactWithCompany
} from './contact';

// Re-export enums from enums.ts
export {
  CompanyType,
  CompanyStatus,
  SortFieldCompany,
  SortFieldContact
} from './companyEnums';

