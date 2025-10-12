// Entity-specific Custom Hooks
// This file provides hooks for entity-related API operations

import { api } from '../services/api/index';
import { useApiCall, useMutation, useApiCallWithDeps } from './useApiCallold';
import { Entity, CreateEntityRequest } from '../types/models/entity';
import { EntityType } from '../types/enums/entity.enums';
import { Country } from '../types/enums/shared.enums';
import { useCallback } from 'react';

// ============================================================================
// ENTITY DEPENDENCY ERROR TYPES
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
// ENTITIES HOOKS
// ============================================================================

/**
 * Hook to get all entities with optional filters
 * 
 * @param options - Optional configuration including filters and refetch behavior
 * @returns Entity list state with data, loading, error, and refetch function
 * 
 * @example
 * ```typescript
 * const { data: entities, loading, error, refetch } = useEntities();
 * 
 * // With filters
 * const { data } = useEntities({
 *   filters: { entity_type: EntityType.PERSON }
 * });
 * ```
 */
export function useEntities(options?: { 
  refetchOnWindowFocus?: boolean;
}) {
  const getEntities = useCallback(async () => {
    const result = await api.entities.getEntities();
    return result;
  }, []);
  
  return useApiCall(
    getEntities,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get a single entity by ID
 * 
 * @param entityId - The ID of the entity to fetch
 * @param options - Optional configuration for refetch behavior
 * @returns Single entity state with data, loading, error, and refetch function
 * 
 * @example
 * ```typescript
 * const { data: entity, loading, error } = useEntity(1);
 * ```
 */
export function useEntity(
  entityId: number,
  options?: { refetchOnWindowFocus?: boolean }
) {
  return useApiCallWithDeps(
    async (id: number) => {
      return await api.entities.getEntity(id);
    },
    [entityId],
    { 
      refetchOnWindowFocus: options?.refetchOnWindowFocus,
      enabled: !!entityId 
    }
  );
}

/**
 * Hook to create a new entity
 * 
 * Note: Entities are immutable after creation - they cannot be edited
 * 
 * @returns Mutation state with mutate function, data, loading, and error
 * 
 * @example
 * ```typescript
 * const createEntity = useCreateEntity();
 * 
 * const handleCreate = async () => {
 *   await createEntity.mutate({
 *     name: 'John Doe',
 *     entity_type: EntityType.PERSON,
 *     tax_jurisdiction: Country.AU
 *   });
 * };
 * ```
 */
export function useCreateEntity() {
  return useMutation<CreateEntityRequest, Entity>(
    (data) => api.entities.createEntity(data)
  );
}

/**
 * Hook to delete an entity
 * 
 * Important: Deletion will fail if entity has dependencies (funds, bank accounts, tax statements)
 * Use parseEntityDependencyError() to extract dependency details from error
 * 
 * @returns Mutation state with mutate function, data, loading, and error
 * 
 * @example
 * ```typescript
 * const deleteEntity = useDeleteEntity();
 * 
 * const handleDelete = async (entityId: number) => {
 *   try {
 *     await deleteEntity.mutate(entityId);
 *     showSuccessMessage('Entity deleted');
 *   } catch (error) {
 *     if (isEntityDependencyError(error)) {
 *       const deps = parseEntityDependencyError(error.message);
 *       showDependencyBlockedDialog(deps);
 *     }
 *   }
 * };
 * ```
 */
export function useDeleteEntity() {
  return useMutation<number, { message: string; deleted_id: number }>(
    (entityId) => api.entities.deleteEntity(entityId)
  );
} 