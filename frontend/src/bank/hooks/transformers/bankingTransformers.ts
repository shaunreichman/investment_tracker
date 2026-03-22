/**
 * Banking Transformers
 * 
 * Transform banking form data to API request types.
 * Covers banks, bank accounts, and balances.
 */

import type {
  CreateBankFormData,
  CreateBankAccountFormData,
  BankAccountBalanceFormData
} from '../schemas';

import type {
  CreateBankRequest,
  CreateBankAccountRequest,
  CreateBankAccountBalanceRequest
} from '../../types';

/**
 * Transform Bank Creation form data to API request
 * 
 * @param formData - Validated bank creation form data
 * @returns API request ready for submission
 */
export function transformCreateBankForm(
  formData: CreateBankFormData
): CreateBankRequest {
  const request: CreateBankRequest = {
    name: formData.name.trim(),
    country: formData.country
  };
  
  // Optional SWIFT/BIC code
  if (formData.swift_bic?.trim()) {
    request.swift_bic = formData.swift_bic.trim().toUpperCase(); // SWIFT codes are uppercase
  }
  
  // Optional bank type
  if (formData.bank_type) {
    request.bank_type = formData.bank_type;
  }
  
  return request;
}

/**
 * Transform Bank Account Creation form data to API request
 * 
 * Note: bank_id is provided via URL path parameter, not in request body
 * 
 * @param formData - Validated bank account creation form data
 * @returns API request ready for submission
 */
export function transformCreateBankAccountForm(
  formData: CreateBankAccountFormData
): CreateBankAccountRequest {
  const request: CreateBankAccountRequest = {
    entity_id: formData.entity_id,
    account_name: formData.account_name.trim(),
    account_number: formData.account_number.trim(),
    currency: formData.currency
  };
  
  // Optional account type
  if (formData.account_type) {
    request.account_type = formData.account_type;
  }
  
  return request;
}

/**
 * Transform Bank Account Balance form data to API request
 * 
 * Note: bank_id and bank_account_id are provided via URL path parameters
 * 
 * @param formData - Validated balance form data
 * @returns API request ready for submission
 */
export function transformBankAccountBalanceForm(
  formData: BankAccountBalanceFormData
): CreateBankAccountBalanceRequest {
  return {
    currency: formData.currency,
    balance_statement: formData.balance_statement,
    date: formData.date
  };
}

