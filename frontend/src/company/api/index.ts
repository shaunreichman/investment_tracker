/**
 * Company API Export
 * 
 * Domain-specific API for company operations.
 * 
 * Usage:
 *   import { companyApi } from '@/company/api';
 *   const companies = await companyApi.getCompanies();
 */

import { apiClient } from '@/shared/api';
import { CompanyApi } from './companyApi';

// Export API class for custom instances if needed
export { CompanyApi } from './companyApi';

// Export singleton instance for standard use
export const companyApi = new CompanyApi(apiClient);
