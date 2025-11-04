/**
 * Entity API Export
 * 
 * Domain-specific API for entity operations.
 * 
 * Usage:
 *   import { entityApi } from '@/entity/api';
 *   const entities = await entityApi.getEntities();
 */

import { apiClient } from '@/shared/api';
import { EntityApi } from './entityApi';

// Export API class for custom instances if needed
export { EntityApi } from './entityApi';

// Export singleton instance for standard use
export const entityApi = new EntityApi(apiClient);
