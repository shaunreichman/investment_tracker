/**
 * Entity Hooks - CRUD operations for entities
 * 
 * Maps 1:1 to entity.api.ts methods and backend /api/entities endpoints
 * 
 * Note: Entities are immutable by design - no update operations exist
 * 
 * @module hooks/data/entities/useEntities
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/hooks/core/api';
import { api } from '@/services/api/index';
import type {
  Entity,
  GetEntitiesResponse,
  GetEntityResponse,
  GetEntitiesQueryParams,
  CreateEntityRequest,
} from '@/types/models/entity';

// ============================================================================
// ENTITY QUERIES
// ============================================================================

/**
 * Get all entities with optional filters
 * Maps to: GET /api/entities
 * 
 * @param params - Query parameters for filtering and sorting
 * @param options - Hook options
 * @returns Query result with entities and count
 * 
 * @example
 * ```typescript
 * // Get all entities
 * const { data, loading } = useEntities();
 * 
 * // Get all PERSON entities in Australia
 * const { data, loading } = useEntities({ 
 *   entity_type: EntityType.PERSON,
 *   tax_jurisdiction: Country.AU
 * });
 * ```
 */
export function useEntities(
  params?: GetEntitiesQueryParams,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(() => api.entities.getEntities(params), [params]);
  
  return useQuery<GetEntitiesResponse>(queryFn, {
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

/**
 * Get a single entity by ID
 * Maps to: GET /api/entities/:id
 * 
 * @param entityId - Entity ID
 * @param options - Hook options
 * @returns Query result with entity data
 * 
 * @example
 * ```typescript
 * const { data: entity, loading } = useEntity(entityId);
 * ```
 */
export function useEntity(
  entityId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  const queryFn = useCallback(
    () => api.entities.getEntity(entityId),
    [entityId]
  );
  
  return useQuery<GetEntityResponse>(queryFn, {
    enabled: entityId > 0,
    refetchOnWindowFocus: options?.refetchOnWindowFocus,
  });
}

// ============================================================================
// ENTITY MUTATIONS
// ============================================================================

/**
 * Create a new entity
 * Maps to: POST /api/entities
 * 
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: createEntity, loading } = useCreateEntity();
 * 
 * createEntity({
 *   name: 'John Doe',
 *   entity_type: EntityType.PERSON,
 *   tax_jurisdiction: Country.AU,
 *   description: 'Individual investor'
 * });
 * ```
 */
export function useCreateEntity() {
  return useMutation<Entity, CreateEntityRequest>(
    (data) => api.entities.createEntity(data)
  );
}

/**
 * Delete an entity
 * Maps to: DELETE /api/entities/:id
 * 
 * Note: Deletion is blocked if entity has dependencies (funds, bank accounts, tax statements)
 * 
 * @param entityId - Entity ID to delete
 * @returns Mutation result
 * 
 * @example
 * ```typescript
 * const { mutate: deleteEntity, loading, error } = useDeleteEntity(entityId);
 * 
 * deleteEntity(undefined, {
 *   onSuccess: () => navigate('/entities'),
 *   onError: (error) => {
 *     // Handle dependency validation errors
 *     console.error('Cannot delete:', error.userMessage);
 *   }
 * });
 * ```
 */
export function useDeleteEntity(entityId: number) {
  return useMutation<{ message: string; deleted_id: number }, void>(
    () => api.entities.deleteEntity(entityId)
  );
}

