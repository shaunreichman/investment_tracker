/**
 * Banking Schemas
 * 
 * Zod validation schemas for banking-related forms.
 * Covers banks, bank accounts, and balances.
 * Aligned with backend: /api/banks, /api/banks/:id/bank-accounts, and balance endpoints
 */

import { z } from 'zod/v3';
import { nonEmptyString, dateString, nonNegativeNumber, isLastDayOfMonth } from '@/shared/hooks/schemas';
import { Country, Currency } from '@/shared/types';
import { BankType, BankAccountType } from '../../types';

/**
 * Bank Creation Schema
 * 
 * Validates new bank creation
 * Aligned with backend: /api/banks POST endpoint
 * 
 * Required: name, country
 */
export const createBankSchema = z.object({
  name: nonEmptyString
    .min(2, 'Bank name must be at least 2 characters')
    .max(255, 'Bank name must be less than 255 characters'),
  
  country: z.nativeEnum(Country, {
    message: 'Please select a valid country'
  }),
  
  swift_bic: z.string()
    .max(11, 'SWIFT/BIC code must be 11 characters or less')
    .regex(/^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/, 'Invalid SWIFT/BIC code format')
    .optional(),
  
  bank_type: z.nativeEnum(BankType, {
    message: 'Please select a valid bank type'
  }).optional()
});

export type CreateBankFormData = z.infer<typeof createBankSchema>;

/**
 * Bank Account Creation Schema
 * 
 * Validates new bank account creation
 * Aligned with backend: /api/banks/:bank_id/bank-accounts POST endpoint
 * 
 * Required: entity_id, account_name, account_number, currency
 * Note: bank_id is provided via path parameter, not in body
 */
export const createBankAccountSchema = z.object({
  entity_id: z.number().int().positive('Account holder is required'),
  
  account_name: nonEmptyString
    .min(2, 'Account name must be at least 2 characters')
    .max(255, 'Account name must be less than 255 characters'),
  
  account_number: nonEmptyString
    .min(1, 'Account number is required')
    .max(64, 'Account number must be less than 64 characters'),
  
  currency: z.nativeEnum(Currency, {
    message: 'Please select a valid currency'
  }),
  
  account_type: z.nativeEnum(BankAccountType, {
    message: 'Please select a valid account type'
  }).optional()
});

export type CreateBankAccountFormData = z.infer<typeof createBankAccountSchema>;

/**
 * Bank Account Balance Schema
 * 
 * Validates balance updates for bank accounts
 * Aligned with backend: /api/banks/:bank_id/bank-accounts/:bank_account_id/bank-account-balances POST endpoint
 * 
 * Required: currency, balance_statement, date
 * Note: bank_id and bank_account_id are provided via path parameters
 * 
 * Backend constraint: date must be the last day of the month (per backend model)
 */
export const bankAccountBalanceSchema = z.object({
  currency: z.nativeEnum(Currency, {
    message: 'Please select a valid currency'
  }),
  
  balance_statement: nonNegativeNumber,
  
  date: dateString
}).refine(
  (data) => isLastDayOfMonth(data.date),
  {
    message: 'Balance date must be the last day of the month',
    path: ['date']
  }
);

export type BankAccountBalanceFormData = z.infer<typeof bankAccountBalanceSchema>;

