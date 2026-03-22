/**
 * Shared Reusable Schemas
 * 
 * Zod schemas for common field types used across multiple forms.
 * These can be composed into domain-specific schemas.
 * 
 * @example
 * ```typescript
 * const fundSchema = z.object({
 *   managementFee: positivePercentage,
 *   email: emailAddress.optional()
 * });
 * ```
 */

import { z } from 'zod/v3';

/**
 * Email address validation
 * Standard email format with helpful error message
 */
export const emailAddress = z
  .string()
  .email('Please enter a valid email address')
  .max(255, 'Email address must be less than 255 characters');

/**
 * Non-empty string validation
 * Useful for required text fields
 */
export const nonEmptyString = z
  .string()
  .min(1, 'This field is required')
  .trim();

/**
 * Positive number validation
 * For values that must be greater than zero (amounts, prices, etc.)
 * Max: 9,999,999,999 (aligned with backend validation)
 */
export const positiveNumber = z
  .number({
    message: 'Must be a valid number'
  })
  .positive('Must be greater than 0')
  .max(9999999999, 'Value must be less than 10 billion')
  .finite('Must be a valid number');

/**
 * Non-negative number validation
 * For values that can be zero or positive (quantities, counts, etc.)
 * Max: 9,999,999,999 (aligned with backend validation)
 */
export const nonNegativeNumber = z
  .number({
    message: 'Must be a valid number'
  })
  .min(0, 'Must be 0 or greater')
  .max(9999999999, 'Value must be less than 10 billion')
  .finite('Must be a valid number');

/**
 * Percentage validation (0-100)
 * For percentage fields like management fees, tax rates
 */
export const percentage = z
  .number({
    message: 'Must be a valid number'
  })
  .min(0, 'Percentage must be between 0 and 100')
  .max(100, 'Percentage must be between 0 and 100')
  .finite('Must be a valid number');

/**
 * Positive percentage validation (0-100, excluding 0)
 * For percentages that must be greater than zero
 */
export const positivePercentage = z
  .number({
    message: 'Must be a valid number'
  })
  .positive('Percentage must be greater than 0')
  .max(100, 'Percentage must be 100 or less')
  .finite('Must be a valid number');

/**
 * Currency amount validation
 * For monetary values (supports decimals, must be positive)
 * Max: 9,999,999,999 (aligned with backend validation)
 */
export const currencyAmount = z
  .number({
    message: 'Must be a valid amount'
  })
  .positive('Amount must be greater than 0')
  .max(9999999999, 'Amount must be less than 10 billion')
  .finite('Must be a valid amount');

/**
 * Date string validation (ISO format: YYYY-MM-DD)
 * For date input fields that provide string values
 */
export const dateString = z
  .string()
  .min(1, 'Date is required')
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Invalid date format');

/**
 * Date validation
 * For actual Date objects
 */
export const dateObject = z
  .date({
    message: 'Invalid date'
  });

/**
 * URL validation
 * For website/link fields
 */
export const urlString = z
  .string()
  .url('Please enter a valid URL')
  .max(255, 'URL must be less than 255 characters');

/**
 * Phone number validation (international)
 * Allows common phone number formats from any country
 * Supports country codes, spaces, dashes, dots, slashes, and parentheses
 * Max 50 characters to match backend constraint
 * 
 * Examples: +1-555-123-4567, +44 20 7123 4567, (02) 1234 5678, +972-3-123-4567
 */
export const phoneNumber = z
  .string()
  .min(1, 'Phone number is required')
  .max(50, 'Phone number must be less than 50 characters')
  .regex(/^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$/, 'Invalid phone number format');

/**
 * Currency code validation (ISO 4217)
 * For currency selection fields
 * Aligned with backend supported currencies
 */
export const currencyCode = z.enum([
  'AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF', 'CNY', 'KRW'
]);

/**
 * Helper: Create date range schema with start/end validation
 * Ensures end date is after start date
 * 
 * @example
 * ```typescript
 * const schema = z.object({
 *   startDate: dateString,
 *   endDate: dateString
 * }).refine((data) => {
 *   const start = new Date(data.startDate);
 *   const end = new Date(data.endDate);
 *   return end >= start;
 * }, {
 *   message: 'End date must be on or after start date',
 *   path: ['endDate']
 * });
 * ```
 */
export function validateDateRange(
  startDate: string,
  endDate: string
): boolean {
  if (!startDate || !endDate) return true;
  const start = new Date(startDate);
  const end = new Date(endDate);
  return end >= start;
}

/**
 * Helper: Create conditional required field
 * Field is required only when condition is met
 * 
 * @example
 * ```typescript
 * const schema = z.object({
 *   type: z.enum(['individual', 'company']),
 *   companyName: z.string().optional()
 * }).refine(
 *   (data) => conditionalRequired(data.type === 'company', data.companyName),
 *   { message: 'Company name is required', path: ['companyName'] }
 * );
 * ```
 */
export function conditionalRequired<T>(condition: boolean, value: T | undefined): boolean {
  if (condition) {
    return value !== undefined && value !== null && value !== '';
  }
  return true;
}

/**
 * Helper: Validate that a date is the last day of the month
 * Matches backend validation for FX rates
 * 
 * @param dateStr - Date string in YYYY-MM-DD format
 * @returns true if the date is the last day of its month
 * 
 * @example
 * ```typescript
 * isLastDayOfMonth('2024-01-31') // true
 * isLastDayOfMonth('2024-01-30') // false
 * isLastDayOfMonth('2024-02-29') // true (leap year)
 * isLastDayOfMonth('2024-02-28') // false (leap year)
 * ```
 */
export function isLastDayOfMonth(dateStr: string): boolean {
  if (!dateStr) return false;
  const date = new Date(dateStr);
  // Create a new date for the next day
  const nextDay = new Date(date);
  nextDay.setDate(date.getDate() + 1);
  // If next day is the 1st, we were on the last day of the month
  return nextDay.getDate() === 1;
}

