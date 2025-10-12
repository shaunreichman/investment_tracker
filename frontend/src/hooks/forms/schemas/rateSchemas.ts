/**
 * Rate Schemas
 * 
 * Zod validation schemas for rate-related forms.
 * Covers FX rates and risk-free rates.
 */

import { z } from 'zod';
import { dateString, positiveNumber, isLastDayOfMonth } from './commonSchemas';
import { Currency } from '@/types/enums/shared.enums';
import { RiskFreeRateType } from '@/types/enums/rates.enums';

/**
 * FX Rate Schema
 * 
 * Validates foreign exchange rate entries
 * Aligned with backend: /api/fx-rates POST endpoint
 * 
 * Backend constraints:
 * - Required fields: from_currency, to_currency, date, fx_rate
 * - fx_rate must be > 0 (validated via positiveNumber)
 * - date must be last day of month (validated via custom refinement)
 * - currencies must be different
 * - No source field supported by backend
 */
export const fxRateSchema = z.object({
  date: dateString,
  
  from_currency: z.nativeEnum(Currency, {
    errorMap: () => ({ message: 'Please select a valid currency' })
  }),
  
  to_currency: z.nativeEnum(Currency, {
    errorMap: () => ({ message: 'Please select a valid currency' })
  }),
  
  fx_rate: positiveNumber
}).refine(
  (data) => {
    // From and to currencies must be different
    return data.from_currency !== data.to_currency;
  },
  {
    message: 'From and to currencies must be different',
    path: ['to_currency']
  }
).refine(
  (data) => isLastDayOfMonth(data.date),
  {
    message: 'FX rate date must be the last day of the month',
    path: ['date']
  }
);

export type FxRateFormData = z.infer<typeof fxRateSchema>;

/**
 * Risk-Free Rate Schema
 * 
 * Validates risk-free rate entries
 * Aligned with backend: /api/risk-free-rates POST endpoint
 * 
 * Backend constraints:
 * - Required fields: currency, date, rate
 * - Optional fields: rate_type (defaults to GOVERNMENT_BOND), source (max 100 chars)
 * - Rate range: -100 to 10000 (allows negative rates)
 */
export const riskFreeRateSchema = z.object({
  date: dateString,
  
  currency: z.nativeEnum(Currency, {
    errorMap: () => ({ message: 'Please select a valid currency' })
  }),
  
  rate: z.number({
    message: 'Must be a valid number'
  })
    .min(-100, 'Rate must be between -100 and 10000')
    .max(10000, 'Rate must be between -100 and 10000')
    .finite('Must be a valid number'),
  
  rate_type: z.nativeEnum(RiskFreeRateType, {
    errorMap: () => ({ message: 'Please select a valid rate type' })
  }).optional(),
  
  source: z.string()
    .max(100, 'Source must be less than 100 characters')
    .optional()
});

export type RiskFreeRateFormData = z.infer<typeof riskFreeRateSchema>;

