// Entity-specific Custom Hooks
// This file provides hooks for entity-related API operations

import { apiClient } from '../services/api';
import { useApiCall, useMutation } from './useApiCall';
import {
  Entity,
  EntityListResponse,
  CreateEntityData,
} from '../types/api';

// ============================================================================
// ENTITIES HOOKS
// ============================================================================

/**
 * Hook to get all entities
 */
export function useEntities(options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCall(
    () => apiClient.getEntities(),
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to create a new entity
 */
export function useCreateEntity() {
  return useMutation<CreateEntityData, Entity>(
    (data) => apiClient.createEntity(data)
  );
} 