// Entity-specific Custom Hooks
// This file provides hooks for entity-related API operations

import { apiClient } from '../services/api';
import { useApiCall, useMutation } from './useApiCall';
import {
  Entity,
  CreateEntityData,
  EntityType,
  Country,
} from '../types/api';
import { useCallback } from 'react';

// ============================================================================
// ENTITIES HOOKS
// ============================================================================

/**
 * Hook to get all entities
 */
export function useEntities(options?: { refetchOnWindowFocus?: boolean }) {
  const getEntities = useCallback(async () => {
    const result = await apiClient.getEntities();
    return result;
  }, []);
  
  return useApiCall(
    getEntities,
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