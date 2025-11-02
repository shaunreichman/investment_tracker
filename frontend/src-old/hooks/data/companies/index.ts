/**
 * Company Data Hooks - Barrel Export
 * 
 * All hooks for company domain operations:
 * - Companies (CRUD)
 * - Contacts (CRUD)
 * 
 * @module hooks/data/companies
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

