/**
 * Banking API Export
 * 
 * Domain-specific API for banking operations.
 * 
 * Usage:
 *   import { bankingApi } from '@/bank/api';
 *   const banks = await bankingApi.getBanks();
 */

import { apiClient } from '@/shared/api';
import { BankingApi } from './bankApi';

// Export API class for custom instances if needed
export { BankingApi } from './bankApi';

// Export singleton instance for standard use
export const bankingApi = new BankingApi(apiClient);

