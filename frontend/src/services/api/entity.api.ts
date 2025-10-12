/**
 * Entity API
 * 
 * All entity-related API methods including:
 * - Entities (CRUD operations)
 * 
 * Entities represent investing entities (people, companies, trusts, etc.)
 * in the investment tracking system.
 */

import { ApiClient } from '../api-client';
import {
  Entity,
  CreateEntityRequest,
  GetEntitiesResponse,
  GetEntityResponse,
  GetEntitiesQueryParams
} from '../../types/models/entity';

export class EntityApi {
  constructor(private client: ApiClient) {}

  // ============================================================================
  // ENTITIES
  // ============================================================================

  /**
   * Get all entities with optional filters.
   * 
   * Supports filtering by:
   * - name (single) or names (multiple)
   * - entity_type (single) or entity_types (multiple)
   * - tax_jurisdiction (single) or tax_jurisdictions (multiple)
   * 
   * Supports sorting by: NAME, TYPE, TAX_JURISDICTION, CREATED_AT, UPDATED_AT
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Array of entities
   * 
   * @example
   * ```typescript
   * // Get all entities
   * const entities = await api.entities.getEntities();
   * 
   * // Get all PERSON entities in Australia
   * const australianPeople = await api.entities.getEntities({
   *   entity_type: EntityType.PERSON,
   *   tax_jurisdiction: Country.AU
   * });
   * 
   * // Get entities sorted by name
   * const sortedEntities = await api.entities.getEntities({
   *   sort_by: SortFieldEntity.NAME,
   *   sort_order: SortOrder.ASC
   * });
   * ```
   */
  async getEntities(params: GetEntitiesQueryParams = {}): Promise<GetEntitiesResponse> {
    return this.client.get<GetEntitiesResponse>('/api/entities', params);
  }

  /**
   * Get a single entity by ID.
   * 
   * @param entityId The ID of the entity to retrieve
   * @returns Single entity object
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if entity doesn't exist
   * 
   * @example
   * ```typescript
   * const entity = await api.entities.getEntity(1);
   * console.log(entity.name, entity.entity_type);
   * ```
   */
  async getEntity(entityId: number): Promise<GetEntityResponse> {
    return this.client.get<GetEntityResponse>(`/api/entities/${entityId}`);
  }

  /**
   * Create a new entity.
   * 
   * Required fields:
   * - name: 2-255 characters
   * - entity_type: Valid EntityType enum
   * - tax_jurisdiction: Valid Country enum
   * 
   * Optional fields:
   * - description: Max 1000 characters
   * 
   * @param data Entity creation data
   * @returns Created entity object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with BUSINESS_LOGIC_ERROR if entity name already exists
   * 
   * @example
   * ```typescript
   * const newEntity = await api.entities.createEntity({
   *   name: 'John Doe',
   *   entity_type: EntityType.PERSON,
   *   tax_jurisdiction: Country.AU,
   *   description: 'Individual investor'
   * });
   * ```
   */
  async createEntity(data: CreateEntityRequest): Promise<Entity> {
    return this.client.post<Entity>('/api/entities', data);
  }

  // Note: UPDATE functionality intentionally NOT implemented
  // Entities are immutable after creation by design
  // This prevents accidental data corruption from entity type changes

  /**
   * Delete an entity.
   * 
   * Important: Deletion is BLOCKED if entity has dependencies.
   * Backend validation prevents deletion if entity has:
   * - Funds owned by this entity
   * - Bank accounts owned by this entity
   * - Fund tax statements for this entity
   * 
   * @param entityId The ID of the entity to delete
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if entity doesn't exist
   * @throws ApiError with BUSINESS_LOGIC_ERROR if entity has dependencies that prevent deletion
   *         Error details will include which dependencies are blocking deletion
   * 
   * @example
   * ```typescript
   * try {
   *   await api.entities.deleteEntity(1);
   *   console.log('Entity deleted successfully');
   * } catch (error) {
   *   if (error.responseCode === 'BUSINESS_LOGIC_ERROR') {
   *     // Entity has dependencies - parse error for details
   *     console.error('Cannot delete: entity has dependencies');
   *   }
   * }
   * ```
   */
  async deleteEntity(entityId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/entities/${entityId}`);
  }
}
