/**
 * Entity Hooks - CRUD operations for entities
 * 
 * Maps 1:1 to entity.api.ts methods and backend /api/entities endpoints
 * 
 * Note: Entities are immutable by design - no update operations exist
 * 
 * @module entity/hooks/useEntities
 */

import { useCallback } from 'react';
import { useQuery, useMutation } from '@/shared/hooks/core';
import { entityApi } from '../api';
import type {
  Entity,
  GetEntitiesResponse,
  GetEntityResponse,
  GetEntitiesQueryParams,
  CreateEntityRequest,
} from '../types';

// ============================================================================
// ENTITY DEPENDENCY ERROR UTILITIES
// ============================================================================

/**
 * Parsed dependency details from backend validation errors
 */
export interface EntityDependencyDetails {
  funds?: number;
  bankAccounts?: number;
  taxStatements?: number;
}

/**
 * Parse entity deletion validation error from backend
 * Backend returns: "Deletion validation failed for entity with ID X: {error_dict}"
 */
export function parseEntityDependencyError(errorMessage: string): EntityDependencyDetails {
  const details: EntityDependencyDetails = {};
  
  // Check for specific dependency messages in error
  if (errorMessage.includes('dependent funds') || errorMessage.includes("'funds'")) {
    details.funds = 1; // At least 1 fund exists
  }
  if (errorMessage.includes('dependent bank accounts') || errorMessage.includes("'bank_accounts'")) {
    details.bankAccounts = 1; // At least 1 bank account exists
  }
  if (errorMessage.includes('dependent tax statements') || errorMessage.includes("'tax_statements'")) {
    details.taxStatements = 1; // At least 1 tax statement exists
  }
  
  return details;
}

/**
 * Check if error is an entity dependency blocking error
 */
export function isEntityDependencyError(error: any): boolean {
  return (
    error?.responseCode === 'BUSINESS_LOGIC_ERROR' &&
    (error?.message?.includes('Deletion validation failed') ||
     error?.message?.includes('dependent'))
  );
}

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
  const queryFn = useCallback(() => entityApi.getEntities(params), [params]);
  
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
    () => entityApi.getEntity(entityId),
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
    (data) => entityApi.createEntity(data)
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
    () => entityApi.deleteEntity(entityId)
  );
}

