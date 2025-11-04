/**
 * Fund Schemas
 * 
 * Zod validation schemas for fund-related forms.
 * Covers fund creation and all fund event types (NAV updates, distributions, etc.).
 * Aligned with backend: /api/funds/* endpoints
 */

import { z } from 'zod';
import { 
  nonEmptyString,
  positiveNumber,
  dateString,
  nonNegativeNumber,
  percentage
} from '@/shared/hooks/schemas';
import { 
  FundTrackingType, 
  FundInvestmentType, 
  DistributionType, 
  CashFlowDirection 
} from '@/fund/types';
import { Country, Currency } from '@/shared/types';


// ======================================================================================
// FUNDS
// ======================================================================================

/**
 * Fund Creation Schema
 * 
 * Validates new fund creation with all required fields.
 * Aligned with backend: /api/funds POST endpoint
 * 
 * Required: name, entity_id, company_id, tracking_type, tax_jurisdiction, currency
 */
export const createFundSchema = z.object({
  name: nonEmptyString
    .min(2, 'Fund name must be at least 2 characters')
    .max(255, 'Fund name must be less than 255 characters'),
  
  entity_id: z.number().int().positive('Entity is required'),
  
  company_id: z.number().int().positive('Company is required'),
  
  tracking_type: z.nativeEnum(FundTrackingType, {
    errorMap: () => ({ message: 'Please select a valid tracking type' })
  }),
  
  tax_jurisdiction: z.nativeEnum(Country, {
    errorMap: () => ({ message: 'Please select a valid tax jurisdiction' })
  }),
  
  currency: z.nativeEnum(Currency, {
    errorMap: () => ({ message: 'Please select a valid currency' })
  }),
  
  fund_investment_type: z.nativeEnum(FundInvestmentType, {
    errorMap: () => ({ message: 'Please select a valid fund investment type' })
  }).optional(),
  
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  
  expected_irr: z.number()
    .min(0, 'Expected IRR must be between 0 and 100')
    .max(100, 'Expected IRR must be between 0 and 100')
    .optional(),
  
  expected_duration_months: z.number()
    .int('Expected duration must be a whole number')
    .min(0, 'Expected duration must be at least 0 months')
    .max(1200, 'Expected duration cannot exceed 1200 months')
    .optional(),
  
  commitment_amount: positiveNumber.optional()
});

export type CreateFundFormData = z.infer<typeof createFundSchema>;


// ======================================================================================
// FUND EVENTS
// ======================================================================================

/**
 * Capital Call Event Schema
 * 
 * Validates capital call events
 * Aligned with backend: /api/funds/:id/fund-events/capital-call POST endpoint
 * 
 * Required: event_date, amount
 */
export const capitalCallSchema = z.object({
  event_date: dateString,
  amount: positiveNumber,
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  reference_number: z.string().max(255, 'Reference number must be less than 255 characters').optional()
});

export type CapitalCallFormData = z.infer<typeof capitalCallSchema>;

/**
 * Return of Capital Event Schema
 * 
 * Validates return of capital events
 * Aligned with backend: /api/funds/:id/fund-events/return-of-capital POST endpoint
 * 
 * Required: event_date, amount
 */
export const returnOfCapitalSchema = z.object({
  event_date: dateString,
  amount: positiveNumber,
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  reference_number: z.string().max(255, 'Reference number must be less than 255 characters').optional()
});

export type ReturnOfCapitalFormData = z.infer<typeof returnOfCapitalSchema>;

/**
 * NAV Update Event Schema
 * 
 * Validates NAV update events with required date and NAV per share.
 * Aligned with backend: /api/funds/:id/fund-events/nav-update POST endpoint
 * 
 * Required: event_date, nav_per_share
 */
export const navUpdateSchema = z.object({
  event_date: dateString,
  nav_per_share: positiveNumber,
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  reference_number: z.string().max(255, 'Reference number must be less than 255 characters').optional()
});

export type NavUpdateFormData = z.infer<typeof navUpdateSchema>;

/**
 * Distribution Event Schema
 * 
 * Validates distribution events with optional withholding tax
 * Aligned with backend: /api/funds/:id/fund-events/distribution POST endpoint
 * 
 * Required: event_date, distribution_type
 * 
 * For simple distributions: amount is required
 * For withholding tax distributions: has_withholding_tax=true, and either:
 *   - gross_amount OR net_amount (one required)
 *   - withholding_tax_amount OR withholding_tax_rate (one required)
 */
export const distributionSchema = z.object({
  event_date: dateString,
  
  distribution_type: z.nativeEnum(DistributionType, {
    errorMap: () => ({ message: 'Please select a valid distribution type' })
  }),
  
  // Simple distribution amount (used when has_withholding_tax is false)
  amount: positiveNumber.optional(),
  
  // Withholding tax flag
  has_withholding_tax: z.boolean().optional(),
  
  // Withholding tax amounts (used when has_withholding_tax is true)
  gross_amount: positiveNumber.optional(),
  net_amount: positiveNumber.optional(),
  withholding_tax_amount: positiveNumber.optional(),
  withholding_tax_rate: percentage.optional(),
  
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  reference_number: z.string().max(255, 'Reference number must be less than 255 characters').optional()
}).refine(
  (data) => {
    // If has_withholding_tax is false or undefined, amount is required
    if (!data.has_withholding_tax) {
      return data.amount !== undefined;
    }
    // If has_withholding_tax is true, exactly one of gross_amount or net_amount is required
    const hasGross = data.gross_amount !== undefined;
    const hasNet = data.net_amount !== undefined;
    return hasGross !== hasNet; // XOR: true only if exactly one is set
  },
  {
    message: 'Must provide exactly one of: amount (for simple distribution) OR gross_amount OR net_amount (not both)',
    path: ['amount']
  }
).refine(
  (data) => {
    // If has_withholding_tax is true, exactly one of tax amount or tax rate is required
    if (data.has_withholding_tax) {
      const hasTaxAmount = data.withholding_tax_amount !== undefined;
      const hasTaxRate = data.withholding_tax_rate !== undefined;
      return hasTaxAmount !== hasTaxRate; // XOR: true only if exactly one is set
    }
    return true;
  },
  {
    message: 'Must provide exactly one of: withholding_tax_amount OR withholding_tax_rate (not both)',
    path: ['withholding_tax_amount']
  }
);

export type DistributionFormData = z.infer<typeof distributionSchema>;

/**
 * Unit Purchase Event Schema
 * 
 * Validates unit purchase transactions
 * Aligned with backend: /api/funds/:id/fund-events/unit-purchase POST endpoint
 * 
 * Required: event_date, units_purchased, unit_price
 */
export const unitPurchaseSchema = z.object({
  event_date: dateString,
  units_purchased: positiveNumber,
  unit_price: positiveNumber,
  brokerage_fee: nonNegativeNumber.optional(),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  reference_number: z.string().max(255, 'Reference number must be less than 255 characters').optional()
});

export type UnitPurchaseFormData = z.infer<typeof unitPurchaseSchema>;

/**
 * Unit Sale Event Schema
 * 
 * Validates unit sale transactions
 * Aligned with backend: /api/funds/:id/fund-events/unit-sale POST endpoint
 * 
 * Required: event_date, units_sold, unit_price
 */
export const unitSaleSchema = z.object({
  event_date: dateString,
  units_sold: positiveNumber,
  unit_price: positiveNumber,
  brokerage_fee: nonNegativeNumber.optional(),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  reference_number: z.string().max(255, 'Reference number must be less than 255 characters').optional()
});

export type UnitSaleFormData = z.infer<typeof unitSaleSchema>;


// ======================================================================================
// FUND EVENT CASH FLOW
// ======================================================================================

/**
 * Fund Event Cash Flow Schema
 * 
 * Validates cash flow records linking fund events to bank accounts.
 * Aligned with backend: /api/funds/:id/fund-events/:event_id/fund-event-cash-flows POST endpoint
 * 
 * Required: bank_account_id, direction, transfer_date, currency, amount
 */
export const fundEventCashFlowSchema = z.object({
  bank_account_id: z.number().int().positive('Bank account is required'),
  
  direction: z.nativeEnum(CashFlowDirection, {
    errorMap: () => ({ message: 'Please select a valid cash flow direction' })
  }),
  
  transfer_date: dateString,
  
  currency: z.nativeEnum(Currency, {
    errorMap: () => ({ message: 'Please select a valid currency' })
  }),
  
  amount: positiveNumber,
  
  reference: z.string().max(255, 'Reference must be less than 255 characters').optional(),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional()
});

export type FundEventCashFlowFormData = z.infer<typeof fundEventCashFlowSchema>;


// ======================================================================================
// FUND TAX STATEMENT
// ======================================================================================

/**
 * Fund Tax Statement Schema
 * 
 * Validates tax statement records for funds with comprehensive tax information.
 * Aligned with backend: /api/funds/:id/fund-tax-statements POST endpoint
 * 
 * Required: entity_id, financial_year
 * 
 * Financial year must be a 4-digit year string (e.g., "2023") between 1900-2100.
 * All tax rates are percentages (0-100).
 * All amounts are non-negative (0 or greater).
 */
export const fundTaxStatementSchema = z.object({
  // Required fields
  entity_id: z.number().int().positive('Entity is required'),
  
  financial_year: z.string()
    .length(4, 'Financial year must be exactly 4 digits')
    .regex(/^\d{4}$/, 'Financial year must be a valid year (e.g., 2023)')
    .refine(
      (val) => {
        const year = parseInt(val, 10);
        return year >= 1900 && year <= 2100;
      },
      { message: 'Financial year must be between 1900 and 2100' }
    ),
  
  // Optional date fields
  tax_payment_date: dateString.optional(),
  statement_date: dateString.optional(),
  
  // Interest fields (rates 0-100, amounts non-negative)
  interest_income_tax_rate: percentage.optional(),
  interest_received_in_cash: nonNegativeNumber.optional(),
  interest_receivable_this_fy: nonNegativeNumber.optional(),
  interest_receivable_prev_fy: nonNegativeNumber.optional(),
  interest_non_resident_withholding_tax_from_statement: nonNegativeNumber.optional(),
  
  // Dividend fields (rates 0-100, amounts non-negative)
  dividend_franked_income_amount: nonNegativeNumber.optional(),
  dividend_unfranked_income_amount: nonNegativeNumber.optional(),
  dividend_franked_income_tax_rate: percentage.optional(),
  dividend_unfranked_income_tax_rate: percentage.optional(),
  
  // Capital gain fields (rates 0-100, amounts non-negative)
  capital_gain_income_amount: nonNegativeNumber.optional(),
  capital_gain_income_tax_rate: percentage.optional(),
  capital_gain_discount_applicable_flag: z.boolean().optional(),
  
  // EOFY debt interest deduction
  eofy_debt_interest_deduction_rate: percentage.optional(),
  
  // Additional information
  accountant: z.string().max(255, 'Accountant name must be less than 255 characters').optional(),
  notes: z.string().max(1000, 'Notes must be less than 1000 characters').optional()
});

export type FundTaxStatementFormData = z.infer<typeof fundTaxStatementSchema>;

