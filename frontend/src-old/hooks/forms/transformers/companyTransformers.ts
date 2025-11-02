/**
 * Company Transformers
 * 
 * Transform company and contact form data to API request types.
 */

import type { CreateCompanyFormData, CreateContactFormData } from '../schemas';
import type { CreateCompanyRequest, CreateContactRequest } from '@/types/models/company';

/**
 * Transform Company Creation form data to API request
 * 
 * Filters empty optional fields and trims string values.
 * 
 * @param formData - Validated company creation form data
 * @returns API request ready for submission
 */
export function transformCreateCompanyForm(
  formData: CreateCompanyFormData
): CreateCompanyRequest {
  const request: CreateCompanyRequest = {
    name: formData.name.trim()
  };
  
  // Optional description
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  // Optional company type
  if (formData.company_type) {
    request.company_type = formData.company_type;
  }
  
  // Optional website
  if (formData.website?.trim()) {
    request.website = formData.website.trim();
  }
  
  // Optional business address
  if (formData.business_address?.trim()) {
    request.business_address = formData.business_address.trim();
  }
  
  return request;
}

/**
 * Transform Contact Creation form data to API request
 * 
 * Note: company_id is provided via URL path parameter, not in request body
 * 
 * @param formData - Validated contact creation form data
 * @returns API request ready for submission
 */
export function transformCreateContactForm(
  formData: CreateContactFormData
): CreateContactRequest {
  const request: CreateContactRequest = {
    name: formData.name.trim()
  };
  
  // Optional direct email
  if (formData.direct_email?.trim()) {
    request.direct_email = formData.direct_email.trim();
  }
  
  // Optional direct number
  if (formData.direct_number?.trim()) {
    request.direct_number = formData.direct_number.trim();
  }
  
  // Optional title
  if (formData.title?.trim()) {
    request.title = formData.title.trim();
  }
  
  return request;
}

