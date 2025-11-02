/**
 * Company Schemas
 * 
 * Zod validation schemas for company and contact forms.
 * Aligned with backend: /api/companies and /api/companies/:id/contacts endpoints
 */

import { z } from 'zod';
import { nonEmptyString, emailAddress, phoneNumber, urlString } from './commonSchemas';
import { CompanyType } from '@/types/enums/company.enums';

/**
 * Company Creation Schema
 * 
 * Validates new company creation
 * Aligned with backend: /api/companies POST endpoint
 * 
 * Required: name
 */
export const createCompanySchema = z.object({
  name: nonEmptyString
    .min(2, 'Company name must be at least 2 characters')
    .max(255, 'Company name must be less than 255 characters'),
  
  description: z.string()
    .max(1000, 'Description must be less than 1000 characters')
    .optional(),
  
  company_type: z.nativeEnum(CompanyType, {
    errorMap: () => ({ message: 'Please select a valid company type' })
  }).optional(),
  
  website: urlString.optional(),
  
  business_address: z.string()
    .max(1000, 'Business address must be less than 1000 characters')
    .optional()
});

export type CreateCompanyFormData = z.infer<typeof createCompanySchema>;

/**
 * Contact Creation Schema
 * 
 * Validates contact creation for companies
 * Aligned with backend: /api/companies/:id/contacts POST endpoint
 * Backend model: src/company/models/contact.py
 * 
 * Required: name
 * Note: company_id is provided via path parameter, not in body
 */
export const createContactSchema = z.object({
  name: nonEmptyString
    .min(2, 'Contact name must be at least 2 characters')
    .max(255, 'Contact name must be less than 255 characters'),
  
  direct_email: emailAddress.optional(),
  
  direct_number: phoneNumber.optional(),
  
  title: z.string()
    .max(100, 'Title must be less than 100 characters')
    .optional()
});

export type CreateContactFormData = z.infer<typeof createContactSchema>;

