/**
 * Entity Transformers
 * 
 * Transform entity (investor/stakeholder) form data to API request types.
 */

import type { CreateEntityFormData } from '../schemas';
import type { CreateEntityRequest } from '@/types/models/entity';

/**
 * Transform Entity Creation form data to API request
 * 
 * Filters empty optional fields and trims string values.
 * 
 * @param formData - Validated entity creation form data
 * @returns API request ready for submission
 */
export function transformCreateEntityForm(
  formData: CreateEntityFormData
): CreateEntityRequest {
  const request: CreateEntityRequest = {
    name: formData.name.trim(),
    entity_type: formData.entity_type,
    tax_jurisdiction: formData.tax_jurisdiction
  };
  
  // Optional description
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  return request;
}
