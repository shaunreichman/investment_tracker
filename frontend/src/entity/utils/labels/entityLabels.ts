/**
 * Entity type labels for UI display.
 * 
 * Maps EntityType enum values to user-friendly strings.
 */

import { EntityType } from '@/entity/types';

export const ENTITY_TYPE_LABELS: Record<EntityType, string> = {
  [EntityType.PERSON]: 'Person',
  [EntityType.COMPANY]: 'Company',
  [EntityType.TRUST]: 'Trust',
  [EntityType.FUND]: 'Fund',
  [EntityType.OTHER]: 'Other',
};

/**
 * Get entity type label with fallback.
 * 
 * @param entityType - The entity type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getEntityTypeLabel(entityType: EntityType): string {
  return ENTITY_TYPE_LABELS[entityType] || entityType;
}

