/**
 * Entity Domain Models
 * 
 * TypeScript interfaces matching backend entity domain models exactly.
 * Source: src/entity/models/entity.py
 * 
 * DO NOT modify these types without updating the corresponding Python models.
 * These must remain in sync with the backend for API communication.
 */

import { EntityType, SortFieldEntity } from './entityEnums';
import { Country, SortOrder } from '@/shared/types';

// ============================================================================
// CORE ENTITY MODEL
// ============================================================================

/**
 * Entity - Represents an investing entity (person or company)
 * 
 * Backend source: src/entity/models/entity.py
 */
export interface Entity {
  // System fields
  /** Auto-generated primary key (SYSTEM) */
  readonly id: number;
  
  /** Creation timestamp (SYSTEM) */
  readonly created_at: string; // ISO 8601 datetime string
  
  /** Last update timestamp (SYSTEM) */
  readonly updated_at: string; // ISO 8601 datetime string
  
  // Manual fields
  /** Entity name - unique across all entities (MANUAL) */
  name: string;
  
  /** Entity type - person or company (MANUAL) */
  entity_type: EntityType;
  
  /** ISO 3166-1 alpha-2 country code for tax jurisdiction (MANUAL) */
  tax_jurisdiction: Country;
  
  /** Optional description of the entity (MANUAL) */
  description: string | null;
}

// ============================================================================
// REQUEST DTOs
// ============================================================================

/**
 * Create Entity Request
 * 
 * Backend validation:
 * - name: required, 2-255 characters, must be unique
 * - entity_type: required, must be valid EntityType enum
 * - tax_jurisdiction: required, must be valid Country enum
 * - description: optional, max 1000 characters
 */
export interface CreateEntityRequest {
  /** Entity name (required, 2-255 characters) */
  name: string;
  
  /** Entity type (required) */
  entity_type: EntityType;
  
  /** ISO 3166-1 alpha-2 country code for tax jurisdiction (required) */
  tax_jurisdiction: Country;
  
  /** Optional description of the entity (optional, max 1000 characters) */
  description?: string;
}

// Note: UPDATE functionality not yet implemented in backend
// When backend implements PUT /api/entities/<id>, add UpdateEntityRequest here

// ============================================================================
// RESPONSE DTOs
// ============================================================================

/**
 * Get Entities Response - List of entities
 */
export type GetEntitiesResponse = Entity[];

/**
 * Get Entity Response - Single entity
 */
export type GetEntityResponse = Entity;

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

/**
 * Query parameters for GET /api/entities
 * 
 * All parameters are optional. Supports filtering and sorting.
 * 
 * Mutually exclusive groups (backend validation):
 * - name OR names (not both)
 * - entity_type OR entity_types (not both)
 * - tax_jurisdiction OR tax_jurisdictions (not both)
 */
export interface GetEntitiesQueryParams {
  /** Filter by entity name */
  name?: string;
  
  /** Filter by entity names (array) */
  names?: string[];
  
  /** Filter by entity type */
  entity_type?: EntityType;
  
  /** Filter by entity types (array) */
  entity_types?: EntityType[];
  
  /** Filter by tax jurisdiction */
  tax_jurisdiction?: Country;
  
  /** Filter by tax jurisdictions (array) */
  tax_jurisdictions?: Country[];
  
  /** Sort by field */
  sort_by?: SortFieldEntity;
  
  /** Sort order */
  sort_order?: SortOrder;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial entity for list views (minimal data)
 */
export type EntitySummary = Pick<Entity, 'id' | 'name' | 'entity_type' | 'tax_jurisdiction'>;

/**
 * Entity with relationships (for detail views)
 * 
 * Note: Current backend doesn't support including relationships.
 * This type is prepared for future enhancement.
 */
export type EntityWithRelationships = Entity & {
  // Future: Include related funds, bank accounts, tax statements
  // funds?: Fund[];
  // bank_accounts?: BankAccount[];
  // fund_tax_statements?: FundTaxStatement[];
};

