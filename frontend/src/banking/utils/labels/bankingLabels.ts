/**
 * Banking labels for UI display.
 * 
 * Maps banking-related enum values to user-friendly strings.
 */

import {
  BankType,
  BankStatus,
  BankAccountType,
  BankAccountStatus,
} from '@/bank/types';

/**
 * Bank type labels for UI display.
 * 
 * Maps BankType enum values to user-friendly strings.
 */
export const BANK_TYPE_LABELS: Record<BankType, string> = {
  [BankType.COMMERCIAL]: 'Commercial Bank',
  [BankType.INVESTMENT]: 'Investment Bank',
  [BankType.CENTRAL]: 'Central Bank',
  [BankType.COOPERATIVE]: 'Cooperative Bank',
  [BankType.DIGITAL]: 'Digital Bank',
};

/**
 * Bank status labels for UI display.
 * 
 * Maps BankStatus enum values to user-friendly strings.
 */
export const BANK_STATUS_LABELS: Record<BankStatus, string> = {
  [BankStatus.ACTIVE]: 'Active',
  [BankStatus.INACTIVE]: 'Inactive',
  [BankStatus.CLOSED]: 'Closed',
};

/**
 * Bank account type labels for UI display.
 * 
 * Maps BankAccountType enum values to user-friendly strings.
 */
export const BANK_ACCOUNT_TYPE_LABELS: Record<BankAccountType, string> = {
  [BankAccountType.CHECKING]: 'Checking Account',
  [BankAccountType.SAVINGS]: 'Savings Account',
  [BankAccountType.INVESTMENT]: 'Investment Account',
  [BankAccountType.BUSINESS]: 'Business Account',
  [BankAccountType.TRUST]: 'Trust Account',
  [BankAccountType.JOINT]: 'Joint Account',
};

/**
 * Bank account status labels for UI display.
 * 
 * Maps BankAccountStatus enum values to user-friendly strings.
 */
export const BANK_ACCOUNT_STATUS_LABELS: Record<BankAccountStatus, string> = {
  [BankAccountStatus.ACTIVE]: 'Active',
  [BankAccountStatus.INACTIVE]: 'Inactive',
  [BankAccountStatus.CLOSED]: 'Closed',
  [BankAccountStatus.SUSPENDED]: 'Suspended',
  [BankAccountStatus.OVERDRAFT]: 'Overdraft',
};

/**
 * Get bank type label with fallback.
 * 
 * @param bankType - The bank type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankTypeLabel(bankType: BankType): string {
  return BANK_TYPE_LABELS[bankType] || bankType;
}

/**
 * Get bank status label with fallback.
 * 
 * @param status - The bank status enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankStatusLabel(status: BankStatus): string {
  return BANK_STATUS_LABELS[status] || status;
}

/**
 * Get bank account type label with fallback.
 * 
 * @param accountType - The bank account type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankAccountTypeLabel(accountType: BankAccountType): string {
  return BANK_ACCOUNT_TYPE_LABELS[accountType] || accountType;
}

/**
 * Get bank account status label with fallback.
 * 
 * @param status - The bank account status enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankAccountStatusLabel(status: BankAccountStatus): string {
  return BANK_ACCOUNT_STATUS_LABELS[status] || status;
}

