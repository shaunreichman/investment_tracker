/**
 * Entity Domain Enums
 * 
 * TypeScript enums matching backend entity domain enums exactly.
 * Source: src/entity/enums/
 * 
 * DO NOT modify these enums without updating the corresponding Python enums.
 * These must remain in sync with the backend for API communication.
 */

// ============================================================================
// ENTITY ENUMS (src/entity/enums/entity_enums.py)
// ============================================================================

/**
 * Entity type enum.
 */
export enum EntityType {
  PERSON = 'PERSON',
  COMPANY = 'COMPANY',
  TRUST = 'TRUST',
  FUND = 'FUND',
  OTHER = 'OTHER'
}

/**
 * Sort field enum for entities.
 */
export enum SortFieldEntity {
  NAME = 'NAME',
  TYPE = 'TYPE',
  TAX_JURISDICTION = 'TAX_JURISDICTION',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT'
}
