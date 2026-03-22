/**
 * Entity Schemas
 * 
 * Zod validation schemas for entity (investor/stakeholder) forms.
 * Aligned with backend: /api/entities POST endpoint
 */

import { z } from 'zod';
import { nonEmptyString } from './commonSchemas';
import { EntityType } from '@/types/enums/entity.enums';
import { Country } from '@/types/enums/shared.enums';

/**
 * Entity Creation Schema
 * 
 * Validates new entity creation (individuals or organizations)
 * 
 * Required: name, entity_type, tax_jurisdiction
 * Note: Backend does NOT support address fields - removed from schema
 */
export const createEntitySchema = z.object({
  name: nonEmptyString
    .min(2, 'Entity name must be at least 2 characters')
    .max(255, 'Entity name must be less than 255 characters'),
  
  entity_type: z.nativeEnum(EntityType, {
    errorMap: () => ({ message: 'Please select a valid entity type' })
  }),
  
  tax_jurisdiction: z.nativeEnum(Country, {
    errorMap: () => ({ message: 'Please select a valid tax jurisdiction' })
  }),
  
  description: z.string()
    .max(1000, 'Description must be less than 1000 characters')
    .optional()
});

export type CreateEntityFormData = z.infer<typeof createEntitySchema>;
