/**
 * Entity Hooks - Barrel Export
 * 
 * All hooks for entity domain operations:
 * - Entities (CRUD - no update, immutable by design)
 * - Form validation schemas
 * - Form transformers
 * 
 * @module entity/hooks
 */

export {
  useEntities,
  useEntity,
  useCreateEntity,
  useDeleteEntity,
} from './useEntities';

// Export form schemas
export * from './schemas';

// Export form transformers
export * from './transformers';

