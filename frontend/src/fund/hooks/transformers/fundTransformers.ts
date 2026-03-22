/**
 * Fund Transformers
 * 
 * Transform validated form data to API request types.
 * Handles fund creation and all fund event types.
 * Includes filtering empty optional fields, trimming strings, and type conversions.
 */

import type {
  CreateFundFormData,
  NavUpdateFormData,
  CapitalCallFormData,
  ReturnOfCapitalFormData,
  DistributionFormData,
  UnitPurchaseFormData,
  UnitSaleFormData,
  FundEventCashFlowFormData,
  FundTaxStatementFormData
} from '../schemas';

import type {
  CreateFundRequest,
  CreateNavUpdateRequest,
  CreateCapitalCallRequest,
  CreateReturnOfCapitalRequest,
  CreateDistributionRequest,
  CreateUnitPurchaseRequest,
  CreateUnitSaleRequest,
  CreateFundEventCashFlowRequest,
  CreateFundTaxStatementRequest
} from '@/fund/types';


// ======================================================================================
// FUNDS
// ======================================================================================

/**
 * Transform Fund Creation form data to API request
 * 
 * Handles:
 * - Filtering empty optional fields
 * - Trimming string values
 * - Ensuring all required fields are present
 * 
 * @param formData - Validated fund creation form data
 * @returns API request ready for submission
 */
export function transformCreateFundForm(
  formData: CreateFundFormData
): CreateFundRequest {
  const request: CreateFundRequest = {
    name: formData.name.trim(),
    entity_id: formData.entity_id,
    company_id: formData.company_id,
    tracking_type: formData.tracking_type,
    tax_jurisdiction: formData.tax_jurisdiction,
    currency: formData.currency
  };
  
  // Optional fund investment type
  if (formData.fund_investment_type) {
    request.fund_investment_type = formData.fund_investment_type;
  }
  
  // Optional description
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  // Optional expected IRR (0 is valid - represents break-even)
  if (formData.expected_irr !== undefined) {
    request.expected_irr = formData.expected_irr;
  }
  
  // Optional expected duration (0 is valid)
  if (formData.expected_duration_months !== undefined) {
    request.expected_duration_months = formData.expected_duration_months;
  }
  
  // Optional commitment amount (must be positive if provided)
  if (formData.commitment_amount !== undefined) {
    request.commitment_amount = formData.commitment_amount;
  }
  
  return request;
}


// ======================================================================================
// FUND EVENTS
// ======================================================================================

/**
 * Transform NAV Update form data to API request
 * 
 * Filters empty optional fields and trims strings.
 * 
 * @param formData - Validated NAV update form data
 * @returns API request ready for submission
 */
export function transformNavUpdateForm(
  formData: NavUpdateFormData
): CreateNavUpdateRequest {
  const request: CreateNavUpdateRequest = {
    event_date: formData.event_date,
    nav_per_share: formData.nav_per_share
  };
  
  // Include optional fields only if they have non-empty values
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  if (formData.reference_number?.trim()) {
    request.reference_number = formData.reference_number.trim();
  }
  
  return request;
}

/**
 * Transform Capital Call form data to API request
 * 
 * @param formData - Validated capital call form data
 * @returns API request ready for submission
 */
export function transformCapitalCallForm(
  formData: CapitalCallFormData
): CreateCapitalCallRequest {
  const request: CreateCapitalCallRequest = {
    event_date: formData.event_date,
    amount: formData.amount
  };
  
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  if (formData.reference_number?.trim()) {
    request.reference_number = formData.reference_number.trim();
  }
  
  return request;
}

/**
 * Transform Return of Capital form data to API request
 * 
 * @param formData - Validated return of capital form data
 * @returns API request ready for submission
 */
export function transformReturnOfCapitalForm(
  formData: ReturnOfCapitalFormData
): CreateReturnOfCapitalRequest {
  const request: CreateReturnOfCapitalRequest = {
    event_date: formData.event_date,
    amount: formData.amount
  };
  
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  if (formData.reference_number?.trim()) {
    request.reference_number = formData.reference_number.trim();
  }
  
  return request;
}

/**
 * Transform Distribution form data to API request
 * 
 * Handles complex conditional logic for withholding tax distributions:
 * - Simple distributions: amount field
 * - Withholding tax distributions: gross/net amounts + tax amount/rate
 * 
 * @param formData - Validated distribution form data
 * @returns API request ready for submission
 */
export function transformDistributionForm(
  formData: DistributionFormData
): CreateDistributionRequest {
  const request: CreateDistributionRequest = {
    event_date: formData.event_date,
    distribution_type: formData.distribution_type
  };
  
  // Handle withholding tax vs simple distribution
  if (formData.has_withholding_tax) {
    request.has_withholding_tax = true;
    
    // Gross or net amount (one is required by schema)
    if (formData.gross_amount !== undefined) {
      request.gross_amount = formData.gross_amount;
    }
    
    if (formData.net_amount !== undefined) {
      request.net_amount = formData.net_amount;
    }
    
    // Tax amount or rate (one is required by schema)
    if (formData.withholding_tax_amount !== undefined) {
      request.withholding_tax_amount = formData.withholding_tax_amount;
    }
    
    if (formData.withholding_tax_rate !== undefined) {
      request.withholding_tax_rate = formData.withholding_tax_rate;
    }
  } else {
    // Simple distribution - just amount
    if (formData.amount !== undefined) {
      request.amount = formData.amount;
    }
  }
  
  // Optional fields
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  if (formData.reference_number?.trim()) {
    request.reference_number = formData.reference_number.trim();
  }
  
  return request;
}

/**
 * Transform Unit Purchase form data to API request
 * 
 * @param formData - Validated unit purchase form data
 * @returns API request ready for submission
 */
export function transformUnitPurchaseForm(
  formData: UnitPurchaseFormData
): CreateUnitPurchaseRequest {
  const request: CreateUnitPurchaseRequest = {
    event_date: formData.event_date,
    units_purchased: formData.units_purchased,
    unit_price: formData.unit_price
  };
  
  // Optional brokerage fee (0 is valid - represents free trades)
  if (formData.brokerage_fee !== undefined) {
    request.brokerage_fee = formData.brokerage_fee;
  }
  
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  if (formData.reference_number?.trim()) {
    request.reference_number = formData.reference_number.trim();
  }
  
  return request;
}

/**
 * Transform Unit Sale form data to API request
 * 
 * @param formData - Validated unit sale form data
 * @returns API request ready for submission
 */
export function transformUnitSaleForm(
  formData: UnitSaleFormData
): CreateUnitSaleRequest {
  const request: CreateUnitSaleRequest = {
    event_date: formData.event_date,
    units_sold: formData.units_sold,
    unit_price: formData.unit_price
  };
  
  // Optional brokerage fee (0 is valid - represents free trades)
  if (formData.brokerage_fee !== undefined) {
    request.brokerage_fee = formData.brokerage_fee;
  }
  
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  if (formData.reference_number?.trim()) {
    request.reference_number = formData.reference_number.trim();
  }
  
  return request;
}


// ======================================================================================
// FUND EVENT CASH FLOW
// ======================================================================================

/**
 * Transform Fund Event Cash Flow form data to API request
 * 
 * Filters empty optional fields and trims strings.
 * 
 * @param formData - Validated fund event cash flow form data
 * @returns API request ready for submission
 */
export function transformFundEventCashFlowForm(
  formData: FundEventCashFlowFormData
): CreateFundEventCashFlowRequest {
  const request: CreateFundEventCashFlowRequest = {
    bank_account_id: formData.bank_account_id,
    direction: formData.direction,
    transfer_date: formData.transfer_date,
    currency: formData.currency,
    amount: formData.amount
  };
  
  // Include optional fields only if they have non-empty values
  if (formData.reference?.trim()) {
    request.reference = formData.reference.trim();
  }
  
  if (formData.description?.trim()) {
    request.description = formData.description.trim();
  }
  
  return request;
}


// ======================================================================================
// FUND TAX STATEMENT
// ======================================================================================

/**
 * Transform Fund Tax Statement form data to API request
 * 
 * Handles comprehensive tax statement data with many optional fields.
 * Filters empty optional fields and trims strings.
 * 
 * @param formData - Validated fund tax statement form data
 * @returns API request ready for submission
 */
export function transformFundTaxStatementForm(
  formData: FundTaxStatementFormData
): CreateFundTaxStatementRequest {
  const request: CreateFundTaxStatementRequest = {
    entity_id: formData.entity_id,
    financial_year: formData.financial_year
  };
  
  // Optional date fields
  if (formData.tax_payment_date) {
    request.tax_payment_date = formData.tax_payment_date;
  }
  
  if (formData.statement_date) {
    request.statement_date = formData.statement_date;
  }
  
  // Interest fields (0 is valid for all numeric fields)
  if (formData.interest_income_tax_rate !== undefined) {
    request.interest_income_tax_rate = formData.interest_income_tax_rate;
  }
  
  if (formData.interest_received_in_cash !== undefined) {
    request.interest_received_in_cash = formData.interest_received_in_cash;
  }
  
  if (formData.interest_receivable_this_fy !== undefined) {
    request.interest_receivable_this_fy = formData.interest_receivable_this_fy;
  }
  
  if (formData.interest_receivable_prev_fy !== undefined) {
    request.interest_receivable_prev_fy = formData.interest_receivable_prev_fy;
  }
  
  if (formData.interest_non_resident_withholding_tax_from_statement !== undefined) {
    request.interest_non_resident_withholding_tax_from_statement = formData.interest_non_resident_withholding_tax_from_statement;
  }
  
  // Dividend fields
  if (formData.dividend_franked_income_amount !== undefined) {
    request.dividend_franked_income_amount = formData.dividend_franked_income_amount;
  }
  
  if (formData.dividend_unfranked_income_amount !== undefined) {
    request.dividend_unfranked_income_amount = formData.dividend_unfranked_income_amount;
  }
  
  if (formData.dividend_franked_income_tax_rate !== undefined) {
    request.dividend_franked_income_tax_rate = formData.dividend_franked_income_tax_rate;
  }
  
  if (formData.dividend_unfranked_income_tax_rate !== undefined) {
    request.dividend_unfranked_income_tax_rate = formData.dividend_unfranked_income_tax_rate;
  }
  
  // Capital gain fields
  if (formData.capital_gain_income_amount !== undefined) {
    request.capital_gain_income_amount = formData.capital_gain_income_amount;
  }
  
  if (formData.capital_gain_income_tax_rate !== undefined) {
    request.capital_gain_income_tax_rate = formData.capital_gain_income_tax_rate;
  }
  
  if (formData.capital_gain_discount_applicable_flag !== undefined) {
    request.capital_gain_discount_applicable_flag = formData.capital_gain_discount_applicable_flag;
  }
  
  // EOFY debt interest deduction
  if (formData.eofy_debt_interest_deduction_rate !== undefined) {
    request.eofy_debt_interest_deduction_rate = formData.eofy_debt_interest_deduction_rate;
  }
  
  // Additional information (trim strings)
  if (formData.accountant?.trim()) {
    request.accountant = formData.accountant.trim();
  }
  
  if (formData.notes?.trim()) {
    request.notes = formData.notes.trim();
  }
  
  return request;
}

