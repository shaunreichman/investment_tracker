/**
 * Fund API Export
 * 
 * Domain-specific API for fund operations.
 * 
 * Usage:
 *   import { fundApi } from '@/fund/api';
 *   const funds = await fundApi.getFunds();
 */

import { apiClient } from '@/shared/api';
import { FundApi } from './fundApi';

// Export API class for custom instances if needed
export { FundApi } from './fundApi';

// Export singleton instance for standard use
export const fundApi = new FundApi(apiClient);

