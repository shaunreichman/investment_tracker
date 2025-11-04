/**
 * Company Hooks - Barrel Export
 * 
 * All hooks for company domain operations:
 * - Companies (CRUD)
 * - Contacts (CRUD)
 * 
 * @module company/hooks
 */

// Company hooks
export {
  useCompanies,
  useCompany,
  useCreateCompany,
  useDeleteCompany,
} from './useCompanies';

// Contact hooks
export {
  useContacts,
  useContactsByCompanyId,
  useContact,
  useCreateContact,
  useDeleteContact,
} from './useContacts';

// Form validation schemas
export * from './schemas';

// Form transformers
export * from './transformers';

