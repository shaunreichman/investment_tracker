/**
 * Rate Transformers
 * 
 * Transform rate form data to API request types.
 * Covers FX rates and risk-free rates.
 */

import type {
  FxRateFormData,
  RiskFreeRateFormData
} from '../schemas';

import type {
  CreateFxRateRequest,
  CreateRiskFreeRateRequest
} from '../../types';

/**
 * Transform FX Rate form data to API request
 * 
 * @param formData - Validated FX rate form data
 * @returns API request ready for submission
 */
export function transformFxRateForm(
  formData: FxRateFormData
): CreateFxRateRequest {
  return {
    date: formData.date,
    from_currency: formData.from_currency,
    to_currency: formData.to_currency,
    fx_rate: formData.fx_rate
  };
}

/**
 * Transform Risk-Free Rate form data to API request
 * 
 * @param formData - Validated risk-free rate form data
 * @returns API request ready for submission
 */
export function transformRiskFreeRateForm(
  formData: RiskFreeRateFormData
): CreateRiskFreeRateRequest {
  const request: CreateRiskFreeRateRequest = {
    date: formData.date,
    currency: formData.currency,
    rate: formData.rate
  };
  
  // Optional rate_type
  if (formData.rate_type) {
    request.rate_type = formData.rate_type;
  }
  
  // Optional source
  if (formData.source?.trim()) {
    request.source = formData.source.trim();
  }
  
  return request;
}

