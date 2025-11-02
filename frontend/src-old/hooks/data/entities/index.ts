/**
 * Entity Data Hooks - Barrel Export
 * 
 * All hooks for entity domain operations:
 * - Entities (CRUD - no update, immutable by design)
 * 
 * @module hooks/data/entities
 */

export {
  useEntities,
  useEntity,
  useCreateEntity,
  useDeleteEntity,
} from './useEntities';

