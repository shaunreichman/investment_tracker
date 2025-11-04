/**
 * Rates API Export
 * 
 * Domain-specific API for rates operations.
 * 
 * Usage:
 *   import { ratesApi } from '@/rates/api';
 *   const rates = await ratesApi.getRiskFreeRates();
 */

import { apiClient } from '@/shared/api';
import { RatesApi } from './ratesApi';

// Export API class for custom instances if needed
export { RatesApi } from './ratesApi';

// Export singleton instance for standard use
export const ratesApi = new RatesApi(apiClient);

