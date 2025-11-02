/**
 * Unified API Export
 * 
 * Provides a single, organized interface to all API methods.
 * 
 * Usage:
 *   import { api } from '@/services/api';
 *   
 *   // Banking
 *   const banks = await api.banking.getBanks();
 *   const bank = await api.banking.createBank({ name: 'Test Bank', country: 'US' });
 *   
 *   // Future domains (will be added incrementally):
 *   // const funds = await api.funds.getFunds();
 *   // const entities = await api.entities.getEntities();
 */

import { apiClient } from '../api-client';
import { BankingApi } from './banking.api';
import { RatesApi } from './rates.api';
import { EntityApi } from './entity.api';
import { CompanyApi } from './company.api';
import { FundApi } from './fund.api';

// ============================================================================
// DOMAIN API INSTANCES
// ============================================================================

const banking = new BankingApi(apiClient);
const rates = new RatesApi(apiClient);
const entities = new EntityApi(apiClient);
const Companies = new CompanyApi(apiClient);
const funds = new FundApi(apiClient);

// ============================================================================
// UNIFIED API OBJECT
// ============================================================================

/**
 * Unified API interface providing access to all domain APIs.
 * 
 * Organized by business domain for clear separation of concerns.
 */
export const api = {
  banking,
  rates,
  entities,
  Companies,
  funds,
};

// ============================================================================
// RE-EXPORTS
// ============================================================================

// Export base client and error for advanced use cases
export { apiClient, ApiClient, ApiError } from '../api-client';

// Export individual domain APIs for tree-shaking
export { BankingApi } from './banking.api';
export { RatesApi } from './rates.api';
export { EntityApi } from './entity.api';
export { CompanyApi } from './company.api';
export { FundApi } from './fund.api';

// ============================================================================
// TYPE EXPORTS
// ============================================================================

// Export API type for use in components
export type Api = typeof api;
